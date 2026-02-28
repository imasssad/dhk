# -*- coding: utf-8 -*-
{
    'name': "mhj_guarantee_letters",

    'summary': """MHJ Guarantee letters""",
    'description': """MHJ Guarantee letters""",
    'author': "MHJ",
    'website': "HAJJAJ.PRO",
    'version': '14.0.1.0',

    'depends': ['account'],

    'data': [
        'security/ir.model.access.csv',
        'security/gurantee_letter_security.xml',
        'views/guarantee_letter.xml',
        'views/setting.xml',
        'views/guarantee_increase.xml',
        'views/guarantee_extension.xml',
        'views/guarantee_reduction.xml',
        'views/gurantee_completion.xml',
        'views/guarantee_send.xml',
        'views/guarantee_recieve.xml',
    ],

    'application': True,
    'installable': True,
}
