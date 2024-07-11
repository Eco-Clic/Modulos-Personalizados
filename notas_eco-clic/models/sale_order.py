from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    notas_internas = fields.Char(string="Notas")