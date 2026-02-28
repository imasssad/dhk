from odoo import models, _
from odoo.exceptions import ValidationError
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_payment_ids(self, invoice):
        payment = invoice.invoice_payments_widget
        payment_ids = []
        if payment:
            payment_dic = json.loads(payment)
            if payment_dic:
                payment_dic = payment_dic.get('content')
                for payment in payment_dic:
                    if payment.get('account_payment_id'):
                        payment_ids.append(payment.get('account_payment_id'))
                if payment_ids:
                    payment_ids = self.env['account.payment'].browse(payment_ids)
                    return payment_ids
        return payment_ids

    def unlink(self):
        for sale in self:
            if sale.picking_ids:
                raise ValidationError(_('Plase Unlink all picking of this sale order'))
            if sale.invoice_ids:
                raise ValidationError(_('Plase Unlink all Invoice of this sale order'))
        return super(SaleOrder, self).unlink()

    def action_cancel(self):
        if self.picking_ids:
            for picking in self.picking_ids:
                if picking.state != 'cancel':
                    picking.action_cancel()

        if self.invoice_ids:
            for invoice in self.invoice_ids:
                if invoice.state != 'cancel':
                    payment_ids = self.get_payment_ids(invoice)
                    if payment_ids:
                        for payment in payment_ids:
                            if payment.state in ['posted', 'reconciled']:
                                payment.action_draft()
                                payment.action_cancel()
                    invoice.button_draft()
                    invoice.button_cancel()
        for line in self.order_line:
            line.qty_delivered = 0
        return self.write({'state': 'cancel'})
