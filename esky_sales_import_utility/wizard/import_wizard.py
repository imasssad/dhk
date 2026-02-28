from odoo import fields, models, _
import base64
from datetime import datetime, timedelta
from io import BytesIO
import xlrd
from odoo.exceptions import UserError

class ImportData(models.TransientModel):
    _name="import.sale.lines"
    _description = 'Import P&L Sheet'

    upload_file = fields.Binary("File")
    file_name = fields.Char("File Name")
    sale_id = fields.Many2one('sale.order')
    
    def read_excel(self):
        attachment_obj = self.env["ir.attachment"]
        if not self.upload_file:
            raise UserError(_("Error!, Please Select a File"))            
        else:
            val = base64.decodebytes(self.upload_file)
            tempfile = BytesIO()
            tempfile.write(val)
            work_book = xlrd.open_workbook(file_contents=tempfile.getvalue())
            vals = {"name": self.file_name, "datas": self.upload_file, "sale_sheet": True, "res_id": self.sale_id.id, "res_model": "sale.order"}
            attachment_obj.sudo().create(vals)
        return work_book

    contract_template = fields.Binary(default=lambda self: self.env.ref('esky_sales_import_utility.sale_lines_excel').datas,string="Template")

    def get_contract_template(self):
        return {
        'type': 'ir.actions.act_url',
        'name': 'contract',
        'url': '/web/content/import.sale.lines/%s/contract_template/P&L.xlsx?download=true' %(self.id),
        }

    def data_upload_sale_lines(self):

        def float_to_date(float_date):
            # The base date for Excel is January 1, 1900
            base_date = datetime(1899, 12, 30)
            delta = timedelta(days=float_date)
            return base_date + delta

        def validate_date(date_str):
            if isinstance(date_str, float):
                return float_to_date(date_str)
            else:
                try:
                    date_obj = datetime.strptime(date_str, '%d-%m-%Y')
                    return date_obj
                except ValueError:
                    return None

        wb = self.read_excel()
        sheet1= wb.sheet_by_index(0)
        sheet2 = wb.sheet_by_index(1)
        sheet_rows=sheet1.nrows
        product_obj = self.env['product.product']
        product_category_obj = self.env['product.category']
        sale_obj = self.env['sale.order'].browse(self.sale_id.id)
        wizard_message = self.env['wizard.message']
        current_company_id = self.env.context['allowed_company_ids'][0]
        company_id = self.env['res.company'].browse(current_company_id)
        usd_id = self.env['res.currency'].search([('name', '=', 'USD')])
        order_lines = []
        count = 0
        for line in sale_obj.order_line:
            order_lines.append((2,line.id))
        for row in range(1,sheet_rows):
            data_dict={}

            if sheet1.row_values(row)[0]:
                product_id = product_obj.search([('default_code','=',sheet1.row_values(row)[0])])
                if product_id:
                    data_dict["product_id"] = product_id.id
                    if product_id.standard_price != sheet1.row_values(row)[5]:
                        price = usd_id._convert(sheet1.row_values(row)[5], company_id.currency_id, company_id, self._context.get('date') or fields.Date.today())
                        product_id.write({'standard_price': price})
                else:
                    category_data = sheet1.row_values(row)[7]
                    if ' / ' in category_data:
                        categories = category_data.split(' / ')

                        parent_category_name = categories[-2]
                        child_category_name = categories[-1]
                        # parent_category = product_category_obj.search([('name', '=', parent_category_name)])
                        # child_category = product_category_obj.search([('name', '=', child_category_name),('parent_id', '=', parent_category.id)])
                        child_category = product_category_obj.search([('complete_name', '=', category_data)])
                        product_category = child_category

                    else:
                        product_category = product_category_obj.search([('name','=',category_data)])
                    if not product_category:
                        product_category = product_category_obj.sudo().create({'name': category_data})
                    price = usd_id._convert(sheet1.row_values(row)[5], company_id.currency_id, company_id, self._context.get('date') or fields.Date.today())
                    product_code = sheet1.row_values(row)[0]
                    product_name = sheet1.row_values(row)[1]
                    description_sale  = sheet1.row_values(row)[3]
                    if not isinstance(sheet1.row_values(row)[0], str):
                        product_code = int(sheet1.row_values(row)[0])
                    if not isinstance(sheet1.row_values(row)[1], str):
                        product_name = int(sheet1.row_values(row)[1])
                    product_id = product_obj.sudo().create({'name':product_name,'description_sale':description_sale ,'default_code': product_code, 'categ_id': product_category.id, 'taxes_id': False, 'standard_price': price, 'company_id': current_company_id})
                    data_dict["product_id"] = product_id.id
            if sheet1.row_values(row)[2]:
                product_part_number = sheet1.row_values(row)[2]
                if not isinstance(sheet1.row_values(row)[2], str):
                    product_part_number = int(sheet1.row_values(row)[2])
                data_dict["part_number"] = product_part_number
            if sheet1.row_values(row)[4]:
                data_dict["product_uom_qty"] = sheet1.row_values(row)[4]
            if sheet1.row_values(row)[5]:
                data_dict["purchase_price"] = sheet1.row_values(row)[5]
            if sheet1.row_values(row)[6]:
                data_dict["price_unit"] = sheet1.row_values(row)[6]
            if sheet1.row_values(row)[8]:
                valid_date = validate_date(sheet1.row_values(row)[8])
                if valid_date:
                    data_dict["start_date"] = valid_date
                else:
                    raise UserError(_("Start Date is not in valid format (dd-mm-yyyy) on row "+str(row+1)))
            if sheet1.row_values(row)[9]:
                valid_date = validate_date(sheet1.row_values(row)[9])
                if valid_date:
                    data_dict["end_date"] = valid_date
                else:
                    raise UserError(_("End Date is not in valid format (dd-mm-yyyy) on row "+str(row+1)))


            if sheet1.row_values(row)[3]:
                count+=1
                description_sale  = sheet1.row_values(row)[3]
                if not isinstance(sheet1.row_values(row)[3], str):
                     description_sale  = int(sheet1.row_values(row)[3])
                data_dict["name"] = description_sale

                row_index = row + 14
                if sheet2.row_values(row_index)[5]:
                    data_dict['brand'] = sheet2.row_values(row_index)[5]
                else:
                    raise UserError(_("Vendor required for row "+str(row+1)+ " Product"))

                if sheet2.row_values(row_index)[6]:
                    vendor = self.env['res.partner'].search([('supplier_rank', '>', 0), ('name', '=', sheet2.row_values(row_index)[6])], limit=1)
                    if vendor:
                        data_dict['vendor_id'] = vendor.id

                order_lines.append((0, 0, data_dict))

        vals = {'order_line': order_lines}

        if sale_obj.state != 'draft':
            vals['state'] = 'draft'
        if sale_obj.approval_ids:
            vals['approval_ids'] = [(5,0)]
        sale_obj.write(vals)
        message = 'Total %s lines uploaded successfully !!!!! ' % count
        view = self.env.ref('esky_sales_import_utility.wizard_message_form')
        temp_id = wizard_message.sudo().create({'text':message})
        return {
            'name':_("Upload Result"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.message',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': temp_id.id,
           }
