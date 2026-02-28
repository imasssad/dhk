# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_merge_order = fields.Boolean(string='Is Merge Order',store=True)
    merge_date = fields.Date(string="Merge date",)
    merge_purchase_orders = fields.Char(string='Merge Purchase Orders')
    merge_user_id = fields.Many2one('res.users', string='Merge By')
