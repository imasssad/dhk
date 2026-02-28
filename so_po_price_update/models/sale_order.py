from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_export_related_po(self):
        """Export all related PO lines to Excel"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Export Related Purchase Orders',
            'res_model': 'po.price.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_action_type': 'export'
            }
        }
    
    def action_import_po_prices(self):
        """Import updated PO prices from Excel"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import PO Price Updates',
            'res_model': 'po.price.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_action_type': 'import'
            }
        }
