# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
import werkzeug

import base64
from odoo import http, _
from odoo.http import request
from odoo import models, registry, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):
    _items_per_page = 10

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        CalendarMeeting = request.env['calendar.event'].sudo()
        custom_meeting_count = CalendarMeeting.search_count(
            [('partner_ids', 'child_of', [partner.commercial_partner_id.id])])
        values.update({'custom_meeting_count': custom_meeting_count, })
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'custom_meeting_count' in counters:
            values['custom_meeting_count'] = request.env['calendar.event'].sudo().search_count(
                [('partner_ids', 'child_of', [partner.commercial_partner_id.id])])
        return values

    def _meeting_get_page_view_values(self, custom_meeting_request, access_token, **kwargs):
        values = {'page_name': 'custom_meeting_page_probc', 'custom_meeting_request': custom_meeting_request, }

        return self._get_page_view_values(custom_meeting_request, access_token, values, 'my_meeting_history', False,
                                          **kwargs)

    @http.route(['/my/custom_meeting_request', '/my/custom_meeting_request/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_custom_meeting(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
                                 search_in='name', **kw):

        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        meeting_obj = http.request.env['calendar.event']
        domain = [('partner_ids', 'child_of', [partner.commercial_partner_id.id])]

        custom_meeting_count = meeting_obj.sudo().search_count(domain)

        # pager
        pager = portal_pager(url="/my/custom_meeting_request", total=custom_meeting_count, page=page,
            step=self._items_per_page)
        searchbar_sortings = {'start': {'label': _('Start Date Ascending'), 'order': 'start'},
            'stop': {'label': _('End Date Ascending'), 'order': 'stop'},
            'start desc': {'label': _('Start Date Descending'), 'order': 'start desc'},
            'stop desc': {'label': _('End Date Descending'), 'order': 'stop desc'}, }

        searchbar_inputs = {'name': {'input': 'name', 'label': _('Search in Subject')}, }
        # default sort by value
        if not sortby:
            sortby = 'start'
        order = searchbar_sortings[sortby]['order']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # content according to pager and archive selected
        meetings = meeting_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({'meetings': meetings, 'page_name': 'custom_meeting_page_probc', 'pager': pager,
            'default_url': '/my/custom_meeting_request', 'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs, 'search_in': search_in, 'sortby': sortby, })
        return request.render("calendar_meeting_portal.portal_my_meeting_custom", values)

    @http.route(['/my/custom_meeting_request/<int:meeting_id>'], type='http', auth="public", website=True)
    def custom_portal_my_meeting(self, meeting_id, access_token=None, **kw):
        try:
            meeting_sudo = self._document_check_access('calendar.event', meeting_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._meeting_get_page_view_values(meeting_sudo, access_token, **kw)
        return request.render("calendar_meeting_portal.custom_portal_my_meeting", values)
