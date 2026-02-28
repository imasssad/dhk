{
    'name': 'Sale to Purchase End User Details',
    'version': '16.0.1.0',
    'depends': ['sale_management', 'purchase_stock', 'web', 'do_purchase_report'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/wizard_end_user_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
