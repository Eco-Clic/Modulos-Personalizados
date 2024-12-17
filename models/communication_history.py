from odoo import models, fields, api, exceptions, _ 

class CommunicationHistory(models.Model):
    _name = "communication.history"
    _description = 'Historial de Comunicaciones'

    name = fields.Char(
        string='Historial de Comunicaciones', 
        required=True, 
        copy=False, 
        readonly=True, 
        default='Nuevo'
    )
    tenant_id = fields.Many2one(
        'res.partner', 
        string='Inquilino', 
        required=True
    )
    communication_date = fields.Date(
        string='Fecha de la Comunicación', 
        required=True
    )
    communication_type = fields.Selection(
        [
            ('email', 'Correo Electrónico'), 
            ('phone', 'Llamada Telefónica'), 
            ('in_person', 'En Persona')
        ],
        string='Tipo de Comunicación'
    )
    description = fields.Text(
        string='Detalles de la Comunicación'
    )
    attachment = fields.Binary(
        string='Adjunto'
    )
    @api.model
    def create(self, vals):
        """Crea la communicacion con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('communication.history.sequence') or 'Nuevo'
            record = super(CommunicationHistory, self).create(vals)
        
        record.message_post(
            body=_("La comunicacion '%s' ha sido creada con éxito.") % record.name,
            subject=_("Nueva Comunicacion Creada"),
            message_type="notification"
        )
        
        return record