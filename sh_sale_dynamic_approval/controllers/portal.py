# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo.addons.sale.controllers.portal import CustomerPortal

class ShCustomerPortal(CustomerPortal):
    
    def _prepare_orders_domain(self, partner):
        """
        This function prepares a domain for orders based on the state and includes 'sale',
        'waiting_for_approval', and 'done' states.
        """
        res = super()._prepare_orders_domain(partner)
        domain = list(('state','in',['sale','waiting_for_approval','done']) if i[0]== 'state' else i for i in res)
        return domain
