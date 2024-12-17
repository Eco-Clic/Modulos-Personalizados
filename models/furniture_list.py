import random

from odoo import models, fields, api

class FurnitureItem(models.Model):
    _name = "furniture.item"
    _description = "Muebles para Habitaciones"

    name = fields.Char(
        string="Nombre", 
        required=True
    )
    description = fields.Text(
        string="Descripción"
    )
    color = fields.Integer(
        string="Índice de Color"
    )

    def create(self, vals):
        """Asigna un color aleatorio si no se proporciona al crear un mueble."""
        if "color" not in vals:
            vals["color"] = random.randint(1, 11)
        return super(FurnitureItem, self).create(vals)
