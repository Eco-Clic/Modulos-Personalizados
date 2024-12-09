from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    room_id = fields.Many2one('rental.room', string="Room")
    payment_id = fields.Many2one('rental.payment.history', string="Payment History")
    status = fields.Selection(
        [
            ("bueno", "Bueno"),
            ("malo", "Malo"),
            ("Regular", "Regular"),
        ],
        string="Current Status",
        required=True,
        default="bueno",
    )
    cantidad = fields.Integer("Cantidad")



class ProductProduct(models.Model):
    _inherit = 'product.product'

    payment_id = fields.Many2one('rental.payment.history', string="Payment History")
