from odoo import fields, models


class ConfirmApprovalWorkflow(models.Model):
    _name = 'confirm.approval.workflow'
    _description = "Confirm Approval Workflow"

    status_by = fields.Many2one('res.users', string="By")
    user_role = fields.Selection(related='status_by.role', string='Role')
    status = fields.Selection([('approved', 'Approved'), ('rejected', 'Rejected')], string="Status")
    status_date = fields.Datetime(string="Date")
    reason = fields.Char(string="Reason")
    sale_order_id = fields.Many2one('sale.order')