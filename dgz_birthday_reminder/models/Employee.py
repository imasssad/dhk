# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api


class DgzBirthdayReminder(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def get_birthday_reminders(self):
        today = fields.Date.today()
        current_year = today.year
        all_employees = self.env['hr.employee'].search([('active', '=', True), ('birthday', '!=', False)])
        employees_with_upcoming_birthday = []
        for emp in all_employees:
            birthday_this_year = datetime(current_year, emp.birthday.month, emp.birthday.day).date()
            if birthday_this_year < today:
                next_birthday = datetime(current_year + 1, emp.birthday.month, emp.birthday.day).date()
                age = next_birthday.year - emp.birthday.year - (
                        (next_birthday.month, next_birthday.day) < (emp.birthday.month, emp.birthday.day))
            else:
                next_birthday = birthday_this_year
                age = next_birthday.year - emp.birthday.year - (
                            (next_birthday.month, next_birthday.day) < (emp.birthday.month, emp.birthday.day))
            employees_with_upcoming_birthday.append((emp, next_birthday,age))
        employees_alldata_dict = {
            emp.id: {
                'name': emp.name,
                'birthday': emp.birthday,
                'next_birthday': bd,
                'age':age,
                'avatar_url': f'/web/image/hr.employee/{emp.id}/avatar_128'
            } for emp, bd ,age in employees_with_upcoming_birthday
        }
        is_in_group = self.env.user.has_group('dgz_birthday_reminder.administration_priority_groups')
        return { 'employee_data_dict': employees_alldata_dict, 'is_in_group': is_in_group }
