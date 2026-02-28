from collections import OrderedDict
import werkzeug

import base64
from odoo import http, _
from odoo.http import request
from odoo import models, registry, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, date, timedelta


from odoo.osv.expression import OR
import requests


class LoanPortal(CustomerPortal):
    _items_per_page = 10

    def is_employee_hired_over_one_year(self, employee_hiring_date):
        # Get the current date
        current_date = datetime.now().date()

        # Calculate the difference between the current date and the hiring date
        difference = current_date - employee_hiring_date

        # Check if the difference is greater than or equal to 365 days
        if difference >= timedelta(days=365):
            return True
        return False

    def pass_loan_amount(self, employee, loan_amount, loan_id=False):
        if loan_id:
            loan_records = request.env['hr.loan'].sudo().search([('id', '!=', loan_id.id), ('employee_id', '=', employee.id), ('state', 'in', ['draft', 'waiting_approval_1', 'running'])])
        else:
            loan_records = request.env['hr.loan'].sudo().search([('employee_id', '=', employee.id), ('state', 'in', ['draft', 'waiting_approval_1', 'running'])])
        balance_amount = sum(loan_records.mapped('balance_amount')) if loan_records else 0.0
        approved_amount = (employee.contract_id.wage * 2) - balance_amount
        return (loan_amount <= approved_amount, approved_amount)

    def _prepare_portal_layout_values(self):
        values = super(LoanPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.employee_id
        loan_sudo = request.env['hr.loan'].sudo()
        if request.env.user._is_admin() or request.env.user.has_group('hr.group_hr_manager'):
            domain = []
        elif request.env.user.has_group('hr.group_hr_user'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]
        custom_loan_count = loan_sudo.search_count(domain)
        values.update({'custom_loan_count': custom_loan_count})
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.employee_id
        if request.env.user._is_admin() or request.env.user.has_group('hr.group_hr_manager'):
            domain = []
        elif request.env.user.has_group('hr.group_hr_user'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]
        if 'custom_loan_count' in counters:
            values['custom_loan_count'] = request.env['hr.loan'].sudo().search_count(domain)
        return values

    def _loan_get_page_view_values(self, custom_loan_request, access_token, **kwargs):
        values = {'page_name': 'custom_loan_page_probc', 'custom_loan_request': custom_loan_request}

        return self._get_page_view_values(custom_loan_request, access_token, values, 'my_loan_history', False,
                                          **kwargs)

    def _get_loan_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('loan_amount', 'all'):
            search_domain = OR([search_domain, [('loan_amount', 'ilike', search)]])
        if search_in in ('employee_id', 'all'):
            search_domain = OR([search_domain, [('employee_id', 'ilike', search)]])
        if search_in in ('state', 'all'):
            search_domain = OR([search_domain, [('state', 'ilike', search)]])
        if search_in in ('installment', 'all'):
            search_domain = OR([search_domain, [('installment', 'ilike', search)]])
        return search_domain

    @http.route(['/my/loan', '/my/loan/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_custom_loan(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                 search_in='all', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.employee_id
        loan_obj = http.request.env['hr.loan']

        if request.env.user._is_admin() or request.env.user.has_group('hr.group_hr_manager'):
            domain = []
        elif request.env.user.has_group('hr.group_hr_user'):
            domain = [('employee_id.user_id', '=', request.env.user.id)]
        else:
            domain = [('employee_id', '=', partner.id)]

        custom_loan_count = loan_obj.sudo().search_count(domain)

        # pager
        pager = portal_pager(url="/my/loan", total=custom_loan_count, page=page,
            step=self._items_per_page)
        searchbar_sortings = {
            'date': {'label': _('Date Ascending'), 'order': 'date', 'sequence': 1}, 
            'date desc': {'label': _('Date Descending'), 'order': 'date desc', 'sequence': 2},
            'payment_date': {'label': _('Payment Date Ascending'), 'order': 'payment_date', 'sequence': 3}, 
            'payment_date desc': {'label': _('Payment Date Descending'), 'order': 'payment_date desc', 'sequence': 4},
            'installment': {'label': _('Installment'), 'order': 'installment', 'sequence': 5},
            'state': {'label': _('Status'), 'order': 'state', 'sequence': 6},
            'employee_id': {'label': _('Customers'), 'order': 'employee_id', 'sequence': 7}

        }
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'loan_amount': {'input': 'loan_amount', 'label': _('Search in Loan Amount')},
            'installment': {'input': 'installment', 'label': _('Search in Installment')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'employee_id': {'input': 'employee_id', 'label': _('Search in Employees')},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            domain += self._get_loan_search_domain(search_in, search)

        # content according to pager and archive selected
        loans = loan_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({'loans': loans, 'page_name': 'custom_loan_page_probc', 'pager': pager,
            'default_url': '/my/loan', 'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs, 'search_in': search_in, 'sortby': sortby, })
        return request.render("ent_ohrms_loan.portal_my_loan_custom", values)

    @http.route(['/my/loan/<int:loan_id>'], type='http', auth="user", website=True)
    def custom_portal_my_loan(self, loan_id, access_token=None, **kw):
        try:
            if request.env.user.share:
                current_employee = request.env.user.employee_id
                current_loan = request.env['hr.loan'].sudo().browse(loan_id)
                if current_loan.employee_id.id != current_employee.id:
                    return request.redirect('/my')
            loan_sudo = self._document_check_access('hr.loan', loan_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._loan_get_page_view_values(loan_sudo, access_token, **kw)
        return request.render("ent_ohrms_loan.custom_portal_my_loan", values)

    @http.route(['/update/loan/<int:loan_id>'], type='http', auth="user", website=True)
    def custom_portal_update_loan(self, loan_id, access_token=None, **kw):
        try:
            if request.env.user.share:
                current_employee = request.env.user.employee_id
                current_loan = request.env['hr.loan'].sudo().browse(loan_id)
                if current_loan.employee_id.id != current_employee.id:
                    return request.redirect('/my')
            loan_sudo = self._document_check_access('hr.loan', loan_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._loan_get_page_view_values(loan_sudo, access_token, **kw)
        return request.render("ent_ohrms_loan.custom_portal_edit_loan", values)

    @http.route(['/create/loan'], type='http', auth="user", website=True)
    def apply_loan(self, **post):
        employee = request.env.user.employee_id
        values = {
            'employee': employee,
            'page_name': 'create_loan',
            'date': date.today(),
            'payment_date': date.today(),
        }
        return request.render("ent_ohrms_loan.portal_apply_loan", values)

    @http.route(['/save/loan'], type='http', auth="user", website=True)
    def save_loan(self, **post):
        field_list = ['start_date', 'loan_amount', 'installment', 'payment_date']
        value = []
        loan_date = datetime.strptime(post.get('start_date'), DF)
        payment_date = datetime.strptime(post.get('payment_date'), DF)
        employee = request.env.user.employee_id
        hiring_date = employee.first_contract_date
        if not hiring_date:
            error_message = "Sorry, you cannot create a loan amount as your hiring date is missing."
            return request.render('http_routing.http_error', {'status_code': _('Oops'), 'status_message': error_message})
        hiring_status = self.is_employee_hired_over_one_year(hiring_date)
        loan_pass, approved_amount = self.pass_loan_amount(employee, float(post.get('loan_amount')))

        if not hiring_status:
            error_message = "Sorry, you have been hired for less than a year and cannot create a loan."
            return request.render('http_routing.http_error', {'status_code': _('Oops'), 'status_message': error_message})

        if not loan_pass:
            error_message = "Sorry, you cannot create a loan more than approved amount."
            return request.render('http_routing.http_error', {'status_code': _('Oops'), 'status_message': error_message})

        for key in post:
            value.append(post[key])
        if any([field not in post.keys() for field in field_list]) or not all(value) or not post:
            post.update({
                'employee': employee,
                'page_name': 'create_loan',
                'error': 'Some Required Fields are Missing.'
            })
            return request.render("ent_ohrms_loan.portal_apply_loan", post)
        vals = {
            'employee_id': employee.id,
            'date': loan_date,
            'loan_amount': post.get('loan_amount'),
            'installment': post.get('installment'),
            'payment_date': payment_date
        }
        loan_id = request.env['hr.loan'].sudo().with_context(portal=True).create(vals)
        loan_id.sudo().compute_installment()
        return request.redirect('/my/loan')

    @http.route('/edit/loan', type='http', auth="user", website=True)
    def edit_loan(self, **post):
        current_loan = request.env['hr.loan'].sudo().browse(int(post['loan']))
        vals = {}
        if post.get('loan_amount'):
            loan_pass, approved_amount = self.pass_loan_amount(current_loan.employee_id, float(post.get('loan_amount')), current_loan)
            if not loan_pass:
                error_message = "Sorry, you already have a loan of approved amount you can not increase that."
                return request.render('http_routing.http_error', {'status_code': _('Oops'), 'status_message': error_message})
            vals['loan_amount'] = post.get('loan_amount')
        if post.get('installment'):
            vals['installment'] = post.get('installment')
        if post.get('payment_date'):
            payment_date = datetime.strptime(post.get('payment_date'), DF)
            vals['payment_date'] = payment_date
        current_loan.sudo().with_context(portal=True).write(vals)
        if vals.get('loan_amount'):
            current_loan.sudo().compute_installment()
        return request.redirect('/my/loan')


    @http.route(['/cancel/loan/<int:loan_id>'], type='http', auth="user", website=True)
    def custom_portal_cancel_loan(self, loan_id, access_token=None, **kw):
        try:
            if request.env.user.share:
                current_employee = request.env.user.employee_id
                current_loan = request.env['hr.loan'].sudo().browse(loan_id)
                if current_loan.employee_id.id != current_employee.id:
                    return request.redirect('/my')
            loan_sudo = self._document_check_access('hr.loan', loan_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        current_loan.sudo().action_cancel()
        return request.redirect('/my/loan')
