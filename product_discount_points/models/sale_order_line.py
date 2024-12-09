# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    point_product = fields.Integer(
        string="Puntos", required=True, related="product_id.point_product"
    )
    calculate = fields.Float(
        compute="_get_calculate_value", required=False, default=0.00
    )

    @api.depends("price_unit", "discount", "product_uom_qty", "point_product")
    def _get_calculate_value(self):
        for record in self:
            record.calculate = (
                record.price_unit * record.point_product * record.discount
            ) * record.product_uom_qty
