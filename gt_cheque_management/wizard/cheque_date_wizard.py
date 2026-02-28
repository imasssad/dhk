from odoo import api, fields, models, _


class ChequeDateWizard(models.TransientModel):
    _name = "cheque.date.wizard"

    @api.model
    def _default_currency_id(self):
        cheque_id = self.env['cheque.manage'].browse(self.env.context.get('active_id'))
        return cheque_id.bank_account.currency_id.id
        
    currency_id = fields.Many2one('res.currency', string="Currency", default=_default_currency_id)
    bank_account = fields.Many2one('account.account', string='Bank account', domain="[('currency_id', '=', currency_id)]")    
    cheque_deposite_date = fields.Date(string='Cheque Date')


    def cash_date_change(self):
        cheque_manage_id_ = self.env['cheque.manage'].browse(self.env.context.get('active_id'))
        Move = self.env['account.move']
        amount = cheque_manage_id_.amount
        currency_id = cheque_manage_id_.company_id.currency_id.id
        if self.currency_id:
            current_rate = self.env['res.currency'].search([('id', '=', self.currency_id.id)]).rate
            amount = cheque_manage_id_.amount / current_rate
            currency_id = cheque_manage_id_.bank_account.currency_id.id
        if self.env.context.get('bounce'):
            cheque_vals = {}
            if cheque_manage_id_.cheq_type == 'incoming':
                cheque_vals['debit_bounced_account'] = cheque_manage_id_.payer.property_account_receivable_id.id
                credit_line = {
                    'account_id': cheque_manage_id_.debit_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - cheque_manage_id_.amount),
                }
                debit_line = {
                    'account_id': cheque_manage_id_.payer.property_account_receivable_id.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': cheque_manage_id_.amount,
                }
            else:
                cheque_vals['credit_bounced_account'] = cheque_manage_id_.payer.property_account_payable_id.id
                credit_line = {
                    'account_id': cheque_manage_id_.payer.property_account_payable_id.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - cheque_manage_id_.amount),
                }
                debit_line = {
                    'account_id': cheque_manage_id_.credit_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': cheque_manage_id_.amount,
                }
            move_vals = {
                'date': self.cheque_deposite_date,
                'journal_id': cheque_manage_id_.journal_id.id,
                'ref': (cheque_manage_id_.name + ' ' + cheque_manage_id_.cheque_date.strftime("%x")),
                'line_ids': [(0, 0, credit_line), (0, 0, debit_line)]
            }
            move_id = Move.sudo().create(move_vals)
            move_id.sudo().action_post()
            cheque_vals.update({'state': 'bounce', 'bounced': True})
            return cheque_manage_id_.write(cheque_vals)
        if self.env.context.get('deposit'):
            cheque_vals = {}
            if cheque_manage_id_.cheq_type == 'incoming':
                cheque_vals['debit_deposit_account'] = cheque_manage_id_.bank_account.id
                credit_line = {
                    'account_id': cheque_manage_id_.debit_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - cheque_manage_id_.amount),
                }
                debit_line = {
                    'account_id': cheque_manage_id_.bank_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': cheque_manage_id_.amount,
                }
            else:
                cheque_vals['credit_deposit_account'] = cheque_manage_id_.bank_account.id
                credit_line = {
                    'account_id': cheque_manage_id_.bank_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - cheque_manage_id_.amount),
                }
                debit_line = {
                    'account_id': cheque_manage_id_.credit_account.id,
                    'partner_id': cheque_manage_id_.payer.id,
                    'name': cheque_manage_id_.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': cheque_manage_id_.cheque_receive_date,
                    'cheque_id': cheque_manage_id_.id,
                    'currency_id': currency_id,
                    'amount_currency': cheque_manage_id_.amount,
                }
            move_vals = {
                'date': self.cheque_deposite_date,
                'journal_id': cheque_manage_id_.journal_id.id,
                'ref': (cheque_manage_id_.name + ' ' + cheque_manage_id_.cheque_date.strftime("%x")),
                'line_ids': [(0, 0, credit_line), (0, 0, debit_line)]
            }
            move_id = Move.sudo().create(move_vals)
            move_id.sudo().action_post()
            cheque_vals.update({'state': 'deposit','bank_account': self.bank_account.id})
            return cheque_manage_id_.write(cheque_vals)

