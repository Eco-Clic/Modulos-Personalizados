from odoo import models, fields, api

class AccountMove(models.Model):    
    _inherit = "account.move"

    notas_internas = fields.Char(string="Notas")