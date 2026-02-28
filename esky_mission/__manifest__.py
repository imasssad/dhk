{
    'name': "Missions",
    'version': '1.0',
    'summary':  """Mission Show to Attendees Portal Users""",
    'author': "Suraj Rawat.",
    'category': 'Productivity/Calendar',
    'depends': ['portal','base','hr','sh_hr_attendance_geolocation', 'hr_payroll'],
    'data': [
            'wizard/mission_report_wizard_views.xml',
            'data/cron.xml',
            'data/salary_rule.xml',
            'security/ir_rule.xml',
            'security/ir.model.access.csv',
            'views/mission_views.xml',
            'views/mission_portal_templates.xml',
            'views/zone_rate_views.xml',
            ],
    'assets': {
        'web.assets_frontend': [
            '/esky_mission/static/src/js/counter.js'
        ],
    },
    'installable': True,
    'application': False,
}
