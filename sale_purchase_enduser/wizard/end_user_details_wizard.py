from odoo import models, fields

class EndUserDetailsWizard(models.TransientModel):
    _name = 'end.user.details.wizard'
    _description = 'End User Details Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    end_user_detail = fields.Html('End User Detail', required=True)

    def confirm_details(self):

        self.sale_order_id.write({'end_user_detail': self.end_user_detail})
        return self.sale_order_id.button_confirm()

