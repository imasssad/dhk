# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderTaxes(models.Model):
    _inherit = 'sale.order'

    line_taxes = fields.Many2many(comodel_name="account.tax" , string="Taxes", )
    line_vendor = fields.Many2one(comodel_name="res.partner" , string="Distributor", )
    line_discount = fields.Float(string="Discount", tracking=True)

    @api.onchange('line_taxes')
    def partner_id_method(self):
        self.order_line.tax_id = self.line_taxes
        
    @api.onchange('line_vendor')
    def vendor_id_method(self):
        self.order_line.vendor_id = self.line_vendor
        
    @api.onchange('line_discount')
    def line_discount_method(self):
        self.order_line.discount = self.line_discount


# class Followers(models.Model):
#    _inherit = 'mail.followers'

#    @api.model
#    def create(self, vals):
#         if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
#             dups = self.env['mail.followers'].search([('res_model', '=',vals.get('res_model')),
#                                            ('res_id', '=', vals.get('res_id')),
#                                            ('partner_id', '=', vals.get('partner_id'))])
#             if len(dups):
#                 for p in dups:
#                     p.unlink()
#         return super(Followers, self).create(vals)
