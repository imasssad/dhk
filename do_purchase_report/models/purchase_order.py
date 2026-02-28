# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import groupby
import json


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    sale_order_number = fields.Char()
    customer_id = fields.Many2one('res.partner')

    vendor_from_sale = fields.Char(string="Vendor", compute="_compute_vendor_from_sale", store=True)



    current_company_name = fields.Many2one("res.company", 
                                            string="Current Company", 
                                            compute="compute_current_company", 
                                            store=False)
    contact_person = fields.Char("Contact Person")

    ship_to = fields.Html()
    bill_to = fields.Html()
    end_user_detail = fields.Html()

    ship_bill_to_contact = fields.Char("Name")
    ship_bill_to_email = fields.Char("Email")
    ship_bill_to_address = fields.Char("Address")
    ship_bill_to_phone = fields.Char("Phone")

    distributor_to_contact = fields.Char("Name")
    distributor_to_email = fields.Char("Email")
    distributor_to_address = fields.Char("Address")
    distributor_to_phone = fields.Char("Phone")

    end_user_to_name = fields.Char("End User Name")
    end_user_to_contact = fields.Char("Contact Person")
    end_user_to_email = fields.Char("Email")
    end_user_to_phone = fields.Char("Phone")

    requistioner = fields.Char("Requistioner")
    delivery = fields.Text("Delivery")
    payment = fields.Text("Payment Terms")

    add_account_name = fields.Char("Account Name")
    add_account_no = fields.Char("Account No.")
    add_currency = fields.Char("Currency")
    add_bank_name = fields.Char("Bank Name")
    add_iban_swift = fields.Char("Swift & IBAN")

    def compute_current_company(self):
        companyId = self.env.context.get('allowed_company_ids')[0]
        company_obj = self.env['res.company'].search([('id', '=', companyId)])
        self.current_company_name = company_obj.id
        report = self.env['ir.actions.report'].sudo().browse(self.env.ref('purchase.report_purchase_quotation').id)
        if company_obj.priority_company == 1:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_purchase_report.paperformat_purchase_report').id)
        elif company_obj.priority_company == 0:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_purchase_report.paperformat_purchase_report').id)
        else:
            paper_format = self.env['report.paperformat'].sudo().browse(self.env.ref('do_sales_report.paperformat_base_report').id)
        report.sudo().write({'paperformat_id': paper_format.id})



    @api.depends('order_line.sale_line_id')
    def _compute_vendor_from_sale(self):
        """Compute vendor based on Sale Order Lines."""
        for po in self:
            sale_order_lines = po.order_line.mapped('sale_line_id')
            brands = sale_order_lines.mapped('brand')  # Fetch all unique brands
            
            if brands:
                po.vendor_from_sale = brands[0]  # Assign first brand
                print(f"✅ Computed Vendor: {brands[0]} for PO {po.name}")
                
    @api.model_create_multi
    def create(self, vals_list):
        orders = self.browse()
        for vals in vals_list:
            print(vals)
            year = fields.Datetime.now().strftime("%Y")
            print("PO VALS", vals)
            p_id = vals['partner_id']
            partner = self.env['res.partner'].search([('id', '=', p_id)])
            vendor = partner.name.split()[0]
            category = None
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])


            # Ensures default picking type and currency are taken from the right company.
            self_comp = self.with_company(company_id)
            if 'order_line' in vals:
                order_lines = vals['order_line']
                print("OL", order_lines)
                if order_lines and isinstance(order_lines, list) and len(order_lines) > 0:
                    product_info = order_lines[0][2]
                    if 'product_id' in product_info:
                        product = self.env['product.product'].search([('id', '=', product_info['product_id'])])
                        if product.categ_id:
                            category = product.categ_id.display_name

                parts = ''
                if category:
                    parts = category.split(" / ")
                if len(parts) >= 3:
                    parts = parts[1]
                else:
                    parts = ''


                if vals.get('name', 'New') == 'New':
                    seq_date = None
                    if 'date_order' in vals:
                        seq_date = fields.Datetime.context_timestamp(self,
                                                                     fields.Datetime.to_datetime(vals['date_order']))
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order',
                                                                             sequence_date=seq_date) or '/'
                    vals['name'] = vals['name'][2:] + '/' + str(year) + '/' + vendor + '/' + parts
                    print("", vals['name'])
            orders |= super(PurchaseOrder, self_comp).create(vals)

        return orders

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    serial_number = fields.Text()
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        line_description = ''
        if values.get('product_description_variants'):
            line_description = values['product_description_variants']
        supplier = values.get('supplier')
        res = self._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, supplier, po)
        # We need to keep the vendor name set in _prepare_purchase_order_line. To avoid redundancy
        # in the line name, we add the line_description only if different from the product name.
        # This way, we shoud not lose any valuable information.
        if line_description and product_id.name != line_description:
            res['name'] += '\n' + line_description
        res['date_planned'] = values.get('date_planned')
        res['move_dest_ids'] = [(4, x.id) for x in values.get('move_dest_ids', [])]
        res['orderpoint_id'] = values.get('orderpoint_id', False) and values.get('orderpoint_id').id
        res['propagate_cancel'] = values.get('propagate_cancel')
        res['product_description_variants'] = values.get('product_description_variants')
        res['sale_line_id'] = values.get('sale_line_id')

        # Add dates from sale order line if available
        if values.get('sale_line_id'):
            sale_line = self.env['sale.order.line'].browse(values['sale_line_id'])
            res.update({
                'start_date': sale_line.start_date,
                'end_date': sale_line.end_date
            })
        return res

    @api.model
    def create(self, vals):
        if 'sale_line_id' in vals and 'order_id' in vals:
            sale_line = self.env['sale.order.line'].search([('id', '=', vals['sale_line_id'])])
            vals.update({
            'start_date': vals.get('start_date', sale_line.start_date),
            'end_date': vals.get('end_date', sale_line.end_date)
            })
            po = self.env['purchase.order'].search([('id', '=', vals['order_id'])])
            if sale_line:
                if sale_line.order_id.analytic_account_id:
                    if not 'analytic_distribution' in vals:
                        ad = { str(sale_line.order_id.analytic_account_id.id): 100}
                        vals['analytic_distribution'] = ad

                vals['price_unit'] = sale_line.purchase_price
                vals['taxes_id'] = sale_line.tax_id
                po.currency_id = sale_line.order_id.currency_id.id

                year = fields.Datetime.now().strftime("%Y")

                category = ''

                if sale_line.product_id.categ_id:
                    category = sale_line.product_id.categ_id.display_name

                parts = ''
                if category:
                    parts = category.split(" / ")
                if len(parts) >= 3:
                    parts = parts[1]
                else:
                    parts = ''

                if sale_line.brand:
                    parts = sale_line.brand

                

                vendor = sale_line.vendor_id.name
                name = po.name
                if name[:1] == 'P':
                    name = name[1:] + '/' + str(year) + '/' + vendor + '/' + parts

                    po.name = name
        print("LB", vals)
        return super(PurchaseOrderLine, self).create(vals)

    # def write(self,vals):
    #     if 'price_unit' in vals:
    #         self.sale_line_id.purchase_price = vals['price_unit']
    #
    #     return super(PurchaseOrderLine, self).write(vals)
    def write(self, vals):
        if 'sale_line_id' in vals:
            sale_line = self.env['sale.order.line'].browse(vals['sale_line_id'])
            vals.update({
                'start_date': sale_line.start_date,
                'end_date': sale_line.end_date
            })
        return super(PurchaseOrderLine, self).write(vals)


class StockMove(models.Model):
    _inherit = 'stock.move'

    serial_number = fields.Text()

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_backorder(self):
        """ This method is called when the user chose to create a backorder. It will create a new
        picking, the backorder, and move the stock.moves that are not `done` or `cancel` into it.
        """
        backorders = self.env['stock.picking']
        bo_to_assign = self.env['stock.picking']
        for picking in self:
            moves_to_backorder = picking.move_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            if moves_to_backorder:
                backorder_picking = picking.copy({
                    'name': '/',
                    'move_ids': [],
                    'move_line_ids': [],
                    'backorder_id': picking.id
                })
                backorder_picking.move_ids = None
                moves_to_backorder.write({'picking_id': backorder_picking.id})
                moves_to_backorder.move_line_ids.package_level_id.write({'picking_id':backorder_picking.id})
                moves_to_backorder.mapped('move_line_ids').write({'picking_id': backorder_picking.id})
                backorders |= backorder_picking

                picking.message_post(
                    body=_('The backorder %s has been created.', backorder_picking._get_html_link())
                )
                if backorder_picking.picking_type_id.reservation_method == 'at_confirm':
                    bo_to_assign |= backorder_picking
        if bo_to_assign:
            bo_to_assign.action_assign()
        return backorders


class StockRule(models.Model):
    _inherit = 'stock.rule'


    @api.model
    def _run_buy(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        errors = []
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])

            supplier = False
            if procurement.values.get('supplierinfo_id'):
                supplier = procurement.values['supplierinfo_id']
            elif procurement.values.get('orderpoint_id') and procurement.values['orderpoint_id'].supplier_id:
                supplier = procurement.values['orderpoint_id'].supplier_id
            else:
                supplier = procurement.product_id.with_company(procurement.company_id.id)._select_seller(
                    partner_id=procurement.values.get("supplierinfo_name"),
                    quantity=procurement.product_qty,
                    date=max(procurement_date_planned.date(), fields.Date.today()),
                    uom_id=procurement.product_uom)

            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                          procurement.product_id.display_name)
                errors.append((procurement, msg))

            partner = supplier.partner_id
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        if errors:
            raise ProcurementException(errors)

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            # if not po:  # For Every SO there will be new PO
            positive_values = [p.values for p in procurements if
                               float_compare(p.product_qty, 0.0, precision_rounding=p.product_uom.rounding) >= 0]
            if positive_values:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(company_id, origins, positive_values)
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.
                # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
                # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
                po = self.env['purchase.order'].with_company(company_id).with_user(SUPERUSER_ID).create(vals)
            # else:
            #     # If a purchase order is found, adapt its `origin` field.
            #     if po.origin:
            #         missing_origins = origins - set(po.origin.split(', '))
            #         if missing_origins:
            #             po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
            #     else:
            #         po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(
                po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id),
                key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*po_lines)
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                                                            procurement.product_qty, procurement.product_uom,
                                                            company_id,
                                                            procurement.values, po_line)
                    po_line.sudo().write(vals)
                else:
                    if float_compare(procurement.product_qty, 0,
                                     precision_rounding=procurement.product_uom.rounding) <= 0:
                        # If procurement contains negative quantity, don't create a new line that would contain negative qty
                        continue
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].partner_id
                    po_line_values.append(self.env['purchase.order.line']._prepare_purchase_order_line_from_procurement(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
                    # Check if we need to advance the order date for the new line
                    order_date_planned = procurement.values['date_planned'] - relativedelta(
                        days=procurement.values['supplier'].delay)
                    if fields.Date.to_date(order_date_planned) < fields.Date.to_date(po.date_order):
                        po.date_order = order_date_planned
            self.env['purchase.order.line'].sudo().create(po_line_values)