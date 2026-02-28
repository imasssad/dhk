from odoo import fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="P&L", domain=[('sale_sheet', '=', True)])

    def open_import_wizard(self):
        view = self.env.ref('esky_sales_import_utility.import_data_wizard_views')
        wiz = self.env['import.sale.lines'].sudo().create({'sale_id': self.id})
        return {
            'name': _('Import P&L Sheet'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.sale.lines',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }