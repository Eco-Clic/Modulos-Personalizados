from odoo import models, fields, api

class AccountMove(models.Model):    
    _inherit = "account.move"

    # Vista de dentro
    x_notas_Modelo = fields.Char(string="Notas")

    # Vista del tree
    x_notas_invoice = fields.Char(string="Notas", related="x_notas_Modelo")