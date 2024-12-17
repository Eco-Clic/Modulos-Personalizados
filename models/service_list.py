import random

from odoo import models, fields, api

class ServicesItem(models.Model):
    _name = "service.item"
    _description = "Services Items for Room"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    color = fields.Integer(string="Color Index")
    
    def create(self, vals):
        if "color" not in vals:
            vals["color"] = random.randint(1, 11)
        return super(ServicesItem, self).create(vals)