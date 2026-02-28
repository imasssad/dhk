from odoo import api, models, fields, _


class Hrattendance(models.Model):
    _inherit = 'hr.attendance'

    date_is_checkin = fields.Boolean(string="Is Checkin", defalse=False)
    date_is_checkout = fields.Boolean(string="Is Checkout", defalse=False)
    ref_meeting_id = fields.Many2one('calendar.event', string="Refrence")

    def create(self, vals):
        res = super(Hrattendance, self).create(vals)
        if res.check_in:
            res.date_is_checkin = True
        return res

    def write(self, vals):
        response = super(Hrattendance, self).write(vals)
        if vals and vals.get('check_out'):
            self.date_is_checkout = True
        return response
