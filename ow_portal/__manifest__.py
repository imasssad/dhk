# -*- coding: utf-8 -*-
# Copyright 2020 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Metro Style Portal Page',
    'summary': 'Metro Style Website User Portal Page',
    'version': '19.0.1.0',
    'category': 'Website',
    'summary': """
Give Odoo website portal a Metro style look
""",
    'author': "Openworx",
    'website': 'https://www.openworx.nl',
    'license': 'LGPL-3',
    'depends': [],
    'data': [
        # 'views/assets.xml',
        'views/portal.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/ow_portal/static/src/scss/style.scss'
        ],
    },
    'images': ['images/image.png'],
    'installable': True,
    'application': False,
}
