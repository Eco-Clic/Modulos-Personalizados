# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    point_product = fields.Integer(string="Puntos", required=True, default=1)
