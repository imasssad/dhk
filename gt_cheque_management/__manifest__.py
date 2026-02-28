# -*- coding: utf-8 -*-
{
    'name' : 'Cheque Management',
    'version' : '19.0',
    'author' : 'CBSEGYPT',
    'category' : 'Accounting',
    'description' : """
check management
cheque management
bank check
bank cheque
checks management
cheques management
bank checks
bank cheques
outgoing check
outgoing cheque
incoming check
incoming cheque
outgoing checks
outgoing cheques
incoming checks
incoming cheques
out check
out cheque
income check
income cheque
out checks
out cheques
income checks
income cheques
check management in odoo
cheque management in odoo
bank check in odoo
bank cheque in odoo
checks management in odoo
cheques management in odoo

""",
    # 'summary': """This module will help to track outgoing checks and incoming checks outgoing check and incoming check outgoing cheque and incoming cheque outgoing cheques and incoming cheques Post Dated Cheque management PDC cheque management account check post dated check PDC check customer check vendor check writing account check writing account cheque writing incoming check outgoing check print cheque print check bank cheque printing check""",
    'depends' : ['base', 'account','attachment_indexation','account_accountant'],
    "license" : "Other proprietary",
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'security/group_rule.xml',
        'report/report_wizard_view.xml',
        'report/cheque_report.xml',
        'wizard/cheque_wizard.xml',
        'wizard/cheque_date_wizard.xml',
        'wizard/return_date_wizard_view.xml',
        'views/ir_sequence_data.xml',
        'views/cheque_manage.xml',
        'views/res_config.xml',
       # 'report/incoming_cheque_template.xml',
       # 'report/outgoing_cheque_template.xml',

    ],
    'qweb' : [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
