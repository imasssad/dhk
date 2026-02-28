# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request

class WebsiteCustomerCalendarComment(http.Controller):

    @http.route(['/custom_calendar/comment'], type='http', auth="user", website=True)
    def customer_meeting_comment(self, **kw):
        custom_calendar_comment = kw.get('custom_calendar_comment')
        custom_calendar_id = kw.get('custom_calendar_comment_id')
        if custom_calendar_comment and custom_calendar_id:
            record_id = request.env['calendar.event'].sudo().browse(int(custom_calendar_id))
            group_msg = _(custom_calendar_comment)
            record_id.message_post(body=group_msg, message_type='comment')
        return request.redirect('/my/custom_meeting_request')  #
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:hashiftwidth=4:
