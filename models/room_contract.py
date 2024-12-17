from datetime import date
from odoo import models, fields, api, _
from num2words import num2words

    
def number_to_words_es(number):
    return num2words(number, lang='es')

class RoomContract(models.Model):
    _name = "room.contract"
    _description = "Modelo para los contratos de una habitacion"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_('Contrato'), required=True, copy=False, readonly=True, default='Nuevo')
    contract_number = fields.Char(string=_('Número de Contrato'))
    contract_date = fields.Date(string=_('Fecha de Firma'), required=True, default=date.today())
    month_sing_in_words = fields.Char(string=_('Mes en Letras'), compute='_compute_month_in_words')
    property_id = fields.Many2one('property.main', string=_('Propiedad'))
    room_id = fields.Many2one('room.main', string=_('Habitación'), domain="[('property_id', '=', property_id)]")
    tenant_id = fields.Many2one('res.partner', string=_('Inquilino'), required=True)
    agency_id = fields.Many2one('res.partner', string=_('Agencia'))
    contract_start_date = fields.Date(string=_('Fecha de Inicio'), required=True, default=date.today())
    contract_end_date = fields.Date(string=_('Fecha de Finalización'), required=True, default=date.today())
    renewal_terms = fields.Text(string=_('Condiciones de Renovación o Terminación'))

    
    property_contract_id = fields.Many2one('property.contract', string='Contrato de Propiedad', readonly=True)

    company_id = fields.Many2one(
        'res.company', string='Compañía',
        default=lambda self: self.env.company
    )
    
    # Terminos Financieros
    monthly_rent = fields.Float(string=_('Renta Mensual'))
    rent_in_words = fields.Char("Renta en palabras", compute="_compute_rent_in_words")

    late_payment_fee = fields.Float(string='Pagos Tardíos (Euros)')
    late_payment_fee_in_words = fields.Char(
        string='Pagos Tardíos en Palabras',
        compute="_compute_late_payment_fee_in_words"
    )

    security_deposit = fields.Float(string='Depósito de Seguridad')
    security_deposit_in_words = fields.Char('Deposito de seguridad en palabras', compute="_compute_security_deposit_in_words" )

    penalty_terms = fields.Text(string=_('Términos de Penalización por Impago o Terminación Anticipada'))


    # Obligaciones
    tenant_responsibilities = fields.Text(string=_('Responsabilidades del Inquilino'))
    agency_responsibilities = fields.Text(string=_('Responsabilidades de la Agencia'))

    # Documentación
    signed_contract = fields.Binary(string=_('Contrato Firmado'))
    contract_attachments = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'rental.contract')],
        string=_('Adjuntos del Contrato')
    )


    is_active = fields.Boolean(string=_('Activo'), compute='_compute_is_active')
    status = fields.Selection(
        [
            ('draft', _('Borrador')),
            ('open', _('Activo')),
            ('closed', _('Cerrado'))
        ],
        string=_('Estado'),
        default='draft',
    )
    active = fields.Boolean(string=_('Activo'), default=True)

    sections_with_data = fields.Char(string="Seciones con datos de apartados de la propiedad", compute="_compute_sections_with_data")

    @api.model
    def create(self, vals):
        """Crea el contrato de habitación con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            # Generar secuencia si es necesario
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('room.contract.sequence') or 'Nuevo'
            
            # Crear el registro
            record = super(RoomContract, self).create(vals)
            
            # Publicar mensaje en el chatter
            record.message_post(
                body=_("El contrato de habitación '%s' ha sido creado con éxito.") % record.name,
                subject=_("Nuevo Contrato de Habitación Creado"),
                message_type="notification"
            )
            
        return record

        
    def action_contract_open(self):
        self.status = 'open'
        if self.property_id and not self.room_id:
            self.property_id.status = 'occupied'
            self.property_id.tenant_id = self.tenant_id.id
            self.property_id.contract_open = self.id
        elif self.property_id and self.room_id:
            self.room_id.status = 'occupied'
            self.room_id.tenant_id = self.tenant_id.id
            self.room_id.contract_open = self.id
        self.active = True

    def action_contract_closed(self):
        self.status = 'closed'
        if self.property_id and not self.room_id:
            self.property_id.status = 'available'
            self.property_id.tenant_id = False
            self.property_id.contract_open = False
        elif self.property_id and self.room_id:
            self.room_id.status = 'available'
            self.room_id.tenant_id = False
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
                raise models.ValidationError(_('La fecha de finalización debe ser posterior a la fecha de inicio.'))\

    def action_confirm_room_contracts(self):
        active_ids = self.env.context.get('active_ids', [])
        property_contract_id = self.env.context.get('default_property_contract_id')

        # Verifica si el contrato principal existe
        property_contract = self.env['property.contract'].browse(property_contract_id).exists()
        if not property_contract:
            raise models.ValidationError(_('El contrato de propiedad ya no existe.'))

        # Verifica cada contrato de habitación
        for contract_id in active_ids:
            room_contract = self.env['room.contract'].browse(contract_id).exists()
            if not room_contract:
                continue  # Ignora contratos eliminados
            property_contract.room_contract_ids = [(4, room_contract.id)]

    @api.depends('property_id')
    def _compute_sections_with_data(self):
        for record in self:
            sections = []
            if record.property_id:
                # Verificar cada sección en property_id
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

    def action_print_contract_room(self):
        return self.env.ref('alquileres.print_contract_report_room').report_action(self)
        
    def action_print_contract_anex_room(self):
        return self.env.ref('alquileres.print_contract_anex_report_room').report_action(self)

    @api.depends('monthly_rent')
    def _compute_rent_in_words(self):
        for record in self:
            record.rent_in_words = number_to_words_es(record.monthly_rent)

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