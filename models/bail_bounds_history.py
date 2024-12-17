from odoo import api, fields, models, _
from odoo.exceptions import UserError

class BailBoundsHistory(models.Model):
    _name = "bail.bounds.history"
    _description = "Historial de Fianzas"
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(
        string="Fianza", 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: 'Nuevo'
    )
    tenant_id = fields.Many2one(
        'res.partner', 
        string="Inquilino"
    )
    amount = fields.Float(
        string="Monto de la Fianza"
    )
    status = fields.Selection(
        [
            ("draft", "Borrador"), 
            ("published", "Publicado"), 
            ("paid", "Pagado")
        ],
        string="Estado de la Fianza",
        required=True,
        default="draft"
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

    @api.model
    def create(self, vals):
        """Crea la fianza con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('bail.bounds.hsitory.sequence') or 'Nuevo'
            record = super(BailBoundsHistory, self).create(vals)
        
            record.message_post(
                body=_("La fianza '%s' ha sido creada con éxito.") % record.name,
                subject=_("Nueva Fianza Creada"),
                message_type="notification"
            )
        
        return record

    def action_change_status(self):
        """Cambia el estado de la fianza a Publicada o Pagada."""
        for record in self:
            if record.status == 'draft':
                record.status = 'published'
                record.message_post(
                    body=_("La fianza '%s' ha sido publicada.") % record.name,
                    subject=_("Fianza Publicada"),
                    message_type="notification"
                )
            elif record.status == 'published':
                record.status = 'paid'
                record.message_post(
                    body=_("La fianza '%s' ha sido marcada como Pagada.") % record.name,
                    subject=_("Fianza Pagada"),
                    message_type="notification"
                )
            else:
                raise UserError(_("La fianza ya se encuentra en estado 'Pagado'."))

    def action_change_cancel(self):
        """Cambia el estado de la fianza a Borrador si está en Publicada o Pagada."""
        for record in self:
            if record.status in ['published', 'paid']:
                record.status = 'draft'
                record.message_post(
                    body=_("La fianza '%s' ha sido restablecida a Borrador.") % record.name,
                    subject=_("Fianza Restablecida"),
                    message_type="notification"
                )
            else:
                raise UserError(_("Solo se puede cancelar si la fianza está en estado Publicada o Pagada."))
