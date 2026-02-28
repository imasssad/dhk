# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import ValidationError, Warning, UserError


class MergePurchaseOrder(models.TransientModel):
    _name = 'merge.purchase.order'

    merge_type = fields.Selection([('new_cancel', 'Create new purchase quote and cancel all selected purchase quote'),
                                   ('new_delete', 'Create new purchase quote and delete all selected purchase quote'),
                                   ('merge_cancel',
                                    'Merge purchase quote on existing selected purchase quote and cancel others'),
                                   (
                                       'merge_delete',
                                       'Merge purchase quote on existing selected purchase quote and delete others')],
                                  default='new_cancel')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Quote')
    vendor_id = fields.Many2one('res.partner', string='Vendor')

    @api.onchange('merge_type')
    def onchange_merge_type(self):
        res = {'domain': {}}
        if self.merge_type in ['merge_cancel', 'merge_delete', 'new_cancel', 'new_delete']:
            purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
            res['domain']['purchase_order_id'] = [('id', 'in', [purchase.id for purchase in purchase_orders])]
            res['domain']['vendor_id'] = [('id', 'in', purchase_orders.mapped('partner_id.id'))]
        return res

    def merge_purchase_order(self):
        purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids', []))
        if len(purchase_orders) < 2:
            raise UserError(_('Please select atleast two purchase quote to perform the Merge Operation.'))

        if any(order.state not in ['draft', 'sent'] for order in purchase_orders):
            raise UserError(_('Please select Purchase quote which are in RFQ stage to perform the Merge Operation.'))

        if self.merge_type == 'new_cancel' or self.merge_type == 'new_delete':
            purchase_orders_id = self.env['purchase.order'].create({
                'partner_id': self.vendor_id.id,
                'merge_date': datetime.now(),
                'merge_user_id': self.env.user.id,
                'merge_purchase_orders': ",".join(purchase_orders.mapped('name')),
                'is_merge_order': True,
            })

            order_line_ids = purchase_orders.mapped('order_line')
            for line in order_line_ids:
                line_id = purchase_orders_id.order_line.filtered(lambda l: l.product_id.id == line.product_id.id)

                if line_id:
                    line_id[0].write({'product_qty': line_id.product_qty + line.product_qty})
                else:
                    line_data = {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_qty': line.product_qty,
                        'qty_received': line.qty_received,
                        'qty_invoiced': line.qty_invoiced,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'taxes_id': [(6, 0, [tax.id for tax in line.taxes_id])],
                        'price_subtotal': line.price_subtotal,
                        'date_planned': line.date_planned,
                        'order_id': purchase_orders_id.id or False,
                    }
                    self.env['purchase.order.line'].create(line_data)
                    purchase_orders.write({'state': 'cancel'})
            if self.merge_type == 'new_delete':
                purchase_orders.unlink()

        elif self.merge_type == 'merge_cancel' or self.merge_type == 'merge_delete':
            purchase_orders_id = self.purchase_order_id
            purchase_orders_id.write({'merge_date': datetime.now(),
                                      'merge_user_id': self.env.user.id,
                                      'merge_purchase_orders': ",".join(purchase_orders.mapped('name')),
                                      'is_merge_order': True, })
            process_products = {}
            for line in purchase_orders_id.order_line:
                product_id = line.product_id.id
                if product_id in process_products:
                    process_products[product_id].write(
                        {'product_qty': process_products[product_id].product_qty + line.product_qty})
                    line.unlink()
                else:
                    process_products[product_id] = line

            for order in purchase_orders:
                if order != purchase_orders_id:
                    order_line_ids = order.mapped('order_line')
                    order.write({'state': 'cancel'})
                    for line in order_line_ids:
                        line_id = purchase_orders_id.order_line.filtered(
                            lambda l: l.product_id.id == line.product_id.id)
                        if line_id:
                            line_id[0].write({'product_qty': line_id[0].product_qty + line.product_qty})
                        else:
                            line_data = {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'product_qty': line.product_qty,
                                'qty_received': line.qty_received,
                                'qty_invoiced': line.qty_invoiced,
                                'product_uom': line.product_uom.id,
                                'price_unit': line.price_unit,
                                'taxes_id': [(6, 0, [tax.id for tax in line.taxes_id])],
                                'price_subtotal': line.price_subtotal,
                                'date_planned': line.date_planned,
                                'order_id': purchase_orders_id.id or False,
                            }
                            self.env['purchase.order.line'].create(line_data)
                    if self.merge_type == 'merge_delete':
                        order.unlink()
