{
    'name': "Esky Sales Workflow",
    'summary': """Complete sales workflow of esky.""",
    'author': "CBS EGYPT",
    'website': "https://cbsegypt.com",
    'category': 'Sales/Sales',
    'version': '19.0.1.0',
    'depends': ['base', 'mail', 'crm', 'sale', 'sales_team'],
    'data': [
        'security/ir.model.access.csv',
        'security/sales_groups.xml',
        'data/mail_template_data.xml',
        'data/channel_data.xml',
        'views/res_users_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
        'views/general_terms_views.xml'
    ],
    'uninstall_hook': 'uninstall_hook',
}
