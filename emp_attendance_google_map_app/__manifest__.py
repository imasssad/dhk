# -*- coding: utf-8 -*-

{
    "name" : "Employee Attendance Location with Google Map",
    "author": "Edge Technologies",
    "version" : "19.0.1.0",
    "images":["static/description/main_screenshot.png"],
    'live_test_url': "https://youtu.be/xZS-m_G3cqg",
    'summary': 'Apps helps Employee Attendance with Google Map Employee Attendance with Map employee location employee google map location of attendance sign in location find location of employee user location sign in location of sign in employee location sign in sign out',
    "description": """
    
    This app helps to track employee login location with google maps.
Odoo 12 Employee Attendance Map
employee loction attendance location employee map location employee google map location of attendance Store Employee Attendance details
check in location employee check in location employee store location check employee location find location of employee check location of employee employee location sales team location user location check in location location of sign in  

    
    """,
    "license" : "OPL-1",
    "depends" : ['base','web','hr','hr_attendance','website_sale'],
    "data": [
        'security/ir.model.access.csv',
        'views/employee_map_attendance_view.xml',
    ],
    'external_dependencies' : {
        'python' : ['googlegeocoder','googlemaps', 'geopy'],
    },
    "auto_install": False,
    "installable": True,
    "price": 15,
    "currency": 'EUR',
    "category" : "Website",
    'assets': {
        'web.assets_frontend': [
            'emp_attendance_google_map_app/static/src/css/gmaps.css',
            ],
        'web.assets_backend': [
            'emp_attendance_google_map_app/static/src/js/gmaps.js',
            'emp_attendance_google_map_app/static/src/js/my_attendances_extend.js',
            ], 
        'web.assets_qweb': [
            'website_sale/static/src/xml/*.xml',
        ],       
        },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
