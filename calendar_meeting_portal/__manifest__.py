# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': "Portal for Calendar Meetings for Attendees",
    'version': '19.0.5.2.6',
    'license': 'Other proprietary',
    'price': 39.0,
    'currency': 'EUR',
    'summary':  """Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees""",
    'description': """
Calendar Meeting Show to Attendees Portal Users / Portal for Calendar Meetings for Attendees
This app allows your attendees to view meetings on my account portal
of your website and send a message using portal login. 
Portal for Calendar Meetings for Attendees
Calendar Meeting Show to Attendees Portal Users
Allow your portal users attendees to view all the calendar meetings where they are set as attendees.
They can also send a message from the list and form a view of the portal as shown.
Portal for Calendar Meetings for Attendees
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'images': ['static/description/image.png'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/calendar_meeting_portal/1018',#'https://youtu.be/kuh2AWBuT8U',
    'category': 'Productivity/Calendar',
    'depends': ['calendar','portal'],
    'data': [
            'views/customer_calendar_template.xml',
            'views/calendar_portal_templates.xml',
            ],
    'assets': {
        'web.assets_frontend': [
            '/calendar_meeting_portal/static/src/js/calendar_comment.js',
            '/calendar_meeting_portal/static/src/js/counter.js',
        ],
    },
    'installable': True,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
