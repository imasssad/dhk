from odoo import api, fields, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    def get_application_groups(self, domain):
        category_id = self.env.ref('esky_sales_workflow.module_category_esky_sales')
        groups_id = self.search([('category_id', '=', category_id.id)])
        return super(ResGroups, self).get_application_groups(domain + [('id', 'not in', groups_id.ids)])