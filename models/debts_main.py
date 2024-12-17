from odoo import fields, models, api, _
from odoo.exceptions import UserError

class DebtMain(models.Model):
    _name = 'debt.main'
    _description = 'Modelo para las Deudas'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(
        string='Deudas', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: 'Nuevo'
    )
    tenant_id = fields.Many2one(
        'res.partner', 
        string='Inquilino Actual', 
        store=True
    )
    amount_due = fields.Float(
        string="Cantidad Adeudada"
    )
    contract_ids = fields.One2many(
        'room.contract', 'tenant_id',
        string='Contratos'
    )
    date_origin = fields.Date(
        string='Fecha de la Deuda'
    )
    status = fields.Selection(
        [
            ("draft", "Borrador"), 
            ('pending', 'Pendiente'),
            ('paid', 'Pagada'),
        ], 
        default='pending',
        string="Estado"
    )

    message_follower_ids = fields.One2many(
        'mail.followers', 
        'res_id', 
        domain=lambda self: [('res_model', '=', self._name)], 
        string='Seguidores'
    )
    message_ids = fields.One2many(
        'mail.message', 
        'res_id', 
        string='Mensajes', 
        readonly=True
    )

    @api.model
    def create(self, vals):
        """Crear una deuda con un número de secuencia único."""
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('debt.main.sequence') or 'Nuevo'
            record =  super(DebtMain, self).create(vals)
        
            record.message_post(
                body=_("La deuda %s ha sido creada.") % record.name,
                subject=_("Nueva deuda creada"),
                message_type="notification"
            )
            
        return record
    
    # Cambiar el estado
    def action_change_status(self):
        for record in self:
            if record.status == 'draft':
                record.status = 'pending'
            elif record.status == 'pending':
                record.status = 'paid'
            else:
                raise UserError("La deuda ya ha sido pagada.")
    
    # Cambiar el estado a borrador al cancelar
    def action_change_cancel(self):
        for record in self:
            if record.status in ['pending', 'paid']:
                record.status = 'draft'
            else:
                raise UserError(_("Solo se puede cancelar si está en Pendiente o Pagada."))
