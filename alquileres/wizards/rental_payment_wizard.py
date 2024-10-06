from odoo import fields, models, api


class ModelName(models.TransientModel):
    _name = 'rental.payment.wizard'
    _description = 'Description'

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
        "rental.payment.history.lines", "payment_id", string="Service"
    )
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")

    alquiler_price = fields.Float(string='Precio Alquiler($)', required=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    reference_field = fields.Reference([
        ('rental.property', 'Property'),
        ('rental.room', 'Room')
    ], string="Related Reference")

    @api.onchange('inmueble', 'tenant_id')
    def _onchange_inmueble(self):
        # Limpiar el campo de referencia cuando cambie la selección de inmueble
        self.reference_field = False

        if self.inmueble and self.tenant_id:
            # Dependiendo del valor de 'inmueble', cambiar el dominio del campo 'reference_field'
            if self.inmueble == 'Property':
                return {
                    'domain': {'reference_field': [('tenant_id', '=', self.tenant_id.id), ('is_property', '=', True)]}}
            elif self.inmueble == 'Room':
                return {'domain': {'reference_field': [('tenant_id', '=', self.tenant_id.id), ('is_room', '=', True)]}}
        else:
            return {'domain': {'reference_field': []}}

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

        if self.payment_type == 'monthly':
            # Agrega un producto de Pago de Alquiler con cantidad 1
            rental_product = self.env['product.template'].search([
                ('name', '=', 'Pago de Alquiler'),
                ('detailed_type', '=', 'service')
            ], limit=1)
            if rental_product:
                invoice_lines.append((0, 0, {
                    'product_id': rental_product.id,
                    'quantity': 1,
                    'price_unit': self.alquiler_price,
                }))
        else:
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
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factura Pago de Alquiler',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',  # Abre en la misma ventana
        }


class RentalPaymentHistoryLines(models.TransientModel):
    _name = 'rental.payment.history.lines'
    _description = ' Payment History Lines'

    payment_id = fields.Many2one('rental.payment.wizard', string='Payment')
    product_id = fields.Many2one("product.template", string="Product")
    quantity = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    observations = fields.Text(string='Observations')
