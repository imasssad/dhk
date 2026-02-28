from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ReturnDateWizard(models.TransientModel):
    _name = 'return.date.wizard'
    _description = 'Return Date Wizard'

    return_date = fields.Date(string="Return Date", required=True, default=fields.Date.today)

    def confirm_return(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        if active_id:
            cheque = self.env['cheque.manage'].browse(active_id)
            cheque.process_return(self.return_date)