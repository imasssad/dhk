# -*- coding: utf-8 -*-
{
    'name': "Employee Birthday Remainder",
    'version': '16.0.1',
    'category': 'HR',
    'website': 'www.digitztech.com',
    'summary': "Arrange employee birthdays in ascending order by date. Ensure you never overlook an employee's birthday moving forward.",
    'description': "Arrange employee birthdays in ascending order by date. Ensure you never overlook an employee's birthday moving forward.",
    'depends': ['base', 'hr'],
    "data": ['security/security.xml'],
    'author': 'Digitz Technologies',
    'assets': {'web.assets_backend': ['dgz_birthday_reminder/static/src/**/*']},
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
    'license': 'LGPL-3',
    'images': ['static/description/thumbnail.gif'],
}
