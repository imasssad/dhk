import pytz

from datetime import datetime, timedelta

from odoo import fields, api, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # customer_name = fields.Char(string="Customer")

    @api.model
    def create(self,vals):
        res = super(CalendarEvent,self).create(vals)
        if self._context.get('website_id'):
            res.allday = True
        return res


    @api.model
    def get_available_time_slots(self, emp_user_id, duration, meeting_date, timezone):
        self = self.sudo()
        timeslots = {}
        employee = self.env['hr.employee'].search([('user_id', '=', emp_user_id)], limit=1)
        date_obj = datetime.strptime(meeting_date, '%Y-%m-%d')
        dayofweek = date_obj.weekday()
        attendances = employee.resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek == str(dayofweek))

        def generate_timeslots(res, date_from, date_to, duration, events, tz):
            remainder = date_from.minute % 15
            if remainder:
                date_from += timedelta(minutes=15 - remainder)
            to_date = date_from + timedelta(minutes=duration)
            if to_date > date_to:
                return res
            else:
                for event in events:
                    start = pytz.timezone('UTC').localize(event.start)
                    stop = pytz.timezone('UTC').localize(event.stop)
                    timeslot_from = date_from.astimezone(pytz.timezone('UTC')).replace(second=0, microsecond=0)
                    timeslot_to = to_date.astimezone(pytz.timezone('UTC')).replace(second=0, microsecond=0)
                    if start == timeslot_from or (timeslot_from < start < timeslot_to) or (
                            start < timeslot_from < stop) or stop == timeslot_to or (
                            timeslot_from < stop < timeslot_to) or (start < timeslot_to < stop):
                        to_date = stop.astimezone(pytz.timezone(tz))
                        events -= event
                        return generate_timeslots(res, to_date, date_to, duration, events, tz)
                    else:
                        res.append((date_from, to_date))
                if not events:
                    res.append((date_from, to_date))
                return generate_timeslots(res, to_date, date_to, duration, events, tz)

        available_timeslots = []
        date_now = datetime.now().astimezone(pytz.timezone(timezone)).replace(second=0, microsecond=0)
        for attendance in attendances:
            events = self.env['calendar.event'].search([('start', '>', date_now.astimezone(pytz.timezone('UTC'))), (
            'stop', '>', pytz.timezone(employee.resource_calendar_id.tz).localize(
                date_obj + timedelta(hours=attendance.hour_from)).astimezone(pytz.timezone('UTC'))),
                                                        ('partner_ids', 'in', employee.user_id.partner_id.ids)],
                                                       order='stop')
            date_from = pytz.timezone(employee.resource_calendar_id.tz).localize(
                date_obj + timedelta(hours=attendance.hour_from)).astimezone(pytz.timezone('UTC')).astimezone(
                pytz.timezone(timezone))
            if date_now > date_from:
                date_from = date_now
            date_to = pytz.timezone(employee.resource_calendar_id.tz).localize(
                date_obj + timedelta(hours=attendance.hour_to)).astimezone(pytz.timezone('UTC')).astimezone(
                pytz.timezone(timezone))
            available_timeslots += generate_timeslots([], date_from, date_to, duration, events, timezone)

        for timeslot in available_timeslots:
            option = value = '{:02d}:{:02d} - {:02d}:{:02d}'.format(timeslot[0].hour, timeslot[0].minute,
                                                                    timeslot[1].hour, timeslot[1].minute)
            timeslots[option] = value
        return timeslots
