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
    service_ids = fields.One2many(
        "rental.payment.history.lines", "payment_id",string="Service"
    )
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")

    @api.depends('tenant_id')
    def _compute_invoice_count(self):
        for record in self:
            partner = record.tenant_id
            if partner:
                record.invoice_count = self.env['account.move'].search_count(
                    [('partner_id', '=', partner.id), ('move_type', '=', 'out_invoice')])
            else:
                record.invoice_count = 0

    def action_create_invoice(self):
        self.ensure_one()
        invoice_lines = []
        for service in self.service_ids:
            invoice_lines.append((0, 0, {
                'product_id': service.product_id.id,
                'quantity': service.quantity,
                'price_unit': service.price,
                'account_id': service.product_id.property_account_income_id.id,
            }))
        invoice = self.env['account.move'].create({
            'partner_id': self.tenant_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
        })
        invoice.action_post()
        self.write({'invoice_id': invoice.id})


class RentalPaymentHistoryLines(models.Model):
    _name = 'rental.payment.history.lines'
    _description = ' Payment History Lines'

    payment_id = fields.Many2one('rental.payment.history', string='Payment')
    product_id = fields.Many2one("product.template", string="Product")
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    observations = fields.Text(string='Observations')