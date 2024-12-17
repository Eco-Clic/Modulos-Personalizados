from odoo import models, fields, api, exceptions, _ 

class HistorialOcupacionHabitacion(models.Model):
    _name = "room.main.occupancy"
    _description = "Historial de Ocupación de Habitaciones"
    _inherit = ["mail.thread", "mail.activity.mixin"]


    name = fields.Char(
        string="Historial de Ocupación de Habitaciones",
        required=True,
        copy=False,
        readonly=True,
        default="Nuevo",
    )
    room_id = fields.Many2one("room.main", string="Habitación", required=True)
    tenant_id = fields.Many2one(
        "res.partner",
        string="Inquilino",
        required=True,
        domain="[('owner_or_tenant', '=', 'tenant')]"
    )    
    start_date = fields.Date(string="Fecha de Inicio", required=True)
    end_date = fields.Date(string="Fecha de Fin")
    
    message_follower_ids = fields.Many2many(
        'res.partner',
        'message_follower_rel',
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

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise models.ValidationError(
                    "La fecha de inicio no puede ser posterior a la fecha de fin."
                )
    @api.model
    def create(self, vals):
        """Crea el historial de ocupación con su número de secuencia y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            # Generar secuencia si es necesario
            if vals.get("name", "Nuevo") == "Nuevo":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("rent.room.occupancy") or "Nuevo"
                )
            
            # Crear el registro
            record = super(HistorialOcupacionHabitacion, self).create(vals)
            
            # Publicar mensaje en el chatter
            record.message_post(
                body=_("El historial de ocupación '%s' ha sido creado con éxito.") % record.name,
                subject=_("Nuevo Historial de Ocupación Creado"),
                message_type="notification"
            )
            
        return record
