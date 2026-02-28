{
    'name': 'DICS Portal Schedule Meeting',
    'version': '19.0.0.5',
    'description': "dics_portal_schedule_meeting",
    'company': 'DataInteger Consultancy Services LLP',
    'website': 'https://www.datainteger.com',
    'depends': ['calendar', 'hr', 'website'],
    "license" : "OPL-1",
    'data': [
        'data/website_calendar_data.xml',
        'data/website_data.xml',
        # 'views/calender_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            # 'dics_portal_schedule_meeting/static/src/scss/portal_schedule_meeting.scss',
            'dics_portal_schedule_meeting/static/src/js/portal_schedule_meeting.js',
        ],

    }
}
