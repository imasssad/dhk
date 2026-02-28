{
    'name': "Invoice Report",
    'summary': """Extended version of invoice report""",
    'description': """Extended version of invoice report""",
    'author': "Tushar Ruhela",
    'category': 'Accounting',
    'version': '1.1',
    'depends': ['base', 'account'],
    'data': [
        'views/account_move_view.xml',
        'data/report_paperformat.xml',
        'report/inovice_report.xml',
        'views/invoice_report_templates.xml',
    ],
}
