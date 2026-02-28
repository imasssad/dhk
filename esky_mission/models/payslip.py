from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_total_expense(self, payslip):
        missions = self.env['mission.mission'].sudo().search([('employee_id', '=', payslip.employee_id), ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('state', '=', 'completed')])
        total_expense = 0.0
        if missions:
            total_expense = sum(mission.zone_rate for mission in missions)
        return total_expense
