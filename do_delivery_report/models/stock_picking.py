# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    current_company_name = fields.Many2one("res.company", 
                                            string="Current Company", 
                                            compute="compute_current_company", 
                                            store=False)

    def compute_current_company(self):
        companyId = self.env.context.get('allowed_company_ids')[0]
        company_obj = self.env['res.company'].search([('id', '=', companyId)])
        self.current_company_name = company_obj.id
        report = self.env['ir.actions.report'].sudo().browse(self.env.ref('stock.action_report_delivery').id)
        if company_obj.priority_company == 1:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_delivery_report.paperformat_delivery_report').id)            
        else:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_sales_report.paperformat_base_report').id)
        report.sudo().write({'paperformat_id': paper_format.id})


