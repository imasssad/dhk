# -*- coding: utf-8 -*-
{
    'name': "Purchase Line Taxes",
    'summary': """Change all the taxes of RFQ/Purchase Order lines""",
    'description': """
        This module allows you to change taxes for all lines in a Request for Quotation (RFQ) 
        or Purchase Order at once from the header level.
        
        Features:
        - Add a taxes field at the purchase order header level
        - Automatically apply selected taxes to all purchase order lines
        - Works with Odoo 16 Enterprise on odoo.sh
    """,
    'author': "MDS",
    'website': "https://MDS.com",
    'category': 'Purchase',
    'version': '16.0.1.0.0',
    'depends': ['base', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
