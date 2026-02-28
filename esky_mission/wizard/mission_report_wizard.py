import io
import base64
import xlsxwriter
from odoo import models, fields, api
import pytz
from datetime import datetime, timedelta

class MissionReportWizard(models.TransientModel):
    _name = 'mission.report.wizard'
    _description = 'Mission Report Wizard'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    department_id = fields.Many2one('hr.department', string='Department')

    def convert_utc_to_local(self, utc_dt, user_tz):
        local_tz = pytz.timezone(user_tz)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt).strftime('%Y-%m-%d %H:%M:%S')

    def print_excel(self):
        # Create an in-memory output file for the new workbook.
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Define formats.
        bold_format = workbook.add_format({'bold': True})
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#a4c2f4',  # Background color
            'border': 1,             # Border around the cell
            'align': 'center',       # Center-align text
            'valign': 'vcenter'      # Vertically center text
        })
        cell_format = workbook.add_format({
            'border': 1,             # Border around the cell
            'align': 'center',       # Center-align text
            'valign': 'vcenter'      # Vertically center text
        })

        # Write headers with bold and background color format.
        headers = [
            'Employee', 'Date',
            'Attendance Check In', 'Attendance Check Out',
            'Mission',
            'Time Off', 'Status'
        ]
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_format)

        row = 1

        if self.department_id:
            employees = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
        else:
            employees = self.employee_ids
        for employee in employees:
            current_date = self.date_from
            while current_date <= self.date_to:
                # Check Attendance
                attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', current_date),
                    ('check_in', '<', current_date + timedelta(days=1))
                ], limit=1)

                user_time_zone = 'Africa/Cairo'  # Example time zone
                # utc_time = datetime.utcnow()


                check_in_attendance = 'N/A'
                if attendance:
                    check_in_attendance = self.convert_utc_to_local(attendance.check_in, user_time_zone)
                    check_out_attendance = attendance.check_out
                    if attendance.check_out:
                        # check_out_attendance = attendance.check_out + timedelta(hours=3)
                        check_out_attendance = self.convert_utc_to_local(attendance.check_out, user_time_zone)
                else:
                    check_out_attendance = 'N/A'

                # Check Mission
                mission = self.env['mission.mission'].search([
                    ('employee_id', '=', employee.id),
                    ('date', '=', current_date)
                ], limit=1)
                options_map = {'from_home': 'Work From Home', 'from_esky': 'Work From Esky', 'visit': 'Visit'}
                check_in_mission = options_map.get(mission.options, 'N/A') if mission else 'N/A'

                # Check Time Off
                time_off = self.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('date_from', '<=', current_date),
                    ('date_to', '>=', current_date),
                    ('state', 'in', ['confirm', 'validate1', 'validate'])
                ], limit=1)

                time_off_status = 'Time Off' if time_off else 'N/A'

                # Determine Status
                if check_in_attendance != 'N/A' or check_in_mission != 'N/A':
                    status = 'Present'
                elif current_date.weekday() in [4, 5]:  # Friday (4) or Saturday (5)
                    check_in_attendance = 'Weekend'
                    check_out_attendance = 'Weekend'
                    check_in_mission = 'Weekend'
                    time_off_status = 'Weekend'
                    status = 'Weekend'

                elif time_off_status == 'Time Off':
                    check_in_attendance = 'Time Off'
                    check_out_attendance = 'Time Off'
                    check_in_mission = 'Time Off'
                    status = 'Time Off'
                else:
                    status = 'Absent'

                # Write data to Excel
                worksheet.write(row, 0, employee.name, cell_format)
                worksheet.write(row, 1, str(current_date), cell_format)
                worksheet.write(row, 2, str(check_in_attendance), cell_format)
                worksheet.write(row, 3, str(check_out_attendance), cell_format)
                worksheet.write(row, 4, str(check_in_mission), cell_format)
                worksheet.write(row, 5, time_off_status, cell_format)
                worksheet.write(row, 6, status, cell_format)

                current_date += timedelta(days=1)
                row += 1

        workbook.close()
        output.seek(0)

        # Create an attachment for the generated Excel file.
        file_name = 'mission_report.xlsx'  # Set the desired file name
        old_attachments = self.env['ir.attachment'].search([('name', '=', 'mission_report.xlsx')])
        if old_attachments:
            old_attachments.unlink()
        attachment = self.env['ir.attachment'].create({
            'name': file_name,  # File name as seen in the download prompt
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'store_fname': file_name,  # Store file name
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })

        # Return an action to download the file and close the wizard form.
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/employees_report?download=true' % attachment.id,
            'target': 'new'
        }

    def cancel(self):
        return {'type': 'ir.actions.act_window_close'}
