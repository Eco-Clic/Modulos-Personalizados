# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    point_product = fields.Integer(
        string="Puntos", required=True, related="product_id.point_product"
    )
    calculate = fields.Float(
        compute="_get_calculate_value", required=False, default=0.00
    )

    @api.depends("price_unit", "discount", "quantity", "point_product")
    def _get_calculate_value(self):
        for record in self:
            record.calculate = (
                record.price_unit * record.point_product * record.discount
            ) * record.quantity
