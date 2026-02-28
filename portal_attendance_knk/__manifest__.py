# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>). 

{
    'name': 'Portal Employee Attendance',
    'version': '19.0.1.0',
    'summary': 'Portal Attendance Using this module user can see their attendance and also mark their attendance from portal as well.| Portal attendance | Portal Attendance filter | Portal Attendance groupby | Online Attendance | Portal attendance list | Website Attendance | Employee attendance | Website employee | Employee attendance | Employee Check In | Employee Checkout | Mobile attendance | Attendance Kiosk',
    'description': "Employee can see their attendance.Using filters Employee can easily find the attendance.Employee can also search the attendance.",
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://www.kanakinfosystems.com',
    'category': 'Human Resources/Attendances',
    'depends': ['portal', 'hr_attendance', 'portal_hr_knk', 'sh_hr_attendance_geolocation'],
    'data': [
        'security/hr_security.xml',
        'views/knk_res_config_view.xml',
        'views/pwa.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'portal_attendance_knk/static/src/scss/custom.scss',
            'portal_attendance_knk/static/src/js/custom.js'
        ],
        'web.assets_backend': [
            'portal_attendance_knk/static/src/js/pwa_install.js'
        ],
    },
    'qweb': ["static/src/xml/pwa_install.xml"],
    'images': ['static/description/banner.gif'],
    'application': True,
}
