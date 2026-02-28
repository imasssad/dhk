
from odoo import fields, models ,api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    debit_inc_account = fields.Many2one('account.account', string='Debit account',config_parameter='gt_cheque_management.debit_inc_account')
    credit_out_account = fields.Many2one('account.account', string='Credit account',config_parameter='gt_cheque_management.credit_out_account')
    deposite_account = fields.Many2one('account.account', string='Deposite account',config_parameter='gt_cheque_management.deposite_account')
    journal_id = fields.Many2one('account.journal', string='Specific Journal',config_parameter='gt_cheque_management.journal_id')
    
    