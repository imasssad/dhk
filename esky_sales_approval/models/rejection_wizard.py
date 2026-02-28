from odoo import fields, models
from datetime import datetime


class RejectionReasonWizard(models.TransientModel):
    _name = 'reject.reason.wizard'
    _description = "Reject reason wizard"

    name = fields.Text(string="Reason")

    def action_reject_order(self):
        active_obj = self.env['sale.order'].browse(self.env.context.get('active_id'))
        active_obj.refused_to_sent({'reason': self.name, 'status_by': active_obj.env.user.id,'status_date': datetime.now(), 'status': 'rejected', 'sale_order_id': active_obj.id})
        return True