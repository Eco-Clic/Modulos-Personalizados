from odoo import models, fields, api

class Repair(models.Model):
    _inherit = 'repair.order'

    notas_internas = fields.Char("Notas")