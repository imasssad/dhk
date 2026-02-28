from odoo import api, models, fields, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approve'), ('confirm', 'Confirm'), ('cancel', 'Cancel')],
                             string="state", default="draft")
    is_checkin = fields.Boolean(string="Is Checkin")
    is_checkout = fields.Boolean(string="Is Checkout")

    def action_confirm(self):
        self.state = 'confirm'
        self.is_checkin = True
        return

    def action_cancel(self):
        self.state = 'cancel'
        return

    def get_approval(self):
        self.state = 'approve'
        return

    def dics_meeting_attendance(self, vals, next_action, entered_pin=None):
        employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)])
        print("employee_id :::: ", employee_id)
        attendances = self.env['hr.attendance'].sudo().search(
            [('employee_id', '=', employee_id.id), ('date_is_checkin', '=', True), ('date_is_checkout', '=', False)])

        meeting_id = self.sudo()
        if employee_id:
            if meeting_id.state == 'confirm':
                if meeting_id.is_checkin:
                    meeting_id.is_checkin = False
                    meeting_id.is_checkout = True
                    attendance_ids = self.env['hr.attendance'].sudo().search([('ref_meeting_id', '!=', meeting_id.id)])

                    for attendance in attendance_ids:
                        if attendance.date_is_checkin and not attendance.date_is_checkout:
                            attendance.sudo().ref_meeting_id.is_checkout = False
                            employee_id.sudo().with_context(
                                meeting_id=attendance.ref_meeting_id.id).sh_attendance_manual(vals, next_action,
                                                                                              entered_pin=entered_pin)
                elif meeting_id.is_checkout:
                    meeting_id.is_checkout = False

            return employee_id.sudo().with_context(meeting_id=meeting_id.id).sh_attendance_manual(vals, next_action,
                                                                                                  entered_pin=entered_pin)
        else:
            return {'warning': _('Wrong PIN')}
