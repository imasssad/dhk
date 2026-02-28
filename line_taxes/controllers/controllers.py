# -*- coding: utf-8 -*-
# from odoo import http


# class LineTaxes(http.Controller):
#     @http.route('/line_taxes/line_taxes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/line_taxes/line_taxes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('line_taxes.listing', {
#             'root': '/line_taxes/line_taxes',
#             'objects': http.request.env['line_taxes.line_taxes'].search([]),
#         })

#     @http.route('/line_taxes/line_taxes/objects/<model("line_taxes.line_taxes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('line_taxes.object', {
#             'object': obj
#         })
