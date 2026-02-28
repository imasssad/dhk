{
    'name': 'Mass Update Pricelist on Quotations',
    'version': '16.0.1.0.0',
    'category': 'Sales',
    'summary': 'Select multiple quotations and apply a pricelist in bulk',
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_pricelist_wizard.xml',
        'views/sale_order_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
