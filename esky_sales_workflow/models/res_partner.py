from odoo import api, fields, models, _
from odoo.exceptions import MissingError


class ResPartner(models.Model):
    _inherit = "res.partner"

    presales = fields.Many2many('res.users', string='Presales')
    account_manager = fields.Many2one('res.users', string='Accounts Manager')
    second_sale_person = fields.Many2one('res.users')

    @api.model_create_multi
    def create(self, vals_list):
        template = self.env.ref('esky_sales_workflow.mail_template_customer_creation')
        presale_template = self.env.ref('esky_sales_workflow.mail_template_assign_presale')
        sales_director = self.env['res.users'].search([('role', '=', 'sales_director')], limit=1)
        technical_head = self.env['res.users'].search([('role', '=', 'technical_head')], limit=1)
        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
            'email_to': sales_director.email
        }
        customers = super(ResPartner, self).create(vals_list)
        for customer in customers:
            if customer.customer_rank:
                if not sales_director:
                    raise MissingError(_("Please assign a sales director in users."))
                if not technical_head:
                    raise MissingError(_("Please assign a technical head in users."))
                channel = self.env['mail.channel'].channel_get([sales_director.partner_id.id])
                director_created_channel_id = self.env["mail.channel"].browse(channel["id"])
                director_created_channel_id.message_post(body="New Customer %s is created please assign salesperson to it." % customer.name, message_type='comment', subtype_xmlid='mail.mt_comment')
                if self.env['ir.mail_server'].sudo().search([]):
                    with self.env.cr.savepoint():
                        force_send = not(self.env.context.get('import_file', False))
                        template.send_mail(customer.id, force_send=force_send, raise_exception=True, email_values=email_values)
                if customer.user_id:
                    tech_channel = self.env['mail.channel'].channel_get([technical_head.partner_id.id])
                    technical_channel_id = self.env["mail.channel"].browse(tech_channel["id"])
                    technical_channel_id.message_post(body="Salesperson has been assigned to new Customer %s please assign presale to it." % customer.name, message_type='comment', subtype_xmlid='mail.mt_comment')
                    if self.env['ir.mail_server'].sudo().search([]):
                        with self.env.cr.savepoint():
                            email_values['email_to'] = technical_head.email
                            presale_template.send_mail(customer.id, force_send=force_send, raise_exception=True, email_values=email_values)
        return customers

    def write(self, vals):
        if vals.get('user_id') and self.customer_rank:
            template = self.env.ref('esky_sales_workflow.mail_template_assign_presale')
            technical_head = self.env['res.users'].search([('role', '=', 'technical_head')], limit=1)
            email_values = {
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
                'email_to': technical_head.email
            }
            tech_channel = self.env['mail.channel'].channel_get([technical_head.partner_id.id])
            technical_channel_id = self.env["mail.channel"].browse(tech_channel["id"])
            technical_channel_id.message_post(body="Salesperson has been assigned to new Customer %s please assign presale to it." % self.name, message_type='comment', subtype_xmlid='mail.mt_comment')
            if self.env['ir.mail_server'].sudo().search([]):
                with self.env.cr.savepoint():
                    force_send = not(self.env.context.get('import_file', False))
                    template.send_mail(self.id, force_send=force_send, raise_exception=True, email_values=email_values)
        if not self.parent_id and 'user_id' in vals:
            for child in self.child_ids:
                child.update({'user_id': vals.get('user_id')})
        return super(ResPartner, self).write(vals)
