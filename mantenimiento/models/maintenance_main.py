from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)



class MantenimientoMain(models.Model):
    _name = "maintenance.main"  
    _description = "Main class for Maintenance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    #ESTADO
    status = fields.Selection([("approval", "PENDIENTE DE APROBACIÓN"), ("inprogress", "EN PROGRESO"), ("finalished", "FINALIZADO")], string="Status del Mantenimiento", required=True, default="inprogress")

    #SECUENCIA
    sequence = fields.Char(string="Secuencia", required=True, copy=False, readonly=True, default=lambda self: 'Nuevo')

    #DESCRIPCION MANTENIMIENTO
    employer_id = fields.Many2one(comodel_name="hr.employee", string="Empleado Responsable", required=True)
    room_propierty_reference = fields.Reference(string="Vivienda/Habitación", selection=[('rental.room', 'Habitación'), ('rental.property', 'Vivienda')], required=True)
    start_date = fields.Datetime(string="Fecha de inicio", default=fields.Datetime.now)
    end_date = fields.Datetime(string="Fecha final")

    #LIENA DE SERVICIOS 
    maintenance_line_id = fields.One2many('maintenance.line', 'maintenance_id', string="Lineas del mantenimiento")

    #MUEBLES
    furniture_list = fields.Many2many(comodel_name="furniture.room.item", string="Lista de Muebles")

    #IMAGENES/VIDEOS
    pictures_maintenance = fields.Many2many(comodel_name="ir.attachment", relation="maintenance_ir_attachment_rel", column1="maintenance_id", column2="attachment_id", string="Fotos del Mantenimiento")
    
    videos_binary = fields.Many2many(
        'ir.attachment',
        string="Videos Subidos",
        relation="maintenance_video_attachment_rel",
        column1="maintenance_id",
        column2="attachment_id",
        help="Sube videos en un formato compatible con el servidor"
    )

    #FUNCIONALIDADES
    message_follower_ids = fields.One2many('mail.followers', 'res_id', domain=lambda self: [('res_model', '=', self._name)], string='Followers')
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages', readonly=True)

    #CALENDARIO
    calendar_event_id = fields.Many2one('calendar.event', string="Evento de Calendario", readonly=True)

    urgent = fields.Boolean(string="Urgente", default=False)

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'Nuevo') == 'Nuevo':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('maintenance.main.sequence') or 'Nuevo'
        record = super(MantenimientoMain, self).create(vals)
        record._create_or_update_calendar_event()
        return record

    def write(self, vals):
        res = super(MantenimientoMain, self).write(vals)
        if any(key in vals for key in ['start_date', 'end_date', 'sequence']):
            self._create_or_update_calendar_event()
        return res

    def action_change_status(self):
        for record in self:
            if record.status == 'approval':
                record.status = 'inprogress'
            elif record.status == 'inprogress':
                record.status = 'finalished'
            else:
                raise exceptions.UserError("El mantenimiento ya está finalizado.")

    def action_cancel(self):
        for record in self:
            if record.status == 'finalished':
                record.status = 'approval'
            elif record.status == 'inprogress':
                record.status = 'approval'
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
        
            

class MantenimientoLines(models.Model):
    _name = 'maintenance.line'
    _description = 'Lineas del mantenimiento'

    maintenance_id = fields.Many2one('maintenance.main', string="Mantenimiento Lineas ID", required=True, ondelete='cascade')
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

    # Estado del mantenimiento relacionado
    maintenance_status = fields.Selection(related="maintenance_id.status", string="Estado del Mantenimiento", store=True)

    def get_graph_data(self):
        """Método para verificar los datos del gráfico."""
        if not self.search([]):
            return False 
        return True  

    def action_open_report_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generar Reporte'),
            'res_model': 'maintenance.report.wizard',
            'view_mode': 'form',
            'target': 'new',
        }