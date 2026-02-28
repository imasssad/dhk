{
    'name': "DO Sales Report",
    'summary': """Extended version of sales report""",
    'description': """Extended version of sales report""",
    'author': "Tushar Ruhela",
    'category': 'Sales',
    'version': '19.0.1.1',
    'depends': ['base', 'sale', 'sale_management', 'web', 'account'],
    'data': [
        'views/sale_order_view.xml',
        'data/report_paperformat.xml',
        'report/sale_report.xml',
        'views/sale_report_templates.xml',
        'views/sale_proforma_invoice_report_template.xml',
    ],
}
