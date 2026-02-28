from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # inherited hr.employee model to override methods
    def sh_attendance_manual(self, vals, next_action, entered_pin=None):
        self.ensure_one()
        can_check_without_pin = not self.env.user.has_group('hr_attendance.group_hr_attendance_use_pin') or (
                self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            return self.sudo().sh_attendance_action(next_action, vals)
        return {'warning': _('Wrong PIN')}

    def sh_attendance_action_change(self, message):
        attendance_id = super(HrEmployee, self).sh_attendance_action_change(message)
        if self._context and self._context.get("meeting_id"):
            attendance_id.ref_meeting_id = self._context.get("meeting_id")
        return attendance_id
