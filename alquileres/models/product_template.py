from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    room_id = fields.Many2one('rental.room', string="Room")
    payment_id = fields.Many2one('rental.payment.history', string="Payment History")