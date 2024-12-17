from odoo import models, api, fields

import logging
_logger = logging.getLogger(__name__)

class WizardPaymentInsurance(models.TransientModel):
    _name = 'wizard.payment.insurance'
    _description = 'Wizard para Seguro de Pago'

    additional_delivery = fields.Boolean(string="Entrega adicional", default=False)
    insurance_date = fields.Date(string="Fecha seguro")
    policy_amount  = fields.Integer(string="Monto del Seguro")
    departure_date = fields.Date(string="Fecha de salida")
    room_id = fields.Many2one('room.main', string="Habitación")
    tenant_id = fields.Many2one('res.partner', string='Inquilino', store=True)

    
    @api.model
    def default_get(self, fields):
        res = super(WizardPaymentInsurance, self).default_get(fields)
        room_id = self.env.context.get('default_room_id')
        if room_id:
            room = self.env['room.main'].browse(room_id)
            if room.exists():
                res.update({
                    'room_id': room.id,
                    'insurance_date': room.insurance_date,
                    'policy_amount': room.policy_amount,
                    'additional_delivery': room.additional_delivery,
                })
            _logger.info(f"Data being written: {self.room_id}")
        return res

    def confirm_payment_insurance(self):
        if self.room_id:
            self.room_id.write({
                'payment_insurance': True,
                'insurance_date': self.insurance_date,
                'policy_amount': self.policy_amount,
                'additional_delivery': self.additional_delivery,    
            })
        return {'type': 'ir.actions.act_window_close'}

