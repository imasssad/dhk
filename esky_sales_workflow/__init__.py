from . import models
from odoo import api, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env['ir.rule'].search([('name', '=', 'res.partner.rule.private.employee')])
    rule.write({'groups': [(6,0, [env.ref('base.group_user').id])]})
