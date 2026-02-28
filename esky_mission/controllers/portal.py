from collections import OrderedDict
import werkzeug

import base64
from odoo import http, _
from odoo.http import request
from odoo import models, registry, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime

from odoo.osv.expression import OR
import requests
import logging
logger = logging.getLogger(__name__)



class CustomerPortal(CustomerPortal):
    _items_per_page = 10

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.employee_id
        Calendarmission = request.env['mission.mission'].sudo()
        if request.env.user._is_admin() or request.env.user.has_group('esky_mission.group_mission_hr_manager'):
            domain = []
        elif request.env.user.has_group('esky_mission.group_mission_manager'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]
        custom_mission_count = Calendarmission.search_count(domain)
        values.update({'custom_mission_count': custom_mission_count, })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.employee_id
        if request.env.user._is_admin() or request.env.user.has_group('esky_mission.group_mission_hr_manager'):
            domain = []
        elif request.env.user.has_group('esky_mission.group_mission_manager'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]
        if 'custom_mission_count' in counters:
            values['custom_mission_count'] = request.env['mission.mission'].sudo().search_count(domain)
        return values

    def _mission_get_page_view_values(self, custom_mission_request, access_token, **kwargs):
        values = {'page_name': 'custom_mission_page_probc', 'custom_mission_request': custom_mission_request, }

        return self._get_page_view_values(custom_mission_request, access_token, values, 'my_mission_history', False,
                                          **kwargs)

    def _get_mission_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('name', 'all'):
            search_domain = OR([search_domain, [('name', 'ilike', search)]])
        if search_in in ('customer_id', 'all'):
            search_domain = OR([search_domain, [('customer_id', 'ilike', search)]])
        if search_in in ('state', 'all'):
            search_domain = OR([search_domain, [('state', 'ilike', search)]])
        if search_in in ('options', 'all'):
            search_domain = OR([search_domain, [('options', 'ilike', search)]])
        return search_domain

    @http.route(['/my/mission', '/my/mission/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_custom_mission(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                 search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.employee_id
        mission_obj = http.request.env['mission.mission']

        if request.env.user._is_admin() or request.env.user.has_group('esky_mission.group_mission_hr_manager'):
            domain = []
        elif request.env.user.has_group('esky_mission.group_mission_manager'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]

        custom_mission_count = mission_obj.sudo().search_count(domain)

        # pager
        pager = portal_pager(url="/my/mission", total=custom_mission_count, page=page,
            step=self._items_per_page)
        searchbar_sortings = {
            'date': {'label': _('Date Ascending'), 'order': 'date', 'sequence': 1}, 
            'date desc': {'label': _('Date Descending'), 'order': 'date desc', 'sequence': 2},
            'options': {'label': _('Options'), 'order': 'options', 'sequence': 3},
            'state': {'label': _('Status'), 'order': 'state', 'sequence': 4},
            'customer_id': {'label': _('Customers'), 'order': 'customer_id', 'sequence': 5}
        }
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'name': {'input': 'name', 'label': _('Search in Mission')},
            'options': {'input': 'options', 'label': _('Search in Options')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'customer_id': {'input': 'customer_id', 'label': _('Search in Customers')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date desc'
        order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            domain += self._get_mission_search_domain(search_in, search)

        # content according to pager and archive selected
        missions = mission_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({'missions': missions, 'page_name': 'custom_mission_page_probc', 'pager': pager,
            'default_url': '/my/mission', 'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs, 'search_in': search_in, 'sortby': sortby, })
        return request.render("esky_mission.portal_my_mission_custom", values)

    @http.route(['/my/mission/<int:mission_id>'], type='http', auth="user", website=True)
    def custom_portal_my_mission(self, mission_id, access_token=None, **kw):
        try:
            if request.env.user.share:
                current_employee = request.env.user.employee_id
                current_mission = request.env['mission.mission'].sudo().browse(mission_id)
                if current_mission.employee_id.id != current_employee.id:
                    return request.redirect('/my')
            mission_sudo = self._document_check_access('mission.mission', mission_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._mission_get_page_view_values(mission_sudo, access_token, **kw)
        return request.render("esky_mission.custom_portal_my_mission", values)

    @http.route(['/update/mission/<int:mission_id>'], type='http', auth="user", website=True)
    def custom_portal_update_mission(self, mission_id, access_token=None, **kw):
        try:
            if request.env.user.share:
                current_employee = request.env.user.employee_id
                current_mission = request.env['mission.mission'].sudo().browse(mission_id)
                if current_mission.employee_id.id != current_employee.id:
                    return request.redirect('/my')
            mission_sudo = self._document_check_access('mission.mission', mission_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._mission_get_page_view_values(mission_sudo, access_token, **kw)
        return request.render("esky_mission.custom_portal_edit_mission", values)

    @http.route(['/create/mission'], type='http', auth="user", website=True)
    def apply_mission(self, **post):
        employee = request.env.user.employee_id
        customer = request.env['res.partner'].sudo().search([("customer_rank", ">", 0), ("is_company", "=", True), ("company_id", "=", 1)])
        values = {
            'employee': employee,
            'page_name': 'create_mission',
            'customer': customer,
        }
        return request.render("esky_mission.portal_apply_mission", values)

    @http.route(['/save/mission'], type='http', auth="user", website=True)
    def save_mission(self, **post):
        field_list = ['start_date', 'name', 'option', 'customer']
        value = []
        date = datetime.strptime(post.get('start_date'), DF)
        employee = request.env.user.employee_id
        option = post.get('option').replace("'", "")
        for key in post:
            value.append(post[key])
        if any([field not in post.keys() for field in field_list]) or not all(value) or not post:
            post.update({
                'employee': employee,
                'page_name': 'create_mission',
                'error': 'Some Required Fields are Missing.'
            })
            return request.render("esky_mission.portal_apply_mission", post)
        vals = {
            'employee_id': request.env.user.employee_id.id,
            'date': date,
            'name': post.get('name'),
            'options': option,
            'desc': post.get('description')
        }
        if option == 'visit':
            vals['customer_id'] = post.get('customer')
        request.env['mission.mission'].sudo().create(vals)
        return request.redirect('/my/mission')

    @http.route('/signin/mission', type='http', auth="user", website=True)
    def signin_mission(self, **post):
        next_action = "hr_attendance.hr_attendance_action_my_attendances"
        if not post.get('latitude') or not post.get('longitude'):
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Please Allow the location access.')})
        full_latitude = post.get('latitude')
        full_longitude = post.get('longitude')
        latitude = full_latitude[:full_latitude.index('.') + 4]
        longitude = full_longitude[:full_longitude.index('.') + 4]
        latitude_parts = latitude.split('.')
        longitude_parts = longitude.split('.')
        latitude_main = int(latitude_parts[0])
        longitude_main = int(longitude_parts[0])
        latitude_decimal = int(latitude_parts[1])
        longitude_decimal = int(longitude_parts[1])
        esky_latitude = request.env['ir.config_parameter'].sudo().search([('key','=','esky_latitude')])
        esky_longitude = request.env['ir.config_parameter'].sudo().search([('key','=','esky_longitude')])

        if not esky_latitude or not esky_longitude:
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Esky latitude and longitude are missing in system parameters.')})

        esky_latitude_parts = esky_latitude.value.split('.')
        esky_longitude_parts = esky_longitude.value.split('.')
        esky_latitude_main = int(esky_latitude_parts[0])
        esky_longitude_main = int(esky_longitude_parts[0])
        esky_latitude_decimal = int(esky_latitude_parts[1])
        esky_longitude_decimal = int(esky_longitude_parts[1])
        esky_latitude_decimal_plus_range = esky_latitude_decimal + 5
        esky_longitude_decimal_plus_range = esky_longitude_decimal + 5
        esky_latitude_decimal_minus_range = esky_latitude_decimal - 5
        esky_longitude_decimal_minus_range = esky_longitude_decimal - 5
        gmap_api_key = request.env['ir.config_parameter'].sudo().search([('key','=','google_map_api_key')])
        if not gmap_api_key:
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Can not locate address beacause api key is missing. Please connect with administrator.')})
        vals = ['', latitude, longitude]
        sign_in_location = "https://maps.google.com/maps?q=" + latitude + ',' + longitude
        employee = request.env['hr.employee'].sudo().browse(int(post['employee']))
        forgot_signout_mission = request.env['mission.mission'].sudo().search([('id','!=',int(post['mission'])),('employee_id', '=', employee.id),('options','=','visit'),('signout','=',False),('signin','=',True)])
        if forgot_signout_mission:
            logger.info("Failing due to forgot mission=====================")
            employee.sudo().sh_attendance_manual(vals, next_action, entered_pin=None)
            forgot_signout_mission.sudo().write({'signout': True, 'sign_out_location': sign_in_location, 'state': 'lost', 'signin_status': 'done', 'signout_time': datetime.now()})
        current_mission = request.env['mission.mission'].sudo().browse(int(post['mission']))
        employee.sudo().sh_attendance_manual(vals, next_action, entered_pin=None)
        mission_vals = {'signin': True, 'sign_in_location': sign_in_location, 'signin_status': 'sign_out', 'signin_time': datetime.now()}
        if esky_latitude_main == latitude_main and esky_longitude_main == longitude_main and (esky_latitude_decimal_minus_range <= latitude_decimal <= esky_latitude_decimal_plus_range) and (esky_longitude_decimal_minus_range <= longitude_decimal <= esky_longitude_decimal_plus_range):
            mission_vals['signin_at_esky'] = True
        current_mission.sudo().write(mission_vals)
        return request.redirect('/my/mission')

    @http.route('/signout/mission', type='http', auth="user", website=True)
    def signout_mission(self, **post):
        next_action = "hr_attendance.hr_attendance_action_my_attendances"
        if not post.get('latitude') or not post.get('longitude'):
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Please Allow the location access.')})
        full_latitude = post.get('latitude')
        full_longitude = post.get('longitude')
        latitude = full_latitude[:full_latitude.index('.') + 4]
        longitude = full_longitude[:full_longitude.index('.') + 4]
        latitude_parts = latitude.split('.')
        longitude_parts = longitude.split('.')
        latitude_main = int(latitude_parts[0])
        longitude_main = int(longitude_parts[0])
        latitude_decimal = int(latitude_parts[1])
        longitude_decimal = int(longitude_parts[1])
        latitude_decimal_plus_range = latitude_decimal + 5
        longitude_decimal_plus_range = longitude_decimal + 5
        latitude_decimal_minus_range = latitude_decimal - 5
        longitude_decimal_minus_range = longitude_decimal - 5

        esky_latitude = request.env['ir.config_parameter'].sudo().search([('key','=','esky_latitude')])
        esky_longitude = request.env['ir.config_parameter'].sudo().search([('key','=','esky_longitude')])

        if not esky_latitude or not esky_longitude:
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Esky latitude and longitude are missing in system parameters.')})

        esky_latitude_parts = esky_latitude.value.split('.')
        esky_longitude_parts = esky_longitude.value.split('.')
        esky_latitude_main = int(esky_latitude_parts[0])
        esky_longitude_main = int(esky_longitude_parts[0])
        esky_latitude_decimal = int(esky_latitude_parts[1])
        esky_longitude_decimal = int(esky_longitude_parts[1])
        esky_latitude_decimal_plus_range = esky_latitude_decimal + 5
        esky_longitude_decimal_plus_range = esky_longitude_decimal + 5
        esky_latitude_decimal_minus_range = esky_latitude_decimal - 5
        esky_longitude_decimal_minus_range = esky_longitude_decimal - 5

        signout_at_esky = False
        if esky_latitude_main == latitude_main and esky_longitude_main == longitude_main and (esky_latitude_decimal_minus_range <= latitude_decimal <= esky_latitude_decimal_plus_range) and (esky_longitude_decimal_minus_range <= longitude_decimal <= esky_longitude_decimal_plus_range):
            signout_at_esky = True

        gmap_api_key = request.env['ir.config_parameter'].sudo().search([('key','=','google_map_api_key')])
        mission = request.env['mission.mission'].sudo().browse(int(post['mission']))
        signin_url = mission.sign_in_location
        signin_latitude, signin_longitude = map(str, signin_url.split('=')[1].split(','))
        signin_latitude_parts = signin_latitude.split('.')
        signin_longitude_parts = signin_longitude.split('.')
        signin_latitude_main = int(signin_latitude_parts[0])
        signin_longitude_main = int(signin_longitude_parts[0])
        signin_latitude_decimal = int(signin_latitude_parts[1])
        signin_longitude_decimal = int(signin_longitude_parts[1])

        if not gmap_api_key:
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Can not locate address beacause api key is missing. Please connect with administrator.')})
        vals = ['', latitude, longitude]
        if not signout_at_esky:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + latitude + ',' + longitude + '&key=' + gmap_api_key.value
        else:
            url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(signin_latitude) + ',' + str(signin_longitude) + '&key=' + gmap_api_key.value
        result = requests.get(url)
        if result.status_code == 200:
            if 'plus_code' in result.json():
                plus_code = result.json()['plus_code']
                compound_code = ((plus_code['compound_code']).split(','))[0].split()[1:]
                zone_name = ' '.join(compound_code)
            elif result.json()['status'] == 'REQUEST_DENIED':
                return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _('Can not locate address beacause api key is missing or invalid. Please connect with administrator.')})
            else:
                zone_name = 'Plus Code is not returned by API'
        else:
            compound_code = result.json()['status']
            return request.render('http_routing.http_error', {'status_code': _('Oops'),
                                                         'status_message': _(compound_code)})
        sign_out_location = "https://maps.google.com/maps?q=" + latitude + ',' + longitude
        employee = request.env['hr.employee'].sudo().browse(int(post['employee']))
        employee.sudo().sh_attendance_manual(vals, next_action, entered_pin=None)
        if mission.signin_at_esky and signout_at_esky:
            if mission.state == 'validate':
                mission.sudo().write({'signout': True, 'state': 'completed', 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})
            else:
                mission.sudo().write({'signout': True, 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})

        elif signout_at_esky:
            zone_id = request.env['zone.rate'].sudo().search([('name', '=', zone_name)], limit=1)
            if zone_id and mission.state == 'validate':
                zone_rate = 0.0 if zone_id and employee.department_id.id in zone_id.departments.ids else zone_id.rate
                mission.sudo().write({'signout': True, 'state': 'completed', 'sign_out_location': sign_out_location, 'zone_id': zone_id.id, 'zone_rate': zone_rate*2, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})
            elif zone_id and mission.state in ['validate1', 'confirm']:
                zone_rate = 0.0 if zone_id and employee.department_id.id in zone_id.departments.ids else zone_id.rate
                mission.sudo().write({'signout': True, 'sign_out_location': sign_out_location, 'zone_id': zone_id.id, 'zone_rate': zone_rate*2, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})
            elif mission.state == 'validate':
                mission.sudo().write({'signout': True, 'state': 'completed', 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})
            else:
                mission.sudo().write({'signout': True, 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_at_esky': signout_at_esky, 'signout_time': datetime.now()})
        elif signin_latitude_main == latitude_main and signin_longitude_main == longitude_main and (latitude_decimal_minus_range <= signin_latitude_decimal <= latitude_decimal_plus_range) and (longitude_decimal_minus_range <= signin_longitude_decimal <= longitude_decimal_plus_range):
            zone_id = request.env['zone.rate'].sudo().search([('name', '=', zone_name)], limit=1)
            if zone_id and mission.state == 'validate':
                zone_rate = 0.0 if zone_id and employee.department_id.id in zone_id.departments.ids else zone_id.rate
                mission.sudo().write({'signout': True, 'state': 'completed', 'sign_out_location': sign_out_location, 'zone_id': zone_id.id, 'zone_rate': zone_rate*2, 'signin_status': 'done', 'signout_time': datetime.now()})
            elif zone_id and mission.state in ['validate1', 'confirm']:
                zone_rate = 0.0 if zone_id and employee.department_id.id in zone_id.departments.ids else zone_id.rate
                mission.sudo().write({'signout': True, 'sign_out_location': sign_out_location, 'zone_id': zone_id.id, 'zone_rate': zone_rate*2, 'signin_status': 'done', 'signout_time': datetime.now()})
            elif mission.state == 'validate':
                mission.sudo().write({'signout': True, 'state': 'completed', 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_time': datetime.now()})
            else:
                mission.sudo().write({'signout': True, 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_time': datetime.now()})
        else:
            logger.info("Failing due to nothing matched=====================")
            mission.sudo().write({'signout': True, 'state': 'lost', 'sign_out_location': sign_out_location, 'signin_status': 'done', 'signout_time': datetime.now()})
        return request.redirect('/my/mission')

    @http.route('/edit/mission', type='http', auth="user", website=True)
    def edit_mission(self, **post):
        current_mission = request.env['mission.mission'].sudo().browse(int(post['mission']))
        current_mission.sudo().write({'desc': post.get('description')})
        return request.redirect('/my/mission')
