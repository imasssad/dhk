# -*- coding: utf-8 -*-
{
    'name': "Sales Team Leader and Access Restriction ",
    'summary': """
Allow team leader to see his team's documents, not access right to other team's documents""",
    'description': """
Allow the team leader to see his team's documents, not access right to other team's documents""",
    'author': 'NOS Erp Consulting',
    'version': '15.0.0.1',
    'license': 'OPL-1',
    'price': 00.00,
    'currency': 'USD',
    'support': 'odoo@nostech.vn',
    'images': [
        # 'static/description/cover.png'
    ],
    'depends': ['sale'],
    'data': [
        # Security
        'security/sale_order_security.xml',
    ],
    'auto_install': False,
    'installable': True,
    'category': 'Sales',
    'application': True,
    'sequence': 10,
}
