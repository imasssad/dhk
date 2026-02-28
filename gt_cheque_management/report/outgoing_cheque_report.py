
from odoo import api, fields, models

class OutgoingChequeReportProforma(models.AbstractModel):
    _name = 'outgoing.cheque.report_saleproforma'


    def get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment',
            'docs': docs,
            'proforma': True
        }