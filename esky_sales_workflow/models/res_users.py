from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    role = fields.Selection([
        ('sales_director', 'Sales Director'), 
        ('technical_head', 'Technical Head'),
        ('sales_operation', 'Sales Operation'),
        ('accounting_manager', 'Financial Team'),
        ('procurement_manager', 'Procurement Manager'),
        ('salesperson', 'Salesperson'),
        ('presales', 'Presales'),
        ], string='Role')

    @api.constrains('role')
    def _check_directors_managers(self):
        users = self.search([('id', '!=', self.id)])
        for user in users:
            if user.role == 'sales_director' and self.role == 'sales_director':
                raise ValidationError(_('Please deselect sales director from %s to make this one.' % user.name))
            if user.role == 'technical_head' and self.role == 'technical_head':
                raise ValidationError(_('Please deselect technical head from %s to make this one.' % user.name))
            if user.role == 'sales_operation' and self.role == 'sales_operation':
                raise ValidationError(_('Please deselect sales operation from %s to make this one.' % user.name))
            if user.role == 'procurement_manager' and self.role == 'procurement_manager':
                raise ValidationError(_('Please deselect procurement manager from %s to make this one.' % user.name))

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            if user.role == 'sales_director':
                group_id = self.env.ref('esky_sales_workflow.group_sales_director')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'technical_head':
                group_id = self.env.ref('esky_sales_workflow.group_technical_head')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'sales_operation':
                group_id = self.env.ref('esky_sales_workflow.group_sales_operation')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'accounting_manager':
                group_id = self.env.ref('esky_sales_workflow.group_accounting_manager')
                group_id.sudo().write({'users': [(4, user.id)]})
            if user.role == 'procurement_manager':
                group_id = self.env.ref('esky_sales_workflow.group_procurement_manager')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
        return users

    def write(self, vals):
        if vals.get('role') or vals.get('role') == False:
            for user in self:
                if user.role == 'sales_director':
                    group_id = user.env.ref('esky_sales_workflow.group_sales_director')
                    group_id.sudo().write({'users': [(5,)]})
                if user.role == 'technical_head':
                    group_id = user.env.ref('esky_sales_workflow.group_technical_head')
                    group_id.sudo().write({'users': [(5,)]})
                if user.role == 'sales_operation':
                    group_id = user.env.ref('esky_sales_workflow.group_sales_operation')
                    group_id.sudo().write({'users': [(5,)]})
                if user.role == 'accounting_manager':
                    group_id = user.env.ref('esky_sales_workflow.group_accounting_manager')
                    group_id.sudo().write({'users': [(3,user.id)]})
                if user.role == 'procurement_manager':
                    group_id = user.env.ref('esky_sales_workflow.group_procurement_manager')
                    group_id.sudo().write({'users': [(5,)]})
        result = super(ResUsers, self).write(vals)
        for user in self:
            if user.role == 'sales_director':
                group_id = user.env.ref('esky_sales_workflow.group_sales_director')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'technical_head':
                group_id = user.env.ref('esky_sales_workflow.group_technical_head')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'sales_operation':
                group_id = user.env.ref('esky_sales_workflow.group_sales_operation')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
            if user.role == 'accounting_manager':
                group_id = user.env.ref('esky_sales_workflow.group_accounting_manager')
                group_id.sudo().write({'users': [(4, user.id)]})
            if user.role == 'procurement_manager':
                group_id = user.env.ref('esky_sales_workflow.group_procurement_manager')
                group_id.sudo().write({'users': [(6, 0, [user.id])]})
        return result

    def get_selection_label(self, field_name):
        field = self._fields.get(field_name)
        if field and field.type == 'selection':
            return dict(field.selection).get(self[field_name])
        return None