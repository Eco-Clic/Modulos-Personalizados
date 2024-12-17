from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)

class WizardPaymentInsurancePartner(models.TransientModel):
    _name = 'wizard.payment.insurance.partner'
    _description = 'Wizard para Seguro de Pago en Partner'

    partner_id = fields.Many2one('res.partner', string='Inquilino')
    additional_delivery = fields.Boolean(string="Entrega adicional", default=False)
    insurance_date = fields.Date(string="Fecha seguro")
    departure_date = fields.Date(string="Fecha de salida")
    policy_amount = fields.Integer(string="Monto del Seguro")

    @api.model
    def default_get(self, fields):
        res = super(WizardPaymentInsurancePartner, self).default_get(fields)
        partner_id = self.env.context.get('default_partner_id')
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            if partner.exists():
                res.update({
                    'partner_id': partner.id,
                    'departure_dat': partner.departure_date,
                    'insurance_date': partner.insurance_date,
                    'policy_amount': partner.policy_amount,
                    'additional_delivery': partner.additional_delivery,
                })
            _logger.info(f"Default values for wizard: {res}")
        return res

    def confirm_payment_insurance(self):
        if self.partner_id:
            self.partner_id.write({
                'payment_insurance': True,
                'insurance_date': self.insurance_date,
                'policy_amount': self.policy_amount,
                'additional_delivery': self.additional_delivery,
                'departure_dat': self.departure_date,

            })
        _logger.info(f"Payment insurance updated for partner {self.partner_id.id}")
        return {'type': 'ir.actions.act_window_close'}