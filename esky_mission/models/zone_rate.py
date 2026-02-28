from odoo import fields, models


class ZoneRate(models.Model):
    _name = 'zone.rate'
    _inherit = 'mail.thread'
    _description = 'Zone with Rates'

    name = fields.Char('Zone', required=True)
    rate = fields.Float('Rate', required=True, tracking=True)
    departments = fields.Many2many('hr.department', string="Departments")
