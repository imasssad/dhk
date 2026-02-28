from odoo import fields, models

class WizardMessage(models.TransientModel):
    _name = "wizard.message"
    _description = 'Wizard message after uploading data successfully'
    
    text = fields.Text('Message')

    def close_wizard(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'  
        }
