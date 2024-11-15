from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)

class CleaningMain(models.Model):
    _name = "cleaning.main"  
    _description = "Modelo de limpieza"
    _inherit = ['mail.thread', 'mail.activity.mixin']  

    #SECUENCIA
    sequence = fields.Char(string="Secuencia", required=True, copy=False, readonly=True, default=lambda self: 'Nuevo')
    
    #DESCRIPCION LIMPIEZA
    employer_id = fields.Many2one(comodel_name="hr.employee", string="Empleado Responsable", required=True)
    date = fields.Datetime(string="Día", default=fields.Datetime.now, required=True)
    status = fields.Selection(
        [("inprogress", "EN PROGRESO"), ("finalished", "FINALIZADO")],
        string="Estado del Mantenimiento",
        required=True,
        default="inprogress"
    )
    room_propierty_reference = fields.Reference(
        string="Vivienda/Habitación",
        selection=[('rental.room', 'Habitación'), ('rental.property', 'Vivienda')],
        required=True
    )
    calendar_event_id = fields.Many2one(comodel_name="calendar.event", string="Evento del Calendario", readonly=True)


    #FUNCIONALIDADES
    message_follower_ids = fields.One2many('mail.followers', 'res_id', domain=lambda self: [('res_model', '=', self._name)], string='Followers')
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'Nuevo') == 'Nuevo':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('cleaning.main.sequence') or 'Nuevo'
        record = super(CleaningMain, self).create(vals)
        record._create_or_update_calendar_event()
        return record

    def write(self, vals):
        res = super(CleaningMain, self).write(vals)
        if any(key in vals for key in ['date', 'sequence']):
            self._create_or_update_calendar_event()
        return res

    def action_change_status(self):
        for record in self:
            if record.status == 'inprogress':
                record.status = 'finalished'
            else:
                raise exceptions.UserError("La limpieza ya está finalizada.")

    def action_cancel(self):
        for record in self:
            if record.status == 'finalished':
                record.status = 'inprogress'
            else:
                raise exceptions.UserError("Solo se puede cancelar si está en Progreso o Finalizada")

    def _create_or_update_calendar_event(self):
        self.ensure_one()
        _logger.info(f"Llamando a _create_or_update_calendar_event para mantenimiento: {self.sequence}")
        event_vals = {
            'name': f'{self.sequence} ({self.date.strftime("%d/%m/%Y")})',
            'start': self.date,
            'stop': self.date,
            'allday': False,
            'user_id': self.employer_id.user_id.id if self.employer_id.user_id else False,
            'description': f'Limpieza {self.sequence} asignada a {self.employer_id.name if self.employer_id else "N/A"}',
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
        return super(CleaningMain, self).unlink()
