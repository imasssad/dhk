from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    sale_sheet = fields.Boolean("P&L", copy=False)