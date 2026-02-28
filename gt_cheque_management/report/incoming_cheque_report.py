
from odoo import api, fields, models

class IncomingChequeReportProforma(models.AbstractModel):
    _name = 'incoming.cheque.report_saleproforma'


    def get_report_values(self, docids, data=None):
        docs = self.env['cheque.manage'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'cheque.manage',
            'docs': docs,
            'proforma': True
        }