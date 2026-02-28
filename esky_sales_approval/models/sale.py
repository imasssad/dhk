from odoo import api, fields, models, _

from odoo.exceptions import UserError


@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('waiting_for_approval_to_send', 'Waiting for approval to send'),
        ('waiting_for_approval_to_confirm', 'Waiting for approval to confirm'),
        ('approved_to_sent', 'Approved to sent'),
        ('refused_to_send', 'Rejected'),
        ('refused_to_confirm', 'Rejected'),
        ('sale',),
    ])
    lang = fields.Selection(_lang_get, string='Language',
                            help="All the emails and documents sent to this contact will be translated in this language.")
    sales_director_send_approve = fields.Boolean("Sales Director Approved To Send", copy=False)
    technical_head_send_approve = fields.Boolean("Technical Head Approved To Send", copy=False)
    accounting_manager_send_approve = fields.Boolean("Financial Team Approved To Send", copy=False)
    sales_director_approve = fields.Boolean("Sales Director Approved", copy=False)
    technical_head_approve = fields.Boolean("Technical Head Approved", copy=False)
    accounting_manager_approve = fields.Boolean("Financial Team Approved", copy=False)
    sales_operation_approve = fields.Boolean("Sales Operation Approved", copy=False)
    procurement_manager_approve = fields.Boolean("Procurement Manager Approved", copy=False)
    approval_ids = fields.One2many('send.approval.workflow', 'sale_order_id', copy=False)
    confirm_approval_ids = fields.One2many('confirm.approval.workflow', 'sale_order_id', copy=False)
    required_attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Required Documents", copy=False, domain=[('required_documents', '=', True)])

    can_import_pl_sheet = fields.Boolean(compute='compute_can_import_pl_sheet')

    def compute_can_import_pl_sheet(self):
        for record in self:
            current_company_id = self.env.context.get('allowed_company_ids')[0]
            company_id = self.env['res.company'].browse(current_company_id)
            if company_id.priority_company == 2 or company_id.priority_company == 4:
                record.can_import_pl_sheet = True
            else:
                record.can_import_pl_sheet = False

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'approved_to_sent').with_context(tracking_disable=True).write({'state': 'sent'})
        return super(SaleOrder, self.with_context(mail_post_autofollow=self.env.context.get('mail_post_autofollow', True))).message_post(**kwargs)

    def send_approval(self):
        template = self.env.ref('esky_sales_approval.mail_template_approval_to_send')
        send_to = self.env['res.users'].search(['|', ('role', 'in', ['sales_director', 'technical_head']), ('id', '=', self.account_manager.id)])
        # for user in send_to:
        #     email_values = {
        #         'email_cc': False,
        #         'auto_delete': True,
        #         'recipient_ids': [],
        #         'partner_ids': [],
        #         'scheduled_date': False,
        #         'email_to': user.email
        #     }
        #     channel = self.env['mail.channel'].channel_get([user.partner_id.id])
        #     channel_id = self.env["mail.channel"].browse(channel["id"])
        #     channel_id.message_post(body="Your approval is needed to send the quotation %s." % self.name, message_type='comment', subtype_xmlid='mail.mt_comment')
        #     if self.env['ir.mail_server'].sudo().search([]):
        #         with self.env.cr.savepoint():
        #             force_send = not(self.env.context.get('import_file', False))
        #             template.send_mail(self.id, force_send=force_send, raise_exception=True, email_values=email_values)
        self.state = 'waiting_for_approval_to_send'
        if self.approval_ids:
            self.approval_ids = [(5, 0)]

    def send_email_to_sale_person(self, type):
        template = self.env.ref('esky_sales_approval.mail_template_quotation_approval')
        if type=="refused":
            template = self.env.ref('esky_sales_approval.mail_template_quotation_refused')

        if template:
            email_values = {
                'email_cc': False,
                'auto_delete': True,
                'recipient_ids': [],
                'partner_ids': [],
                'scheduled_date': False,
                'email_to': self.user_id.email
            }
            template.send_mail(self.id, force_send=False, raise_exception=True, email_values=email_values)

    def approved_to_sent(self):
        vals = [(0, 0, {'status_by': self.env.user.id, 'status': 'approved', 'status_date': fields.Datetime.now(), 'sale_order_id': self.id})]
        if self.env.user.role == 'sales_director':
            self.sales_director_send_approve = True
            self.approval_ids = vals
        if self.env.user.role == 'technical_head':
            self.technical_head_send_approve = True
            self.approval_ids = vals
        if self.env.user.role == 'accounting_manager':
            if self.accounting_manager_send_approve:
                raise UserError(_("Already approved by Finance"))
            self.accounting_manager_send_approve = True
            self.approval_ids = vals
        if all([self.sales_director_send_approve,self.technical_head_send_approve,self.accounting_manager_send_approve]):
            self.state = 'approved_to_sent'
        self.message_post(body=_("Approved by " + self.env.user.name), message_type='comment',
                          subtype_xmlid='mail.mt_note')
        self.send_email_to_sale_person("approved")

    def approved_to_confirm(self):
        vals = [(0, 0, {'status_by': self.env.user.id, 'status': 'approved', 'status_date': fields.Datetime.now(), 'sale_order_id': self.id})]
        if self.env.user.role == 'sales_director':
            self.sales_director_approve = True
            self.confirm_approval_ids = vals
        if self.env.user.role == 'technical_head':
            self.technical_head_approve = True
            self.confirm_approval_ids = vals
        if self.env.user.role == 'accounting_manager':
            if self.accounting_manager_approve:
                raise UserError(_("Already approved by Finance"))
            self.accounting_manager_approve = True
            self.confirm_approval_ids = vals
        if self.env.user.role == 'sales_operation':
            self.sales_operation_approve = True
            self.confirm_approval_ids = vals
        if self.env.user.role == 'procurement_manager':
            self.procurement_manager_approve = True
            self.confirm_approval_ids = vals
        self.message_post(body=_("Approved by "+self.env.user.name),message_type='comment',
                              subtype_xmlid='mail.mt_note')
        if all([self.sales_director_approve,self.technical_head_approve,self.accounting_manager_approve,self.sales_operation_approve,self.procurement_manager_approve]):
            self.action_confirm()

    def refused_to_sent_wizard(self):
        if self.state in ['refused_to_send','refused_to_confirm']:
            raise UserError(_("Already Rejected"))

        view = self.env.ref('esky_sales_approval.rejection_reason_wizard_view_form')
        wiz = self.env['reject.reason.wizard'].sudo().create({})
        return {
            'name': _('Reject Quotation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reject.reason.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }
    
    def refused_to_sent(self, vals):
        if self.state == 'waiting_for_approval_to_send':
            if self.approval_ids:
                self.approval_ids = [(5, 0)]
            self.state = 'refused_to_send'
            values = [(0, 0, vals)]
            self.approval_ids = values
            self.sales_director_send_approve = False
            self.technical_head_send_approve = False
            self.accounting_manager_send_approve = False
            self.send_email_to_sale_person("refused")
        elif self.state == 'waiting_for_approval_to_confirm':
            if self.confirm_approval_ids:
                self.confirm_approval_ids = [(5, 0)]
            self.state = 'refused_to_confirm'
            values = [(0, 0, vals)]
            self.confirm_approval_ids = values
            self.sales_director_approve = False
            self.technical_head_approve = False
            self.sales_operation_approve = False
            self.accounting_manager_approve = False
            self.procurement_manager_approve = False
            self.send_email_to_sale_person("refused")

    def _action_cancel(self):
        result = super(SaleOrder, self)._action_cancel()
        return self.write({'approval_ids': [(5, 0)]})

    def button_confirm(self):
        self.sudo().action_confirm()
        # view = self.env.ref('esky_sales_approval.import_documents_wizard_views')
        # wiz = self.env['import.sales.documents'].sudo().create({})
        # return {
        #     'name': _('Upload Documents'),
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'import.sales.documents',
        #     'views': [(view.id, 'form')],
        #     'view_id': view.id,
        #     'target': 'new',
        #     'res_id': wiz.id,
        #     'context': self.env.context,
        # }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    start_date = fields.Date()
    end_date = fields.Date()
    brand = fields.Char(string="Vendor")