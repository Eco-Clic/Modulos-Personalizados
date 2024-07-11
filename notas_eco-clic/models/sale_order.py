from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Vista de dentro
    x_notas_sale = fields.Char(string="Notas")

    # Vista del tree
    x_notas_Modelo = fields.Char(string="Notas", related="x_notas_sale")