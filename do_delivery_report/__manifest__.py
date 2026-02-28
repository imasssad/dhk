{
    'name': "Delivery Report",
    'summary': """Extended version of Delivery report""",
    'description': """Extended version of Delivery report""",
    'author': "Tushar Ruhela",
    'category': 'Accounting',
    'version': '19.0.1.1',
    'depends': ['base', 'account', 'sale', 'stock'],
    'data': [
        'views/stock_picking_view.xml',
        'data/report_paperformat.xml',
        'report/delivery_report.xml',
        'views/delivery_report_templates.xml',
    ],
}
