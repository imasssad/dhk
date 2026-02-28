import pytz
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.form import WebsiteForm


class WebsiteMeeting(http.Controller):

    @http.route(['/schedule'], type='http', auth="user", methods=['GET'], website=True)
    def schedule(self, **kw):
        values = {'website': request.website,
            'members': [('{0} [{1}] ({2})'.format(emp.name, emp.job_title, emp.resource_calendar_id.tz), emp.user_id.id)
                        for emp in request.env['hr.employee'].sudo().search([('user_id', '!=', None)])],
            'partners': [('{0}'.format(partner.name), partner.id) for partner in
                         request.env['res.partner'].sudo().search([])], 'tzs': [(tz, tz) for tz in
                                                                                sorted(pytz.all_timezones, key=lambda
                                                                                    tz: tz if not tz.startswith(
                                                                                    'Etc/') else '_')], }
        return request.render('dics_portal_schedule_meeting.schedule_meeting', values)


class WebsiteFormInherit(WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        if model_name == 'calendar.event':
            # attendees = request.env['res.partner'].sudo().browse(
            #     int(kwargs['partner'])) + request.env.user.partner_id
            attendees = request.env.user.partner_id

            kwargs['partner_ids'] = ','.join([str(partner_id) for partner_id in attendees.ids])
            # time_from = kwargs['timeslot'].split(' - ')[0]
            meeting_date = pytz.timezone(kwargs['timezone']).localize(datetime.strptime(kwargs['meeting_date'], '%Y-%m-%d'))
            # meeting_start_date = pytz.timezone(kwargs['timezone']).localize(
            #     datetime.strptime(kwargs['meeting_start_datetime'], '%Y-%m-%dT%H:%M'))
            # meeting_end_date = pytz.timezone(kwargs['timezone']).localize(
            #     datetime.strptime(kwargs['meeting_end_datetime'], '%Y-%m-%dT%H:%M'))
            request.params.update({'partner_ids': ','.join([str(partner_id) for partner_id in attendees.ids]),
                # 'start': meeting_start_date.astimezone(pytz.timezone('UTC')).replace(tzinfo=None),
                # 'stop': meeting_end_date.astimezone(pytz.timezone('UTC')).replace(tzinfo=None) + timedelta(
                #     minutes=int(kwargs['duration'])), 'duration': (int(kwargs['duration']) / 60),
                # 'customer_name':str(kwargs['customer_name']),
            })
            # kwargs['start'] = meeting_start_date.astimezone(pytz.timezone('UTC')).replace(tzinfo=None)
            # kwargs['stop'] = meeting_end_date.astimezone(pytz.timezone('UTC')).replace(
            #     tzinfo=None)  # kwargs['customer_name'] = request.params['customer_name']
        # print("kwargs ========================== ",kwargs)
        return super(WebsiteFormInherit, self)._handle_website_form(model_name, **kwargs)
