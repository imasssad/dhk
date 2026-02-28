# Purchase Line Taxes Module

## Description
This Odoo 16 module allows you to change taxes for all lines in a Request for Quotation (RFQ) or Purchase Order at once from the header level, similar to the sales order line_taxes module.

## Features
- Add purchase taxes at the purchase order header level
- Automatically apply selected taxes to all purchase order lines
- Domain filter ensures only purchase taxes are selectable
- Compatible with Odoo 16 Enterprise on odoo.sh

## Installation

### For odoo.sh:
1. Upload the `purchase_line_taxes` folder to your custom addons directory in your odoo.sh repository
2. Push changes to your odoo.sh branch
3. Update the apps list in Odoo
4. Install the "Purchase Line Taxes" module

### Manual Installation:
1. Copy the `purchase_line_taxes` folder to your Odoo addons directory
2. Restart the Odoo server
3. Update the apps list (Apps menu → Update Apps List)
4. Search for "Purchase Line Taxes" and click Install

## Usage

1. Open any Request for Quotation (RFQ) or Purchase Order
2. You'll see a new "Purchase Taxes" field after the Payment Terms field
3. Select one or multiple taxes from the dropdown
4. All existing lines in the purchase order will automatically have their taxes updated
5. Any new lines added will need to have taxes set individually or you can update the "Purchase Taxes" field again

## Technical Details

### Module Structure:
```
purchase_line_taxes/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── controllers.py
├── models/
│   ├── __init__.py
│   └── purchase_order.py
├── security/
│   └── ir.model.access.csv
└── views/
    └── purchase_order_views.xml
```

### Key Components:
- **Model Extension**: Extends `purchase.order` with a `line_taxes` Many2many field
- **Domain Filter**: Only shows taxes with `type_tax_use = 'purchase'`
- **Onchange Method**: `_onchange_line_taxes()` updates all line taxes when header taxes change
- **View Inheritance**: Adds the taxes field to the purchase order form view

## Differences from Sales Module

Unlike the sales module which includes discount and vendor fields, this purchase module:
- ✅ Only includes taxes (no discount field as requested)
- ✅ Uses purchase taxes domain filter instead of sales taxes
- ✅ Updates `taxes_id` field on purchase.order.line (not `tax_id`)
- ✅ Inherits from purchase.order form view

## Version
- **Version**: 16.0.1.0.0
- **Odoo Version**: 16.0 Enterprise
- **License**: LGPL-3

## Author
MDS

## Support
For issues or questions, please contact the module author or your Odoo administrator.
