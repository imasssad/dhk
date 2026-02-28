from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _order_revised_count(self):
        for sale_rec in self:
            order_revised_count = self.search(
                [('parent_saleorder_id', '=', sale_rec.id)])
            sale_rec.order_revised_count = len(order_revised_count)

    from_revision = fields.Many2one('sale.order', 'From Revision', copy=False)
    parent_saleorder_id = fields.Many2one(
        'sale.order', 'Parent SaleOrder', copy=False)
    order_revised_count = fields.Integer(
        '# of Orders Revised', compute='_order_revised_count', copy=False)
    so_number = fields.Integer('SO Number', copy=False, default=1)
    state = fields.Selection(selection_add=[
        ('draft_quote', 'Revised Quotation'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('revised', 'Revised Order'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True,
        tracking=True, default='draft')

    def write(self, values):
        if values.get('order_line') or values.get('partner_id') or values.get('validity_date') or values.get('date_order') or values.get('payment_term_id'):
            self.so_revision_quote()
            values["so_number"] = self.so_number + 1
        res = super(SaleOrder, self).write(values)
        return res

    def so_revision_quote(self):
        for cur_rec in self:
            vals = {
                'name': cur_rec.name + '_Old_Version_' + str(cur_rec.so_number),
                'state': 'revised',
                'parent_saleorder_id': cur_rec.id,
                'validity_date': cur_rec.validity_date,
            }
            cur_rec.copy(default=vals)

    def convert_to_current_quotation(self):
        if self.parent_saleorder_id.state not in ['draft', 'sent']:
            raise ValidationError(_('Sorry, Can not perform this operation.'))
        vals = {
                'name': self.parent_saleorder_id.name,
                'parent_saleorder_id': False,
                'from_revision': self.id,
                'validity_date': self.validity_date,
                'state': self.parent_saleorder_id.state,
                'so_number': self.parent_saleorder_id.so_number
            }
        new_order = self.copy(default=vals)
        old_parent = self.parent_saleorder_id
        revisions = self.search([('parent_saleorder_id', '=', old_parent.id)])
        for revision in revisions:
            revision.sudo().write({'parent_saleorder_id': new_order.id})
        old_parent.sudo()._action_cancel()
        old_parent.sudo().with_context(only_parent=True).unlink()
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'target': 'main',
                'res_id': new_order.id,
                'context': {'edit': True}
            }

    def unlink(self):
        for record in self:
            if not record._context.get('only_parent') and not record.parent_saleorder_id:
                revisions = record.search([('parent_saleorder_id', '=', record.id)])
                if revisions:
                    revisions.sudo()._action_cancel()
                    revisions.sudo().unlink()
        res = super(SaleOrder, self).unlink()
        return res
