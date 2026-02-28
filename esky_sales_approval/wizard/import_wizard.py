from odoo import fields,models, _
from odoo.exceptions import ValidationError

class ImportSalesDocuments(models.TransientModel):
    _name="import.sales.documents"
    _description = 'Import Vendor Quotation and Customer PO'

    vendor_quotation = fields.Binary("Vendor Quotation")
    customer_po = fields.Binary("Customer PO")
    vendor_quotation_name = fields.Char("File Name")
    customer_po_name = fields.Char("File Name 2")
    
    def read_documents(self):
        if not all([self.vendor_quotation,self.customer_po]):
            raise ValidationError(_("Kindly upload both documents."))
        attachment_obj = self.env["ir.attachment"]
        vals = [{"name": self.vendor_quotation_name, "datas": self.vendor_quotation, "required_documents": True, "res_id": self._context.get("active_id"), "res_model": "sale.order"},
                {"name": self.customer_po_name, "datas": self.customer_po, "required_documents": True, "res_id": self._context.get("active_id"), "res_model": "sale.order"}]
        attachment_obj.sudo().create(vals)
        sale_obj = self.env['sale.order'].browse(self._context.get("active_id"))
        # sale_obj.sudo().write({'state': 'waiting_for_approval_to_confirm'})
        sale_obj.sudo().action_confirm()

    def data_upload(self):
        wb = self.read_documents()
        sale_obj = self.env['sale.order'].browse(self._context.get("active_id"))
        template = self.env.ref('esky_sales_approval.mail_template_approval_to_confirm')
        send_to = self.env['res.users'].search(['|', ('role', 'in', ['sales_director', 'technical_head', 'sales_operation', 'procurement_manager']),('id', '=', sale_obj.account_manager.id)])
        for user in send_to:
            email_values = {
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
                'email_to': user.email
            }
            channel = self.env['mail.channel'].channel_get([user.partner_id.id])
            channel_id = self.env["mail.channel"].browse(channel["id"])
            channel_id.message_post(body="Vendor Quotation and Customer PO is uploaded on %s and your approval is needed to confirm the quotation." % sale_obj.name, message_type='comment', subtype_xmlid='mail.mt_comment')
            if self.env['ir.mail_server'].sudo().search([]):
                with self.env.cr.savepoint():
                    force_send = not(self.env.context.get('import_file', False))
                    template.send_mail(sale_obj.id, force_send=force_send, raise_exception=True, email_values=email_values)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'  
        }
