{
    'name': "Purchase Report",
    'summary': """Extended version of purchase report""",
    'description': """Extended version of purchase report""",
    'author': "Tushar Ruhela",
    'category': 'Purchase',
    'version': '1.1',
    'depends': ['base', 'sale', 'sale_management', 'web', 'account','purchase'],
    'data': [
        'views/purchase_order_view.xml',
        'data/report_paperformat.xml',
        'report/purchase_report.xml',
        'views/purchase_report_templates.xml',
        'views/purchase_rfq_report_templates.xml',
        'views/esky_po_print.xml',
        'views/esky_po_rfq_print.xml',
        'views/esky_delivery_Note.xml',
    ],
}
