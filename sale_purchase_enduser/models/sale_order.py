from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    end_user_detail = fields.Html('End User Detail')

    def button_confirm(self):
        # Check if end user details are already filled
        if not self.end_user_detail:
            return {
                'name': 'Enter End User Details',
                'type': 'ir.actions.act_window',
                'res_model': 'end.user.details.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_sale_order_id': self.id
                }
            }
        # If details exist, continue to approval process
        return super(SaleOrder, self).button_confirm()
