from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    d_register = fields.Boolean("D Register")
    presales = fields.Many2many('res.users', string='Presales', compute='_compute_presales_contact_person', readonly=False, store=True)
    contact_person = fields.Many2one('res.partner', string='Contact', compute='_compute_presales_contact_person', readonly=False, store=True, domain="[('type', '=', 'contact'), ('parent_id', '=', partner_id), ('parent_id', '!=', False)]")
    usd_currency = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.USD'))

    @api.depends('partner_id')
    def _compute_presales_contact_person(self):
        contact_obj = self.env['res.partner']
        for lead in self:
            lead.presales = lead.partner_id.presales
            contact_person = contact_obj.search([('type', '=', 'contact'), ('parent_id', '=', lead.partner_id.id), ('parent_id', '!=', False)], limit=1)
            if contact_person:
                lead.contact_person = contact_person
            else:
                lead.contact_person = False

class SaleOrder(models.Model):
    _inherit = "sale.order"

    account_manager = fields.Many2one('res.users', string='Accounts Manager', related='partner_id.account_manager',store=True)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    account_manager = fields.Many2one(related='order_id.account_manager', string="Accounts Manager", store=True)
