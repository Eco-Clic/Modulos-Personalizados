from datetime import date
from odoo import api, fields, models, _
from num2words import num2words

class ContratoPropiedad(models.Model):
    _name = "property.contract"
    _description = "Modelo de contratos de propiedad"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Contrato', required=True, copy=False, readonly=True, default='Nuevo')
    contract_number = fields.Char(string='Número de Contrato')
    contract_date = fields.Date(string='Fecha de Firma', required=True, default=date.today())
    property_id = fields.Many2one('property.main', string='Propiedad')
    owner_id = fields.Many2one('res.partner', string='Propietario', required=True)
    agency_id = fields.Many2one('res.partner', string='Agencia')
    contract_start_date = fields.Date(string='Fecha de Inicio', required=True, default=date.today())
    contract_end_date = fields.Date(string='Fecha de Finalización', required=True, default=date.today())
    renewal_terms = fields.Text(string='Condiciones de Renovación o Terminación')
    security_deposit = fields.Float(string='Depósito de Seguridad')
    security_deposit_in_words = fields.Char('Deposito de seguridad en palabras', compute="_compute_security_deposit_in_words" )

    room_contract_ids = fields.One2many("room.contract", "property_contract_id", string="Habitaciones")
    room_id = fields.Many2one("room.main", string="Habitación")

    
    company_id = fields.Many2one(
        'res.company', string='Compañía',
        default=lambda self: self.env.company
    )
    
    # Términos Financieros
    monthly_rent = fields.Float(string='Pago Mensual')
    rent_in_words = fields.Char("Renta en palabras", compute="_compute_rent_in_words")
    penalty_terms = fields.Text(string='Términos de Penalización por Impago o Terminación Anticipada')

    late_payment_fee = fields.Float(string='Pagos Tardíos (Euros)')
    late_payment_fee_in_words = fields.Char(
        string='Pagos Tardíos en Palabras',
        compute="_compute_late_payment_fee_in_words"
    )


    # Obligaciones
    owner_responsibilities = fields.Text(string='Responsabilidades del Propietario')
    agency_responsibilities = fields.Text(string='Responsabilidades de la Agencia')

    # Documentación
    signed_contract = fields.Binary(string='Contrato Firmado')
    contract_attachments = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'rental.contract')],
        string='Adjuntos del Contrato'
    )

    is_active = fields.Boolean(string='Activo', compute='_compute_is_active')
    status = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('open', 'Activo'),
            ('closed', 'Cerrado')
        ],
        string='Estado',
        default='draft',
    )
    active = fields.Boolean(string='Activo', default=True)

    message_follower_ids = fields.Many2many(
        'res.partner',
        'property_contract_follower_rel',  
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

    @api.model
    def create(self, vals):
        """Crea el contrato de propiedad con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            # Generar secuencia si es necesario
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('property.contract.sequence') or 'Nuevo'
            
            # Crear el registro
            record = super(ContratoPropiedad, self).create(vals)
            
            # Publicar mensaje en el chatter
            record.message_post(
                body=_("El contrato de propiedad '%s' ha sido creado con éxito.") % record.name,
                subject=_("Nuevo Contrato de Propiedad Creado"),
                message_type="notification"
            )
            
        return record


    def action_contract_open(self):
        self.status = 'open'
        if self.property_id and not self.room_id:
            self.property_id.status = 'occupied'
            self.property_id.owner_id = self.owner_id.id
            self.property_id.contract_open = self.id
        elif self.property_id and self.room_id:
            self.room_id.status = 'occupied'
            self.room_id.owner_id = self.owner_id.id
            self.room_id.contract_open = self.id
        self.active = True

    def action_contract_closed(self):
        self.status = 'closed'
        if self.property_id and not self.room_id:
            self.property_id.status = 'available'
            self.property_id.owner_id = False
            self.property_id.contract_open = False
        elif self.property_id and self.room_id:
            self.room_id.status = 'available'
            self.room_id.owner_id = False
            self.room_id.contract_open = False

    def action_contract_draft(self):
        self.status = 'draft'
        self.active = True

    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_is_active(self):
        for record in self:
            today = date.today()
            record.is_active = record.contract_start_date <= today <= record.contract_end_date

    @api.constrains('contract_start_date', 'contract_end_date')
    def _check_dates(self):
        for record in self:
            if record.contract_start_date > record.contract_end_date:
                raise models.ValidationError('La fecha de finalización debe ser posterior a la fecha de inicio.')

    def action_print_contract_property(self):
        return self.env.ref('alquileres.print_contract_report_property').report_action(self)
        
    def action_print_contract_anex_property(self):
        return self.env.ref('alquileres.print_contract_anex_report_property').report_action(self)
    
    def action_print_termination_contract(self):
        return self.env.ref('alquileres.print_termination_contract').report_action(self)
    
    @api.depends('property_id')
    def _compute_sections_with_data(self):
        for record in self:
            sections = []
            if record.property_id:
                # Verificar cada sección
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Terraza'):
                    sections.append('Terraza')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Patio Interior'):
                    sections.append('Patio Interior')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Patio Exterior'):
                    sections.append('Patio Exterior')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Habitaciones'):
                    sections.append('Habitaciones')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Baño'):
                    sections.append('Baño')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Cocina'):
                    sections.append('Cocina')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Salón'):
                    sections.append('Salón')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Comedor'):
                    sections.append('Comedor')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Pasillo'):
                    sections.append('Pasillo')
                if record.property_id.furniture_list.filtered(lambda f: f.location == 'Entrada'):
                    sections.append('Entrada')
                if record.property_id.service_list:
                    sections.append('Servicios')

            record.sections_with_data = ', '.join(sections)

    @api.depends('security_deposit_in_words')
    def  _compute_security_deposit_in_words(self):
        for record in self:
            record.security_deposit_in_words = number_to_words_es(record.security_deposit)

    @api.depends('contract_date')
    def _compute_month_in_words(self):
        for record in self:
            if record.contract_date:
                fecha = fields.Date.from_string(record.contract_date)
                record.month_sing_in_words = fecha.strftime('%B').capitalize()
            else:
                record.month_sing_in_words = ''
                
    @api.depends('late_payment_fee')
    def _compute_late_payment_fee_in_words(self):
        for record in self:
            if record.late_payment_fee:
                # Convertir el número a palabras en español
                record.late_payment_fee_in_words = num2words(record.late_payment_fee, lang='es').capitalize()
            else:
                record.late_payment_fee_in_words = ''