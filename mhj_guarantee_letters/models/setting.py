# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LetterGuranteeSetting(models.Model):
    _name = 'guarantee.letter.setting'
    _rec_name='name'

    name = fields.Char('Name')
    
    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Debit",
        required=True,
        )

    letter_type = fields.Selection(
        string="Letter Type",
        selection=[
            ('premium', 'Premium'), 
            ('final', 'Final'),
            ('deposit', 'Deposit'),
            ]
        )

    bank_expense_account_id = fields.Many2one(
        comodel_name='account.account', 
        string="Account Expenses Debit",
        required=True,
        )

    bank_expense_credit_account_id = fields.Many2one(
        comodel_name='account.account', 
        string="Account Expenses Credit",
        required=True,
        )

    bank_lg_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Bank LG Account",
        required=True,
        )

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)