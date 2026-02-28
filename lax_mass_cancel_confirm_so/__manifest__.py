# -*- coding: utf-8 -*-
{
    'name': "Mass Cancel Confirm Sale Orders",
    'summary': """ This module allows to Cancel or Confirm Quotations mass/bulk/multiple Sales Orders
            from the tree view.""",
    'author': "Laxicon Solution",
    'website': "www.laxicon.in",
    'sequence': 101,
    'support': 'info@laxicon.in',
    'category': 'Sales',
    'version': '16.0.1',
    'license': 'LGPL-3',
    'description': """ This module allow to Cancle or Confirm Sales Orders.
    """,
    'depends': ['sale_management', 'account', 'lax_mass_cancel_picking'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_orders_cancel_confirm_wizard.xml',
    ],
    'images':  ["static/description/banner.png"],
    'installable': True,
    'auto_install': False,
    'application': True,
}
