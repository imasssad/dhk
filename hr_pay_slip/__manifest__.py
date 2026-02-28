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

{
    'name': 'HR Pay Slip',
    'version': '16.0.1',
    'category': 'hr',
    'license': 'LGPL-3',
    'summary': """This modual help you for.""",
    'description': """This modual help you to.""",
    'sequence': 1,
    'author': 'Laxicon Solution',
    'website': 'www.laxicon.in',
    'depends': ['base', 'hr', 'hr_payroll'],
    'data': [
        'report/emp_pay_slip_report.xml',
        'views/hr_payroll_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    "pre_init_hook":  "pre_init_check",
}
