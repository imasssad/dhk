
{
    'name': 'ERP ESKY',
    'version': '19.0.0.4',
    'author': 'DataInteger Consultancy Services LLP',
    'description': '',
    "license" : "OPL-1",
    'category': 'Extra Tools',
    'website': 'www.datainteger.com',
    'depends': ['base','hr_attendance','calendar','portal','sh_hr_attendance_geolocation','portal_attendance_knk'],
    'data': [
        'security/security.xml',
        'views/calendar_views.xml',
        'views/hr_attendance_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'erp_esky/static/src/js/custom.js',
            'erp_esky/static/src/js/meeting_attendance.js',
        ],
    },
    'qweb': [],
    'images': [],
    'license': 'OPL-1',
    'application': True,
}
