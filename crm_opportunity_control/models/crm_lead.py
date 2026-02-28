from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_data_amount_total = fields.Monetary(compute='_compute_sale_data_amount', string="Sum of Orders", help="Untaxed Total of Confirmed Orders", currency_field='sale_currency_id')
    sale_currency_id = fields.Many2one("res.currency", string='Currency', compute="_compute_sale_currency")

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order', 'order_ids.company_id')
    def _compute_sale_data_amount(self):
        for lead in self:
            sale_orders = lead.order_ids.filtered_domain(self._get_lead_sale_order_domain())
            lead.sale_data_amount_total = sum(
                order.currency_id._convert(
                    order.amount_untaxed, order.currency_id, order.company_id, order.date_order or fields.Date.today()
                )
                for order in sale_orders
            )

    @api.depends('order_ids.currency_id')
    def _compute_sale_currency(self):
        for lead in self:
        	sale_orders = lead.order_ids.filtered_domain(self._get_lead_sale_order_domain())
        	for order in sale_orders:
        		lead.sale_currency_id = order.currency_id
        		break
        	if not sale_orders:
        		company_currency = lead.company_currency or self.env.company.currency_id
        		lead.sale_currency_id = company_currency

    def write(self, vals):
        if 'stage_id' in vals and not self.env.user.has_group('base.group_system'):
            stage_id = self.env['crm.stage'].browse([vals['stage_id']])
            for lead in self:
                sale_orders = lead.order_ids
                sent_orders = sale_orders.filtered(lambda order: order.state in ['sent', 'sale', 'done'])
                if not sent_orders and stage_id.name not in ['LEAD', 'OPPORTUNITY']:
                    raise UserError(_('Quotation is not sent. Please first send it.'))
        return super(CrmLead, self).write(vals)
