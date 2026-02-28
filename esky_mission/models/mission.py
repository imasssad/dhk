from odoo import fields, models, api
from datetime import datetime as dt
import datetime
import logging
logger = logging.getLogger(__name__)


class Mission(models.Model):
    _name = 'mission.mission'
    _description = 'Portal User Mission'

    name = fields.Char('Mission', required=True)
    desc = fields.Text('Description')
    readonly_desc = fields.Boolean('Readonly Description')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    date = fields.Date('Date', required=True, default=fields.Date.today)
    signin = fields.Boolean('SignIn')
    signout = fields.Boolean('SignOut')
    signin_at_esky = fields.Boolean('SignIn at Esky')
    signout_at_esky = fields.Boolean('SignOut at Esky')
    state = fields.Selection(string="Status",
        selection=[
            ('confirm', 'Waiting Manager Approval'),
            ('validate1', 'Waiting HR Manager Approval'),
            ('validate', 'Approved'),
            ('refuse', 'Refused'),
            ('lost', 'Lost'),
            ('completed', 'Completed')
        ], default='confirm')
    options = fields.Selection(string="Options",
        selection=[
            ('from_home', 'Work From Home'),
            ('from_esky', 'Work From Esky'),
            ('visit', 'Visit')
        ], default='from_home')
    customer_id = fields.Many2one('res.partner', 'Customer')
    sign_in_location = fields.Char('Sign In Location')
    sign_out_location = fields.Char('Sign Out Location')
    zone_id = fields.Many2one('zone.rate', 'Zone')
    zone_rate = fields.Float(string="Expense")
    signin_status = fields.Selection(string="Sign In Status",
        selection=[
            ('sign_in', 'Need to Sign In'),
            ('sign_out', 'Need to Sign Out'),
            ('missed', 'Missed'),
            ('done', 'Both Sign In/Out Done'),
        ], default='sign_in')
    signin_time = fields.Datetime(string="Sign In Time")
    signout_time = fields.Datetime(string="Sign Out Time")

    def approve_by_manager(self):
        self.state = 'validate1'

    def approve_by_hr_manager(self):
        if self.signin_status == 'done':
            self.state = 'completed'
        else:
            self.state = 'validate'

    def refuse_mission(self):
        self.state = 'refuse'

    def approve_mission_expense(self):
        self.state = 'completed'
        if not self.signin_status:
            self.signin_status = 'done'

    def update_mission_state(self):
        missions = self.sudo().search([])
        current_date = dt.now().date()
        for record in missions:
            if current_date > record.date and (not record.signin or not record.signout) and record.options == 'visit':
                logger.info("Failing due to update mission=====================")
                record.state = 'lost'
                record.signin_status = 'missed'

    def make_description_readonly(self):
        missions = self.sudo().search([])
        current_date = dt.now().date()
        for record in missions:
            two_days_later = record.date + datetime.timedelta(days=2)
            if current_date >= two_days_later:
                record.readonly_desc = True

