from odoo import fields, models, api


class RentalPaymentHistory(models.Model):
    _name = 'rental.payment.history'
    _description = 'Rental Payment History'

    tenant_id = fields.Many2one('res.partner', string='Tenant')
    payment_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('services', 'Services')
    ], string='Payment Type')
    inmueble = fields.Selection([
        ('Property', 'Property'),
        ('Room', 'Room')
    ], string='Inmueble')

    alquiler_price = fields.Float(string='Precio Alquiler($)')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    reference_field = fields.Reference([
        ('rental.property', 'Property'),
        ('rental.room', 'Room')
    ], string="Related Reference")
    property_id = fields.Many2one('rental.property', string='Property')
    room_id = fields.Many2one('rental.room', string='Room')
