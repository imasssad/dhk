# -*- coding: utf-8 -*-
###############################################################################
# Author : Laxicon Solution. (<https://www.laxicon.in/>)
# Copyright(c): 2015-Today Laxicon Solution.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.laxicon.in/license>
###############################################################################

from odoo import models, api
from num2words import num2words


class HrPaySlipReport(models.AbstractModel):
    _name = 'report.hr_pay_slip.report_hr_pay_slip'
    _template = 'hr_pay_slip.report_hr_pay_slip'
    _description = "Hr Pay Slip Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = self.env['hr.payslip'].browse(docids)
        basic_slry = 0
        total = 0
        final_total = 0
        count = 0
        for rec in ids.line_ids:
            total += rec.total
            count += 1
            if count in [1, 2, 3, 4, 5, 6]:
                final_total += rec.total
            else:
                final_total -= rec.total
            if rec.name == 'Basic Salary':
                basic_slry = rec.total
        taxt_amt = num2words(final_total, lang='en')
        day = 0
        for days in ids.worked_days_line_ids:
            day += days.number_of_days
        return {
            'doc_model': 'hr.payslip',
            'docs': ids,
            'basic_slry': basic_slry,
            'day': day,
            'total': total,
            'taxt_amt': taxt_amt,
        }
