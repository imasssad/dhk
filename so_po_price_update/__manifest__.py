{
    'name': 'SO-PO Price Update Automation',
    'version': '19.0.1.0.0',
    'category': 'Sales/Purchase',
    'summary': 'Export PO from SO, update prices via Excel, auto-update SO costs',
    'description': """
Export and update Purchase Order prices from Sales Orders.
This module adds buttons to Sales Orders to export related PO prices and import updates.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'purchase', 'do_purchase_report'],  # Add do_purchase_report here
    'data': [
        'security/ir.model.access.csv',
        'wizard/po_price_update_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
