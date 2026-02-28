# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order'

    current_company_name = fields.Many2one("res.company", 
                                            string="Current Company", 
                                            compute="compute_current_company", 
                                            store=False)
    is_esky = fields.Boolean("Is Esky", compute="compute_is_esky")
    contact_person = fields.Char("Contact Person")
    project_ref = fields.Char("Project Ref")
    bill_to_contact = fields.Char("Contact Person")
    bill_to_email = fields.Char("Email")
    bill_to_address = fields.Char("Address")
    bill_to_phone = fields.Char("Phone")
    ship_to_contact = fields.Char("Contact Person")
    ship_to_email = fields.Char("Email")
    ship_to_address = fields.Char("Address")
    ship_to_phone = fields.Char("Phone")
    requistioner = fields.Char("Requistioner")
    delivery = fields.Char("Delivery")
    payment = fields.Char("Payment Terms")
    add_account_name = fields.Char("Account Name")
    add_account_no = fields.Char("Account No.")
    add_currency = fields.Char("Currency")
    add_bank_name = fields.Char("Bank Name")
    add_iban_swift = fields.Char("Swift & IBAN")
    show_unit_price = fields.Boolean("Unit Price", default=True)
    
    def compute_is_esky(self):
        for record in self:
            current_company_id = self.env.context.get('allowed_company_ids')[0]
            company_id = self.env['res.company'].browse(current_company_id)
            if company_id.priority_company == 2:
                record.is_esky = True
            else:
                record.is_esky = False

    def compute_current_company(self):
        companyId = self.env.context.get('allowed_company_ids')[0]
        company_obj = self.env['res.company'].search([('id', '=', companyId)])
        self.current_company_name = company_obj.id
        report = self.env['ir.actions.report'].sudo().browse(self.env.ref('sale.action_report_pro_forma_invoice').id)
        if company_obj.priority_company == 1:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_sales_report.paperformat_portrait_quotation').id)            
        else:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_sales_report.paperformat_base_report').id)
        report.sudo().write({'paperformat_id': paper_format.id})

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    part_number = fields.Char("Part Number")

    # Will remove when push to production
    price_cost = fields.Float("Cost")

class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

    priority_company = fields.Integer(string="Priority")

