from odoo import models, fields, api, exceptions, _ 
import logging
_logger = logging.getLogger(__name__)

class MantenimientoMain(models.Model):
    _name = "maintenance.main"
    _description = "Mantenimiento Principal"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre del Mantenimiento", required=True, readonly=True, default=lambda self: 'Nuevo')
    room_id = fields.Many2one("room.main", string="Habitación")
    
    # ESTADO
    status = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('finalished', 'Finalizada')
    ], string="Estado", default='draft')
    
    # SECUENCIA
    sequence = fields.Char(string="Secuencia", required=True, copy=False, readonly=True, default=lambda self: 'Nuevo')

    # DESCRIPCIÓN DEL MANTENIMIENTO
    employer_id = fields.Many2one(comodel_name="hr.employee", string="Empleado Responsable", required=True)
    room_propierty_reference = fields.Reference(
        string="Vivienda/Habitación", 
        selection=[('room.main', 'Habitación'), ('property.main', 'Vivienda')], 
        required=True
    )
    start_date = fields.Date(string="Fecha de Inicio", default=fields.Datetime.now)
    end_date = fields.Date(string="Fecha Final") 
    description = fields.Text(string="Descripción del Mantenimiento")
    hours_worked = fields.Float(string="Horas Trabajadas")
    price_per_hour = fields.Float(string="Precio por Hora")
    total_price = fields.Float(string="Precio Total", compute="_total_price_worked")

    # LÍNEA DE SERVICIOS
    maintenance_line_id = fields.One2many('maintenance.line', 'maintenance_id', string="Líneas del Mantenimiento")

    # MUEBLES
    furniture_list = fields.Many2many(comodel_name="furniture.item", string="Lista de Muebles")

    # IMÁGENES/VIDEOS
    pictures_maintenance = fields.Many2many(
        comodel_name="ir.attachment", 
        relation="maintenance_ir_attachment_rel", 
        column1="maintenance_id", 
        column2="attachment_id", 
        string="Fotos del Mantenimiento"
    )
    
    videos_binary = fields.Many2many(
        'ir.attachment',
        string="Videos Subidos",
        relation="maintenance_video_attachment_rel",
        column1="maintenance_id",
        column2="attachment_id",
        help="Sube videos en un formato compatible con el servidor"
    )

    # FUNCIONALIDADES
    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', 
        domain=lambda self: [('res_model', '=', self._name)], 
        string="Seguidores"
    )
    message_ids = fields.One2many('mail.message', 'res_id', string="Mensajes", readonly=True)

    # CALENDARIO
    calendar_event_id = fields.Many2one('calendar.event', string="Evento del Calendario", readonly=True)

    urgent = fields.Boolean(string="Urgente", default=False)

    @api.model
    def create(self, vals):
        """Crea el mantenimiento con su número de secuencia, actualiza eventos en el calendario y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            # Deshabilitar el seguimiento temporalmente
            self = self.with_context(tracking_disable=True)
            
            # Generar secuencia si es necesario
            if vals.get('sequence', 'Nuevo') == 'Nuevo':
                vals['sequence'] = self.env['ir.sequence'].next_by_code('maintenance.main.sequence') or 'Nuevo'
            
            # Crear el registro
            record = super(MantenimientoMain, self).create(vals)
            
            # Crear o actualizar evento en el calendario
            record._create_or_update_calendar_event()
            
            # Publicar mensaje en el chatter
            record.message_post(
                body=_("El mantenimiento '%s' ha sido creado con éxito.") % record.sequence,
                subject=_("Nuevo Mantenimiento Creado"),
                message_type="notification"
            )
            
        return record


    def write(self, vals):
        res = super(MantenimientoMain, self).write(vals)
        if any(key in vals for key in ['start_date', 'end_date', 'sequence']):
            self._create_or_update_calendar_event()
        return res

    def action_change_status(self):
        for record in self:
            if record.status == 'draft':
                record.status = 'sent'
            elif record.status == 'sent':
                record.status = 'approved'
            elif record.status == 'approved':
                record.status = 'inprogress'
            elif record.status == 'inprogress':
                record.status = 'finalished'
            else:
                raise exceptions.UserError("El mantenimiento ya está finalizado.")

    def action_cancel(self):
        for record in self:
            if record.status == 'finalished':
                record.status = 'approved'
            elif record.status == 'inprogress':
                record.status = 'approved'
            else:
                raise exceptions.UserError("Solo se puede cancelar si está en Progreso o Finalizada")

    def _create_or_update_calendar_event(self):
        self.ensure_one()
        _logger.info(f"Llamando a _create_or_update_calendar_event para mantenimiento: {self.sequence}")
        event_vals = {
            'name': f'{self.sequence} ({self.start_date.strftime("%d/%m/%Y")} - {self.end_date.strftime("%d/%m/%Y") if self.end_date else "Sin Fecha Final"})',
            'start': self.start_date,
            'stop': self.end_date or self.start_date,
            'allday': False,
            'user_id': self.employer_id.user_id.id if self.employer_id.user_id else False,
            'description': f'Mantenimiento {self.sequence} asignado a {self.employer_id.name if self.employer_id else "N/A"}',
        }
        if self.calendar_event_id:
            _logger.info(f"Actualizando evento existente con ID: {self.calendar_event_id.id}")
            self.calendar_event_id.write(event_vals)
        else:
            _logger.info(f"Creando nuevo evento con valores: {event_vals}")
            event = self.env['calendar.event'].create(event_vals)
            self.calendar_event_id = event.id
            _logger.info(f"Nuevo evento creado con ID: {event.id}")
    
    def unlink(self):   
        """
        Sobrescribe unlink para eliminar también el evento del calendario asociado.
        """
        for record in self:
            if record.calendar_event_id:
                record.calendar_event_id.unlink()
        return super(MantenimientoMain, self).unlink()

    @api.depends('hours_worked', 'price_per_hour')
    def _total_price_worked(self):
        for record in self:
            if record.hours_worked > 0:
                record.total_price = record.hours_worked * record.price_per_hour
            else:
                record.total_price = 0.0

    def action_aceptar(self):
        for record in self:
            record.write({'status': 'approved'})
            record.message_post(
                body=_("El registro ha sido aprobado."),
                subject=_("Aprobado"),
                message_type="notification"
            )
            record.message_subscribe(partner_ids=[record.create_uid.partner_id.id])

    def action_rechazar(self):
        for record in self:
            record.write({'status': 'rejected'})
            record.message_post(
                body=_("El registro ha sido rechazado."),
                subject=_("Rechazado"),
                message_type="notification"
            )
            record.message_subscribe(partner_ids=[record.create_uid.partner_id.id])


class MantenimientoLines(models.Model):
    _name = 'maintenance.line'
    _description = 'Líneas del Mantenimiento'

    maintenance_id = fields.Many2one('maintenance.main', string="ID de Mantenimiento", required=True, ondelete='cascade')
    service_ids = fields.Many2one(
        'product.product',
        string="Servicios",
        domain="[('type', '=', 'service')]",
    )
    responsible = fields.Selection([
        ('owner', 'Propietario'),
        ('agency', 'Agencia'),
        ('tenant', 'Inquilino')
    ], string="Responsable", required=True)
    amount = fields.Float(string="Importe", required=True)
    tax_id = fields.Many2one(
        'account.tax',
        string="IVA",
        help="El impuesto IVA asociado a este registro"
    )
    def get_graph_data(self):
        """Método para verificar los datos del gráfico."""
        if not self.search([]):
            return False 
        return True
