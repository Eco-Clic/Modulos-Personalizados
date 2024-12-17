from odoo import fields, models, api, _


class PaymentHistory(models.Model):
    _name = 'payment.history'
    _description = 'Historial de Pagos de Renta'
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(string='Deudas', required=True, copy=False, readonly=True, default='Nuevo')

    payment_type = fields.Selection([
        ('monthly', _('Mensual')),
        ('services', _('Servicios')),
        ('debt', 'Deuda'),
        ('bail_bound', 'Fianza'),
        ('maintenance', 'Mantenimiento')
    ], string=_('Tipo de Pago'))

    inmueble = fields.Selection([
        ('Property', _('Propiedad')),
        ('Room', _('Habitación'))
    ], string=_('Inmueble'))

    amount = fields.Float(string=_('Precio'))

    property_id = fields.Many2one('property.main', string=_('Propiedad'))

    tenant_id = fields.Many2one('res.partner', string=_('Inquilino'))
    room_id = fields.Many2one('room.main', string=_('Habitación')) 

    debt_id = fields.Many2one(
        "debt.main",
        string="Deuda",
        domain="[('tenant_id', '=', tenant_id), ('status', '!=', 'paid')]"
    )
    bail_bound_id = fields.Many2one(
        "bail.bounds.history",
        string="Fianza",
        domain="[('tenant_id', '=', tenant_id), ('status', '!=', 'paid')]"
    )

    message_follower_ids = fields.Many2many(
        'res.partner',
        'payment_history_follower_rel',  
        'res_id',
        'partner_id',
        string="Seguidores",
        help="Contactos que siguen este registro"
    )

    activity_ids = fields.One2many(
        'mail.activity',
        'res_id',
        string="Actividades",
        auto_join=True,
        domain=lambda self: [('res_model', '=', self._name)],
        help="Actividades relacionadas con este registro"
    )

    message_ids = fields.One2many(
        'mail.message',
        'res_id',
        string="Mensajes",
        auto_join=True,
        domain=lambda self: [('model', '=', self._name)],
        help="Mensajes relacionados con este registro"
    )

    date_payment = fields.Date(string="Fecha del pago")

    @api.model
    def create(self, vals):
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.history') or 'Nuevo'
            record = super(PaymentHistory, self).create(vals)
        
            record.message_post(
                body=_("El pago %s ha sido creada.") % record.name,
                subject=_("Nuevo pago creado"),
                message_type="notification"
            )
        
        return record

    def _update_related_status(self):
        """Actualizar el estado de la deuda o fianza relacionada al registrar el pago."""
        if self.payment_type == 'debt' and self.debt_id:
            if self.amount >= self.debt_id.amount_due:
                self.debt_id.status = 'paid'
                self.debt_id.message_post(
                    body=_("La deuda '%s' ha sido marcada como Pagada mediante el pago '%s'.") % (self.debt_id.name, self.name),
                    subject=_("Deuda Pagada"),
                    message_type="notification"
                )
            else:
                raise models.ValidationError(_("El monto del pago es insuficiente para cubrir la deuda '%s'.") % self.debt_id.name)

        if self.payment_type == 'bail_bound' and self.bail_bound_id:
            if self.amount >= self.bail_bound_id.amount:
                self.bail_bound_id.status = 'paid'
                self.bail_bound_id.message_post(
                    body=_("La fianza '%s' ha sido marcada como Pagada mediante el pago '%s'.") % (self.bail_bound_id.name, self.name),
                    subject=_("Fianza Pagada"),
                    message_type="notification"
                )
            else:
                raise models.ValidationError(_("El monto del pago es insuficiente para cubrir la fianza '%s'.") % self.bail_bound_id.name)
            
    @api.depends('debt_id', 'bail_bound_id', 'maintenance_id')
    def _compute_status(self):
        for record in self:
            if record.debt_id:
                record.status = record.debt_id.status
            elif record.bail_bound_id:
                record.status = record.bail_bound_id.status
            elif record.maintenance_id:
                record.status = record.maintenance_id.status
            else:
                record.status = False