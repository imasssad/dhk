from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class GeneralTerms(models.Model):
    _name = 'general.terms'
    _description = 'General Terms and Disclaimer'

    name = fields.Char("GT Number")
    general_terms = fields.Html('General Terms')
    disclaimer = fields.Html('Disclaimer')
    default_gt = fields.Boolean('Default General Terms')

    @api.constrains('default_gt')
    def _check_directors_managers(self):
        gts = self.search([('id', '!=', self.id)])
        for gt in gts:
            if gt.default_gt and self.default_gt:
                raise ValidationError(_('Only one general terms can be default please deselect the previous one.'))