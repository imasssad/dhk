from odoo import models, fields, _
from odoo.exceptions import ValidationError


class CancelSalesOrders(models.TransientModel):
    _name = 'cancel.sales.orders'
    _description = 'Cancel Sales Orders'

    cancel_type = fields.Selection([
        ('cancel', 'Cancel Only'),
        ('cancel_reset_draft', 'Cancel and Reset to Draft'),
        ('cancel_and_delete', 'Cancel and Delete')], string='Cancel Type', default="cancel")
    cancel_delivery_order = fields.Boolean(string="Cancel Delivery Order")
    cancel_invoice_and_payment = fields.Boolean(string="Cancel Invoice and Payment")

    def confirm_btn_wizard(self):
        for rec in self:
            sale_order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))

            if rec.cancel_delivery_order:
                for res in sale_order_ids:
                    for picking in res.picking_ids:
                        picking.action_cancel()

            if rec.cancel_invoice_and_payment:
                for res in sale_order_ids:
                    for invo in res.invoice_ids:
                        invo.button_cancel()

            if rec.cancel_type == 'cancel':
                for res in sale_order_ids:
                    if res.state != 'cancel':
                        res.action_cancel()
                return True

            elif rec.cancel_type == 'cancel_reset_draft':
                for res in sale_order_ids:
                    res.action_cancel()
                    res.action_draft()
                return True

            elif rec.cancel_type == 'cancel_and_delete':
                for res in sale_order_ids:
                    if res.picking_ids:
                        for picking in res.picking_ids:
                            picking.action_cancel()
                            picking.action_set_draft()
                            picking.unlink()
                    if res.invoice_ids:
                        for invo in res.invoice_ids:
                            if invo.state == 'posted':
                                invo.button_draft()
                            invo.button_cancel()
                            invo.unlink()
                    res.action_cancel()
                    res.unlink()
                return True


class ConfirmSalesOrders(models.TransientModel):
    _name = 'confirm.sales.orders'
    _description = 'confirm Sales Orders'

    def confirm_sales_order(self):
        confirm_sale_order = self.env['sale.order'].browse(self._context.get('active_ids'))
        for rec in confirm_sale_order:
            if rec.state in ['done', 'cancel']:
                raise ValidationError(_('Change the State or Use Reset & Confirm Sales Orders Button.'))
            rec.action_confirm()
            return True

    def confirm_and_reset_sales_order(self):
        confirm_sale_order = self.env['sale.order'].browse(self._context.get('active_ids'))
        for rec in confirm_sale_order:
            rec.action_draft()
            rec.action_confirm()
        return True
