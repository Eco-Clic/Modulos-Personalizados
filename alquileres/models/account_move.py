from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_history_id = fields.Many2one('rental.payment.history', string='Payment History')
