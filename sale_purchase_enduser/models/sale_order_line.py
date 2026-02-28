from odoo import models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
 
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        values.update({
            'end_user_detail': self.order_id.end_user_detail or '',
            'start_date': self.start_date,  # Add start date
            'end_date': self.end_date,      # Add end date
        })
        return values
