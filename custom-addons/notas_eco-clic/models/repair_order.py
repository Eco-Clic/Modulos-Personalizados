from odoo import models, fields, api

class Repair(models.Model):
    _inherit = 'repair.order'

    # Vista de dentro
    x_notas_reparacion = fields.Char(string="Notas")

    # Vista del tree
    x_notas_Modelo = fields.Char(string="Notas", related="x_notas_reparacion")