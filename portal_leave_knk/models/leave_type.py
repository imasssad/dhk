from odoo import models, fields


class LeaveType(models.Model):
    _inherit = "hr.leave.type"

    apply_before_days = fields.Integer(string='Apply Before (Days)')
