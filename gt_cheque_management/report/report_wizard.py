from odoo import api, fields, models

class ChequeReportWizard(models.TransientModel):
    _name = 'cheque.report.wizard'
    
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date',default=fields.Date.context_today)
    cheq_type = fields.Selection([('incoming', 'Incoming'),('outgoing', 'Outgoing')],string="Report Type",default='incoming')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('register', 'Registered'),
        ('bounce', 'Bounced'),
        ('return', 'Returned'),
        ('deposit', 'Deposited'),
        ('transfer', 'Transfered'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status')
    

    def print_report(self):
        return self.env.ref('gt_cheque_management.action_cheque_manage_report_document').report_action(self)
        
        
 
    def print_data(self):
        cheque_data=[]
        if self.cheq_type=='incoming':
            if self.date_from and self.state:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','incoming'),('cheque_date','>=',self.date_from),('cheque_date','<=',self.date_to),('state','=',self.state)])
            elif self.date_from:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','incoming'),('cheque_date','>=',self.date_from),('cheque_date','<=',self.date_to)])
            elif self.state:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','incoming'),('cheque_date','<=',self.date_to),('state','=',self.state)])
            else:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','incoming'),('cheque_date','>=',self.date_to)])
        else:
            if self.date_from and self.state:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','outgoing'),('cheque_date','>=',self.date_from),('cheque_date','<=',self.date_to),('state','=',self.state)])
            elif self.date_from:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','outgoing'),('cheque_date','>=',self.date_from),('cheque_date','<=',self.date_to)])
            elif self.state:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','outgoing'),('cheque_date','<=',self.date_to),('state','=',self.state)])
            else:
                cheque_data=self.env['cheque.manage'].search([('cheq_type','=','outgoing'),('cheque_date','<=',self.date_to)])
        return cheque_data