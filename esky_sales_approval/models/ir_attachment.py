from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    required_documents = fields.Boolean("Required Documents", copy=False)