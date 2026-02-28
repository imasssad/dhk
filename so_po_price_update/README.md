# SO-PO Price Update Automation

## Description
This module provides automated workflow for exporting Purchase Orders related to Sales Orders, updating prices in Excel, and automatically reflecting the changes back in both PO and SO.

## Features
- Export all PO lines related to a Sales Order to Excel
- Update PO prices in Excel offline
- Import updated prices with one click
- Automatic cost update in Sales Order lines
- Automatic margin recalculation
- Detailed update summary and error reporting

## Installation
1. Copy this module to your Odoo addons directory
2. Update the apps list: Settings → Apps → Update Apps List
3. Search for "SO-PO Price Update Automation"
4. Click Install

## Dependencies
- sale_management
- purchase
- sale_purchase

## Usage

### Export Process
1. Open a confirmed Sales Order
2. Click the "Export Related POs" button in the header
3. Click "Export PO Lines" in the wizard
4. Click "Download File" to get the Excel file

### Update Process
1. Open the downloaded Excel file
2. Modify prices in the "Updated Unit Price" column (Column J)
3. Save the file

### Import Process
1. Go back to the Sales Order
2. Click "Import PO Prices" button
3. Upload your modified Excel file
4. Click "Import & Update"
5. Review the update summary
6. Check your Sales Order - costs will be updated automatically

## Excel File Structure
The exported Excel contains:
- External ID (for internal tracking)
- PO Number
- PO Line ID
- SO Number
- SO Line ID
- Product Code
- Product Name
- Quantity
- Original Unit Price
- Updated Unit Price (modify this column)
- Currency
- PO State

## Technical Notes
- Only modify the "Updated Unit Price" column (Column J)
- Do not modify any other columns
- The module automatically handles PO state (resets to draft if needed)
- All updates are logged in the summary

## Support
For issues or questions, please contact your system administrator.

## License
LGPL-3

## Author
Your Company

## Version
16.0.1.0.0
