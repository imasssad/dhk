{
    'name' : 'Import P&L Sheet',
    'version' : '1.0',
    'description': """This module is used to import sale order lines""",
    'category': 'Sales',
    'company': "CBS EGYPT",
    'author': "Suraj Rawat",
    'website': "https://cbsegypt.com",
    'depends' : ['base', 'sale', 'esky_sales_approval', 'sale_margin'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_wizard_views.xml',
        'views/sale_order_views.xml',
        'wizard/demo_data.xml',
        'wizard/wizard_message_view.xml'
    ],  
    'installable': True,
    'application': True,
    'auto_install': False,
}