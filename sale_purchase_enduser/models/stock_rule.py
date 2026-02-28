from odoo import api, models

class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        res = super(StockRule, self)._run_buy(procurements)

        for procurement, rule in procurements:
            group = procurement.values.get('group_id')
            sale_order = group.sale_id if group else None
            sale_line = self.env['sale.order.line'].browse(procurement.values.get('sale_line_id'))

            if sale_order:
                # Update PO header fields
                purchase_orders = self.env['purchase.order'].search([
                    ('origin', '=', sale_order.name)
                ])
                for po in purchase_orders:
                    po.end_user_detail = sale_order.end_user_detail
                    
                # Update PO line fields
                if sale_line:
                    po_lines = self.env['purchase.order.line'].search([
                        ('sale_line_id', '=', sale_line.id)
                    ])
                    po_lines.write({
                        'start_date': sale_line.start_date,
                        'end_date': sale_line.end_date
                    })

        return res
