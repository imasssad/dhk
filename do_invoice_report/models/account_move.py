from itertools import chain

from odoo import models, fields, api
from num2words import num2words

class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move'

    current_company_name = fields.Many2one("res.company", 
                                            string="Current Company", 
                                            compute="compute_current_company", 
                                            store=False)
    add_attention = fields.Char("Attention")
    add_po_no = fields.Char("PO. NO.")
    add_payment = fields.Char("Payment")
    add_account_name = fields.Char("Account Name")
    add_account_no = fields.Char("Account No.")
    add_currency = fields.Char("Currency")
    add_bank_name = fields.Char("Bank Name")
    add_iban_no = fields.Char("IABN No.")
    add_swift = fields.Char("Swift")
    amount_in_words = fields.Char("Amount In Words")

    # def compute_current_company(self):
    #     companyId = self.env.context.get('allowed_company_ids')[0]
    #     company_obj = self.env['res.company'].search([('id', '=', companyId)])
    #     self.current_company_name = company_obj.id
    #     total_amount = int(self.amount_total)
    #     temp = num2words(total_amount, to = 'ordinal') + ' ' + company_obj.currency_id.name
    #     self.amount_in_words = temp

    def compute_current_company(self):
        company_id = self.env.context.get('allowed_company_ids')[0]
        company_obj = self.env['res.company'].browse(company_id)
        self.current_company_name = company_obj.id

        total_amount = int(self.amount_total)
        try:
            if total_amount < 0:
                amount_words = 'negative ' + num2words(abs(total_amount), to='cardinal')
            else:
                amount_words = num2words(total_amount, to='ordinal')
            self.amount_in_words = f"{amount_words} {company_obj.currency_id.name}"
        except Exception as e:
            self.amount_in_words = f"Error: {str(e)}"

