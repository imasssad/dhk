# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLineTaxes(models.Model):
    """
    Extend Purchase Order to add bulk tax management for all order lines.
    """
    _inherit = 'purchase.order'

    line_taxes = fields.Many2many(
        comodel_name="account.tax",
        string="Purchase Taxes",
        domain="[('type_tax_use', '=', 'purchase')]",
        help="Select taxes to apply to all purchase order lines"
    )

    @api.onchange('line_taxes')
    def _onchange_line_taxes(self):
        """
        When line_taxes field changes, update taxes_id on all purchase order lines.
        This allows bulk assignment of taxes to all lines at once.
        """
        if self.order_line:
            for line in self.order_line:
                line.taxes_id = self.line_taxes
