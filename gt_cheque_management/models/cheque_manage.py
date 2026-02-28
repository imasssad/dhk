
from odoo import fields, models ,api, _
from odoo.exceptions import UserError, ValidationError

    
class ChequeManage(models.Model):
    _name = "cheque.manage"
    _description = 'Cheque Manage'

        
    partner_ids = fields.Many2many('res.partner', compute='_get_partner_ids')
    seq_no = fields.Char(string='Sequence',copy=False)
    name = fields.Char(string='Name')
    attachment_count = fields.Integer(string='Attachment Count', compute='_get_attach', readonly=True,copy=False)
    journal_item_count = fields.Integer(string='Journal Items', compute='_journal_item_count', readonly=True,copy=False)
    payer = fields.Many2one('res.partner', 'Payee')
    bank_account = fields.Many2one('account.account', string='Bank account')
    bank_name = fields.Text(string='Bank Name')
    debit_account = fields.Many2one('account.account', string='Debit account')
    credit_account = fields.Many2one('account.account', string='Credit account')
    debit_cashed_account = fields.Many2one('account.account', string='Cashed account', readonly=True)
    debit_bounced_account = fields.Many2one('account.account', string='Bounced account', readonly=True)
    debit_returned_account = fields.Many2one('account.account', string='Returned account', readonly=True)
    debit_deposit_account = fields.Many2one('account.account', string='Deposit account', readonly=True)
    credit_cashed_account = fields.Many2one('account.account', string='Cashed account', readonly=True)
    credit_bounced_account = fields.Many2one('account.account', string='Bounced account', readonly=True)
    credit_returned_account = fields.Many2one('account.account', string='Returned account', readonly=True)
    credit_deposit_account = fields.Many2one('account.account', string='Deposit account', readonly=True)
    debit = fields.Monetary(default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'confirm': [('readonly', True)]})
    cheque_date = fields.Date(string='Cheque Date',default=fields.Date.context_today)
    cashed_date = fields.Date(string='Cashed Date',copy=False)
    return_date = fields.Date(string='Returned Date',copy=False)
    cheque_receive_date = fields.Date(string='Cheque Given/Receive Date')
    cheque_no = fields.Char(string='Cheque Number',copy=False)
    amount = fields.Float(string='Amount')
    bounced = fields.Boolean(string='Bounced', copy=False)
    partner_id = fields.Many2one('res.partner', 'Company')
    cheq_attachment_ids=fields.One2many('ir.attachment','cheque_id','Attachment Line',copy=False)
    state = fields.Selection([
    ('draft', 'Draft'),
    ('register', 'Registered'),
    ('deposit', 'Deposited'),
    ('done', 'Cashed'),
    ('transfer', 'Transfered'),
    ('bounce', 'Bounced'),
    ('return', 'Returned'),
    ('cancel', 'Cancelled'),
    ], string='Status', default='draft')
    description = fields.Text('Description')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', compute='_get_currency_id',string="Company Currency", readonly=True, store=True)
    move_line_ids = fields.One2many('account.move.line', 'cheque_id', readonly=True, copy=False, ondelete='restrict')

    amount_with_currency = fields.Char(
        string="Amount",
        compute='_compute_amount_with_currency',
        store=False
    )

    @api.model
    def default_get(self, deafult_fields):
        res = super(ChequeManage, self).default_get(deafult_fields)
        debit_account = False
        credit_account = False
        Parameters = self.env['ir.config_parameter'].sudo()
        if res.get('cheq_type') == 'incoming':
            debit_account = Parameters.get_param('gt_cheque_management.debit_inc_account')
        #            credit_account = Parameters.get_param('gt_cheque_management.credit_inc_account')
        else:
            #            debit_account = Parameters.get_param('gt_cheque_management.debit_out_account')
            credit_account = Parameters.get_param('gt_cheque_management.credit_out_account')
        res.update({'debit_account': int(debit_account), 'credit_account': int(credit_account),
                    'bank_account': int(Parameters.get_param('gt_cheque_management.deposite_account')),
                    'journal_id': int(Parameters.get_param('gt_cheque_management.journal_id'))})
        return res

    @api.depends('cheq_attachment_ids')
    def _get_attach(self):
        Attachment = self.env['ir.attachment']
        for attachment in self:
            attachment.attachment_count = Attachment.search_count([('cheque_id', '=', attachment.id)])

    @api.depends('move_line_ids')
    def _journal_item_count(self):
        for item in self:
            item.journal_item_count = len(item.move_line_ids)

    cheq_type = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing')])

    @api.depends('cheq_type')
    def _get_partner_ids(self):
        partner_obj = self.env['res.partner']
        for record in self:
            if record.cheq_type == 'incoming':
                record.partner_ids = partner_obj.search([('customer_rank', '=', True)])
            else:
                record.partner_ids = partner_obj.search([('supplier_rank', '=', True)])

    @api.depends('bank_account')
    def _get_currency_id(self):
        for cheque in self:
            if cheque.bank_account.currency_id:
                cheque.company_currency_id = cheque.bank_account.currency_id
            else:
                cheque.company_currency_id = cheque.company_id.currency_id

    @api.depends('amount', 'company_currency_id')
    def _compute_amount_with_currency(self):
        for line in self:
            currency = line.company_currency_id.symbol or line.company_currency_id.name
            line.amount_with_currency = "{} {}".format('{:,.2f}'.format(line.amount),currency)

    _sql_constraints = [
        ('cheque_no_company_uniq', 'unique (cheque_no,company_id)', 'The Cheque Number of must be unique per company !')
    ]
    
    @api.model
    def create(self, vals):
        if vals.get('cheq_type')=='incoming':
            vals['seq_no'] = self.env['ir.sequence'].next_by_code('cheque.manage.incoming', vals.get('cheque_date')) or '/'
        else:
            vals['seq_no'] = self.env['ir.sequence'].next_by_code('cheque.manage.outgoing', vals.get('cheque_date')) or '/'
        return super(ChequeManage, self).create(vals)


    def action_cashed(self):
        return {
            'res_model': 'cheque.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('gt_cheque_management.cheque_wizard_view').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        

    def action_transfer(self):
        return {
            'res_model': 'cheque.transfer.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('gt_cheque_management.cheque_transfer_wizard_view').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
    
    def abc(self):
        acc_pay = self.env['account.payment'].search([('move_line_ids','=',self.ids)])
        for rec in acc_pay:
            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
    
            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer_rank':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier_rank':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
    
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
    
            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
    
            rec.write({'state': 'posted', 'move_name': move.name})
            

    def action_submit(self):
        Move=self.env['account.move']
        amount = self.amount
        currency_id = self.company_id.currency_id.id
        if self.bank_account.currency_id:
            current_rate = self.env['res.currency'].search([('id', '=', self.bank_account.currency_id.id)]).rate
            amount = self.amount / current_rate
            currency_id = self.bank_account.currency_id.id

        if self.cheq_type=='incoming':
            credit_line={
                'account_id':self.payer.property_account_receivable_id.id,
                'partner_id':self.payer.id,
                'name':self.name,
                'debit':0,
                'credit':amount,
                'date_maturity':self.cheque_receive_date,
                'cheque_id':self.id,
                'currency_id': currency_id,
                'amount_currency': (0 - self.amount),
            }
            debit_line={
                'account_id':self.debit_account.id,
                'partner_id':self.payer.id,
                'name':self.name,
                'debit':amount,
                'credit':0,
                'date_maturity':self.cheque_receive_date,
                'cheque_id':self.id,
                'currency_id': currency_id,
                'amount_currency': self.amount,
            }
        else:
            credit_line={
                'account_id':self.credit_account.id,
                'partner_id':self.payer.id,
                'name':self.name,
                'debit':0,
                'credit':amount,
                'date_maturity':self.cheque_receive_date,
                'cheque_id':self.id,
                'currency_id': currency_id,
                'amount_currency': (0 - self.amount),
            }
            debit_line={
                'account_id':self.payer.property_account_payable_id.id,
                'partner_id':self.payer.id,
                'name':self.name,
                'debit':amount,
                'credit':0,
                'date_maturity':self.cheque_receive_date,
                'cheque_id':self.id,
                'currency_id': currency_id,
                'amount_currency': self.amount,
            }
        move_vals={
            'date':self.cheque_date,
            'journal_id':self.journal_id.id,
            'ref':(self.name + ' ' + self.cheque_date.strftime("%x")),
            'line_ids':[(0,0,credit_line),(0,0,debit_line)]
        }
        move_id=Move.sudo().create(move_vals)
        move_id.sudo().action_post()
        return self.write({'state': 'register'})

    def action_cancel(self):
        if not self.move_line_ids:
            raise UserError(_("You cannot cancel a record that is not posted yet!"))
        for rec in self:
            for move in rec.sudo().move_line_ids.mapped('move_id'):
                move.sudo().button_cancel()
                move.sudo().with_context(force_delete=True).unlink()
            return rec.write({'state': 'cancel'})
    
#    It will make reverse entry for the registerd entries

    def action_bounce(self):
        return {
            'res_model': 'cheque.date.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('gt_cheque_management.cheque_date_wizard_view').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
             'context': {'bounce':True},
        }


    

    def action_draft(self):
        return self.write({'state': 'draft'})
    

    # def action_return(self):
    #     if self.bounced:
    #         for rec in self:
    #             for move in rec.sudo().move_line_ids.mapped('move_id'):
    #                 move.sudo().button_cancel()
    #                 move.sudo().with_context(force_delete=True).unlink()
    #             return rec.write({'state': 'return','return_date':fields.Date.today()})
    #     else:
    #         Move=self.env['account.move']
    #         cheque_vals = {}
    #         amount = self.amount
    #         currency_id = self.company_id.currency_id.id
    #         if self.bank_account.currency_id:
    #             current_rate = self.env['res.currency'].search([('id', '=', self.bank_account.currency_id.id)]).rate
    #             amount = self.amount / current_rate
    #             currency_id = self.bank_account.currency_id.id
    #         if self.cheq_type=='incoming':
    #             cheque_vals['debit_returned_account'] = self.payer.property_account_receivable_id.id
    #             credit_line={
    #                 'account_id':self.debit_account.id,
    #                 'partner_id':self.payer.id,
    #                 'name':self.name,
    #                 'debit':0,
    #                 'credit':amount,
    #                 'date_maturity':self.cheque_receive_date,
    #                 'cheque_id':self.id,
    #                 'currency_id': currency_id,
    #                 'amount_currency': (0 - self.amount),
    #             }
    #             debit_line={
    #                 'account_id':self.payer.property_account_receivable_id.id,
    #                 'partner_id':self.payer.id,
    #                 'name':self.name,
    #                 'debit':amount,
    #                 'credit':0,
    #                 'date_maturity':self.cheque_receive_date,
    #                 'cheque_id':self.id,
    #                 'currency_id': currency_id,
    #                 'amount_currency': self.amount,
    #             }
    #         else:
    #             cheque_vals['credit_returned_account'] = self.payer.property_account_payable_id.id
    #             credit_line={
    #                 'account_id':self.payer.property_account_payable_id.id,
    #                 'partner_id':self.payer.id,
    #                 'name':self.name,
    #                 'debit':0,
    #                 'credit':amount,
    #                 'date_maturity':self.cheque_receive_date,
    #                 'cheque_id':self.id,
    #                 'currency_id': currency_id,
    #                 'amount_currency': (0 - self.amount),
    #             }
    #             debit_line={
    #                 'account_id':self.credit_account.id,
    #                 'partner_id':self.payer.id,
    #                 'name':self.name,
    #                 'debit':amount,
    #                 'credit':0,
    #                 'date_maturity':self.cheque_receive_date,
    #                 'cheque_id':self.id,
    #                 'currency_id': currency_id,
    #                 'amount_currency': self.amount,
    #             }
    #         move_vals={
    #             'date':fields.Date.today(),
    #             'journal_id':self.journal_id.id,
    #             'ref':(self.name + ' ' + self.cheque_date.strftime("%x")),
    #             'line_ids':[(0,0,credit_line),(0,0,debit_line)],
    #         }
    #         move_id=Move.sudo().create(move_vals)
    #         move_id.sudo().action_post()
    #         cheque_vals.update({'state': 'return','return_date':fields.Date.today()})
    #         return self.write(cheque_vals)
    #
    #

    def action_return(self):
        return {
            'name': 'Select Return Date',
            'type': 'ir.actions.act_window',
            'res_model': 'return.date.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def process_return(self, return_date):
        self.ensure_one()
        if self.bounced:
            for move in self.sudo().move_line_ids.mapped('move_id'):
                move.sudo().button_cancel()
                move.sudo().with_context(force_delete=True).unlink()
            return self.write({'state': 'return', 'return_date': return_date})
        else:
            Move = self.env['account.move']
            cheque_vals = {}
            amount = self.amount
            currency_id = self.company_id.currency_id.id
            if self.bank_account.currency_id:
                current_rate = self.env['res.currency'].search([('id', '=', self.bank_account.currency_id.id)]).rate
                amount = self.amount / current_rate
                currency_id = self.bank_account.currency_id.id
                aml = self.env['account.move.line'].search([('cheque_id', '=', self.id), ('debit', '!=', 0)], limit=1)
                if aml:
                    amount = aml.debit

            if self.cheq_type == 'incoming':
                cheque_vals['debit_returned_account'] = self.payer.property_account_receivable_id.id
                credit_line = {
                    'account_id': self.debit_account.id,
                    'partner_id': self.payer.id,
                    'name': self.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': self.cheque_receive_date,
                    'cheque_id': self.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - self.amount),
                }
                debit_line = {
                    'account_id': self.payer.property_account_receivable_id.id,
                    'partner_id': self.payer.id,
                    'name': self.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': self.cheque_receive_date,
                    'cheque_id': self.id,
                    'currency_id': currency_id,
                    'amount_currency': self.amount,
                }
            else:
                cheque_vals['credit_returned_account'] = self.payer.property_account_payable_id.id
                credit_line = {
                    'account_id': self.payer.property_account_payable_id.id,
                    'partner_id': self.payer.id,
                    'name': self.name,
                    'debit': 0,
                    'credit': amount,
                    'date_maturity': self.cheque_receive_date,
                    'cheque_id': self.id,
                    'currency_id': currency_id,
                    'amount_currency': (0 - self.amount),
                }
                debit_line = {
                    'account_id': self.credit_account.id,
                    'partner_id': self.payer.id,
                    'name': self.name,
                    'debit': amount,
                    'credit': 0,
                    'date_maturity': self.cheque_receive_date,
                    'cheque_id': self.id,
                    'currency_id': currency_id,
                    'amount_currency': self.amount,
                }
            move_vals = {
                'date': return_date,
                'journal_id': self.journal_id.id,
                'ref': (self.name + ' ' + self.cheque_date.strftime("%x")),
                'line_ids': [(0, 0, credit_line), (0, 0, debit_line)],
            }
            move_id = Move.sudo().create(move_vals)
            move_id.sudo().action_post()
            cheque_vals.update({'state': 'return', 'return_date': return_date})
            return self.write(cheque_vals)

    def action_deposit(self):
        return {
            'res_model': 'cheque.date.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('gt_cheque_management.cheque_date_wizard_view').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'deposit': True}
        }


    

    def unlink(self):
        if any(bool(rec.move_line_ids) for rec in self):
            raise UserError(_("You cannot delete a record that is already posted!"))
        return super(ChequeManage, self).unlink()
    
    def open_payment_matching_screen(self):
        # Open reconciliation view for customers/suppliers
        move_line_id = False
        for move_line in self.move_line_ids:
            if move_line.account_id.reconcile:
                move_line_id = move_line.id
                break;
        action_context = {'company_ids': [self.company_id.id], 'partner_ids': [self.payer.commercial_partner_id.id]}
        if self.payer.customer_rank:
            action_context.update({'mode': 'customers_rank'})
        elif self.payer.supplier_rank:
            action_context.update({'mode': 'suppliers_rank'})
        if move_line_id:
            action_context.update({'move_line_id': move_line_id})
        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
            'context': action_context,
        }
        

    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('cheque_id', 'in', self.ids)],
        }
    
    
class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    
    cheque_id = fields.Many2one('cheque.manage', 'Cheque Id')
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    cheque_id = fields.Many2one('cheque.manage', 'Cheque Id')
    
