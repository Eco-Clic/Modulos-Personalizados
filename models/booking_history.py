from odoo import api, fields, models, _ 

class BookingHistory(models.Model):
    _name = "booking.history"
    _description = "Historial de Reservas"
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    booking_amount = fields.Float(string="Importe de Reserva")
    issue_date = fields.Date(string="Fecha de Emisión")
    due_date = fields.Date(string="Fecha de Vencimiento")
    iva = fields.Many2one(
        'account.tax',
        string="Impuesto",
        domain="[('type_tax_use', 'in', ['sale', 'purchase'])]",
        help="Selecciona el impuesto aplicable."

    )
    irpf = fields.Float(string="IRPF (%)", digits=(6, 2))

    name = fields.Char(
        string="Reserva", 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: 'Nuevo'
    )
    tenant_id = fields.Many2one(
        'res.partner', 
        string="Inquilino"
    )
    room_id = fields.Many2one(
        'room.main', 
        string="Habitación"
    )
    message_follower_ids = fields.One2many(
        'mail.followers', 
        'res_id', 
        domain=lambda self: [('res_model', '=', self._name)], 
        string="Seguidores"
    )
    message_ids = fields.One2many(
        'mail.message', 
        'res_id', 
        string="Mensajes", 
        readonly=True
    )

    def create(self, vals):
        """Crea la reserva con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('booking.history.sequence') or 'Nuevo'
            record = super(BookingHistory, self).create(vals)
        
        record.message_post(
            body=_("La reserva '%s' ha sido creada con éxito.") % record.name,
            subject=_("Nueva Fianza Creada"),
            message_type="notification"
        )
        
        return record
