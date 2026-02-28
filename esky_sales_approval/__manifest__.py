{
    'name': "Esky Sales Approval",
    'summary': """Approval for send quotation and confirm quotation.""",
    'author': "CBS EGYPT",
    'website': "https://cbsegypt.com",
    'category': 'Sales/Sales',
    'version': '1.0',
    'depends': ['base', 'sale', 'esky_sales_workflow', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/channel_data.xml',
        'data/mail_template_data.xml',
        'views/sale_order_views.xml',
        'views/rejection_wizard.xml',
        'wizard/import_wizard_views.xml'
    ]
}
