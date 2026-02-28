# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class LetterOfGurantee(models.Model):
    _name = 'guarantee.letter'
    _rec_name = 'letter_number'
    _inherit = ["mail.thread"]

    number = fields.Char('Sequence')
    state = fields.Selection(string="State", 
        selection=[
            ('draft', 'Draft'), ('confirm', 'Running'), ('closed', 'Closed')],
        required=False, default="draft"
        )
    partner_id = fields.Many2one(string='Customer', comodel_name='res.partner',)
    journal_id = fields.Many2one(comodel_name='account.journal', string='Bank',domain=[('type','=','bank')],)
    letter_type = fields.Selection(string="Letter Type",selection=[('premium', 'Premium'), ('final', 'Final'), ('deposit', 'Deposit'), ],)
    config_id = fields.Many2one('guarantee.letter.setting', 'Letter Name',)
    analytic_id = fields.Many2one('account.analytic.account', 'Expenses Analytic Account',)
    move_id = fields.Many2one('account.move', 'Letter Journal',)
    expenses_id = fields.Many2one('account.move', 'Expenses Journal',)
    letter_amount =fields.Float('Letter Amount',)
    cover_amount_percentage =fields.Float('Cover Percentage %',)
    cover_amount =fields.Float('Cover Amount ',)
    is_expenses = fields.Boolean('Is Expense',)
    is_letter_name = fields.Boolean('Is letter name',default=False,)
    expenses_amount = fields.Float('Expenses Amount',)
    transaction_date = fields.Date(string="Transaction Date",)
    start_date = fields.Date(string="Start Date",)
    end_date = fields.Date(string="End Date",)
    letter_number=fields.Char('Letter Number',)
    note=fields.Text('Note',)
    is_close=fields.Boolean('Is Closed',readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    increase_count = fields.Integer(compute="_compute_increase_count", string='Increase Guarantee Count')
    extend_count = fields.Integer(compute="_compute_extend_count", string='Extend Guarantee Count')
    reduction_count = fields.Integer(compute="_compute_reduction_count", string='Reduce Guarantee Count')
    closing_count = fields.Integer(compute="_compute_closing_count", string='Close Guarantee Count')

    def _compute_increase_count(self):
        guarantee_increase = self.env['guarantee.increase']
        for letter in self:
            increase_guarantees = guarantee_increase.search_count([('letter_guarantee_id', '=', letter.id)])
            if increase_guarantees:
                letter.increase_count = increase_guarantees
            else:
                letter.increase_count = 0

    def action_view_increase_guarantee(self):
        action = self.env['ir.actions.act_window']._for_xml_id('mhj_guarantee_letters.guarantee_inc_action_view')
        if self.state == 'closed':
            action['context'] = {'default_letter_guarantee_id': self.id, 'create':False, 'edit':False}
        else:
            action['context'] = {'default_letter_guarantee_id': self.id}
        action["domain"] = [("letter_guarantee_id", "=", self.id)]
        return action

    def _compute_extend_count(self):
        guarantee_extension = self.env['guarantee.extension']
        for letter in self:
            extension_guarantees = guarantee_extension.search_count([('letter_guarantee_id', '=', letter.id)])
            if extension_guarantees:
                letter.extend_count = extension_guarantees
            else:
                letter.extend_count = 0

    def action_view_extend_guarantee(self):
        action = self.env['ir.actions.act_window']._for_xml_id('mhj_guarantee_letters.guarantee_ext_action_view')
        if self.state == 'closed':
            action['context'] = {'default_letter_guarantee_id': self.id, 'create':False, 'edit':False}
        else:
            action['context'] = {'default_letter_guarantee_id': self.id}
        action["domain"] = [("letter_guarantee_id", "=", self.id)]
        return action

    def _compute_reduction_count(self):
        guarantee_reduction = self.env['guarantee.reduction']
        for letter in self:
            reduction_guarantees = guarantee_reduction.search_count([('letter_guarantee_id', '=', letter.id)])
            if reduction_guarantees:
                letter.reduction_count = reduction_guarantees
            else:
                letter.reduction_count = 0

    def action_view_reduction_guarantee(self):
        action = self.env['ir.actions.act_window']._for_xml_id('mhj_guarantee_letters.reduce_guarantee_action_view')
        if self.state == 'closed':
            action['context'] = {'default_letter_guarantee_id': self.id, 'create':False, 'edit':False}
        else:
            action['context'] = {'default_letter_guarantee_id': self.id}
        action["domain"] = [("letter_guarantee_id", "=", self.id)]
        return action

    def _compute_closing_count(self):
        guarantee_closing = self.env['guarantee.closing']
        for letter in self:
            closing_guarantees = guarantee_closing.search_count([('letter_guarantee_id', '=', letter.id)])
            closing_guarantees_confirmed = guarantee_closing.search_count([('letter_guarantee_id', '=', letter.id),('state','=','confirm')])
            if closing_guarantees:
                letter.closing_count = closing_guarantees
                if closing_guarantees_confirmed:
                    letter.state = 'closed'
            else:
                letter.closing_count = 0

    def action_view_closing_guarantee(self):
        action = self.env['ir.actions.act_window']._for_xml_id('mhj_guarantee_letters.close_guarantee_action_view')
        if self.state == 'closed':
            action['context'] = {'default_letter_guarantee_id': self.id, 'create':False, 'edit':False}
        else:
            action['context'] = {'default_letter_guarantee_id': self.id}
        action["domain"] = [("letter_guarantee_id", "=", self.id)]
        return action

    @api.onchange('letter_type')
    def _onchange_letter_name_readonly(self):
        if self.letter_type:
            self.is_letter_name = True

    @api.onchange('cover_amount')
    def _onchange_cover_amount(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount_percentage =rec.cover_amount/rec.letter_amount*100

    @api.onchange('cover_amount_percentage')
    def _onchange_cover_amount_percentage(self):
        for rec in self:
            if rec.letter_amount:
                rec.cover_amount = rec.letter_amount * rec.cover_amount_percentage /100
    
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and not rec.move_id:
                raise UserError('Can not delete')
            else:
                super().unlink()

    def cancel_button(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.button_cancel()
                rec.move_id.unlink()
                rec.state= 'draft'
            else:
                rec.state = 'draft'
            if rec.expenses_id:
                rec.expenses_id.button_cancel()
                rec.expenses_id.unlink()
                rec.state= 'draft'
            else:
                rec.state = 'draft'

    def confirm_button(self):
        for rec in self:
            config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,'date': rec.transaction_date,'ref': rec.letter_number})
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,'account_id': config.account_id.id,'name': rec.letter_number,'debit': rec.letter_amount, 'partner_id': rec.partner_id.id})
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,'account_id': config.bank_expense_credit_account_id.id,'name': rec.letter_number,'credit': rec.cover_amount,})
            remaining_amount = rec.letter_amount - rec.cover_amount
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,'account_id': config.bank_lg_account_id.id,'name': rec.letter_number,'credit': remaining_amount,})
            move.action_post()
            rec.move_id = move.id
            if rec.is_expenses :
                config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
                move = self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,'date': rec.transaction_date,'ref': rec.letter_number})
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,'account_id': config.bank_expense_account_id.id,'name': rec.letter_number,'debit': rec.expenses_amount,})
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,'account_id': config.bank_expense_credit_account_id.id,'name': rec.letter_number,'credit': rec.expenses_amount,})
                move.action_post()
                rec.expenses_id = move.id
            rec.state = "confirm"


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('guarantee.letter') or '/'
        vals['number'] = seq
        return super(LetterOfGurantee, self).create(vals)

