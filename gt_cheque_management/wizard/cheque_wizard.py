


from odoo import api, fields, models, _


class ChequeWizard(models.TransientModel):
    _name = "cheque.wizard"
    
    cheque_date = fields.Date(string='Cheque Date')
    

    def cash_submit(self):  
        cheque_inc = self.env['cheque.manage'].search([])
        cheque_inc.cheque_date = self.cheque_date 
        return cheque_inc.write({'state': 'done'})
    
    
class ChequeTransferWizard(models.TransientModel):
    _name = "cheque.transfer.wizard"
    
    transfer_date = fields.Date(string='Transfered Date')
    contact = fields.Many2one('res.partner', 'Contact')
    

    def transfer_submit(self):  
        cheque_inc = self.env['cheque.manage'].search([])
        return cheque_inc.write({'state': 'transfer'})
    
                    
class ChequeOutgoingWizard(models.TransientModel):
    _name = "cheque.outgoing.wizard"

    @api.model
    def _default_currency_id(self):
        cheque_id = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
        return cheque_id.bank_account.currency_id.id
        
    currency_id = fields.Many2one('res.currency', string="Currency", default=_default_currency_id)
    cheque_date = fields.Date(string='Cheque Date')
    bank_acc = fields.Many2one('account.account', 'Bank Account', domain="[('currency_id', '=', currency_id)]", required=True)
    journal_item_date=fields.Date('Journal Item Date')
    
    

    def cash_out_submit(self):
        cheque_id = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))        
        Move=self.env['account.move']
        amount = cheque_id.amount
        currency_id = cheque_id.company_id.currency_id.id
        if cheque_id.bank_account.currency_id:
            current_rate = self.env['res.currency'].search([('id', '=', cheque_id.bank_account.currency_id.id)]).rate
            amount = cheque_id.amount / current_rate
            currency_id = cheque_id.bank_account.currency_id.id
        cheque_vals = {}
        if cheque_id.cheq_type=='incoming':
            cheque_vals['debit_cashed_account'] = self.bank_acc.id
            credit_line={
                'account_id':cheque_id.debit_account.id,
                'partner_id':cheque_id.payer.id,
                'name':cheque_id.name,
                'debit':0,
                'credit':amount,
                'date_maturity':cheque_id.cheque_receive_date,
                'cheque_id':cheque_id.id,
                'currency_id': currency_id,
                'amount_currency': (0 - cheque_id.amount),
            }
            debit_line={
                'account_id':self.bank_acc.id,
                'partner_id':cheque_id.payer.id,
                'name':cheque_id.name,
                'debit':amount,
                'credit':0,
                'date_maturity':cheque_id.cheque_receive_date,
                'cheque_id':cheque_id.id,
                'currency_id': currency_id,
                'amount_currency': cheque_id.amount,
            }
        else:
            cheque_vals['credit_cashed_account'] = self.bank_acc.id
            credit_line={
                'account_id':self.bank_acc.id,
                'partner_id':cheque_id.payer.id,
                'name':cheque_id.name,
                'debit':0,
                'credit':amount,
                'date_maturity':cheque_id.cheque_receive_date,
                'cheque_id':cheque_id.id,
                'currency_id': currency_id,
                'amount_currency': (0 - cheque_id.amount),
            }
            debit_line={
                'account_id':cheque_id.credit_account.id,
                'partner_id':cheque_id.payer.id,
                'name':cheque_id.name,
                'debit':amount,
                'credit':0,
                'date_maturity':cheque_id.cheque_receive_date,
                'cheque_id':cheque_id.id,
                'currency_id': currency_id,
                'amount_currency': cheque_id.amount,
            }
        move_vals={
            'date':self.journal_item_date,
            'journal_id':cheque_id.journal_id.id,
            'ref': (cheque_id.name + ' ' + cheque_id.cheque_date.strftime("%x")),
            'line_ids':[(0,0,credit_line),(0,0,debit_line)]
        }
        move_id=Move.sudo().create(move_vals)
        move_id.sudo().action_post()
        cheque_vals.update({'cashed_date':self.cheque_date,'state':'done', 'bank_account': self.bank_acc.id})
        cheque_id.write(cheque_vals)
        return True
