from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SalePricelistWizard(models.TransientModel):
    _name = 'sale.pricelist.wizard'
    _description = 'Mass Update Pricelist on Quotations and Sales Orders'

    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
    )
    order_ids = fields.Many2many(
        'sale.order',
        string='Orders',
        readonly=True,
    )
    recompute_prices = fields.Boolean(
        string='Recompute Prices',
        default=False,
        help='If checked, unit prices will be recalculated using the new pricelist. '
             'Leave unchecked to keep existing prices as-is.',
    )
    order_count = fields.Integer(
        string='Number of Orders',
        compute='_compute_order_count',
    )

    @api.depends('order_ids')
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if active_ids:
            orders = self.env['sale.order'].browse(active_ids)
            if not orders:
                raise UserError(_('No orders selected.'))
            # Allow ALL statuses — no filtering by state
            res['order_ids'] = [(6, 0, orders.ids)]
        return res

    def action_apply_pricelist(self):
        self.ensure_one()
        if not self.order_ids:
            raise UserError(_('No orders selected.'))

        for order in self.order_ids:
            if self.recompute_prices:
                # Update pricelist first, then recompute line prices
                order.sudo().write({'pricelist_id': self.pricelist_id.id})
                for line in order.order_line:
                    if line.product_id:
                        new_price = line._get_display_price()
                        if new_price:
                            line.sudo().write({'price_unit': new_price})
            else:
                # Only swap pricelist, keep all existing unit prices untouched
                order.sudo().write({'pricelist_id': self.pricelist_id.id})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Pricelist Updated'),
                'message': _(
                    'Pricelist "%s" applied to %d order(s).'
                ) % (self.pricelist_id.name, len(self.order_ids)),
                'sticky': False,
                'type': 'success',
            },
        }
