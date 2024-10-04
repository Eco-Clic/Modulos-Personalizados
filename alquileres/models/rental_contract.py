from datetime import date

from odoo import models, fields, api

class RentalContract(models.Model):
    _name = 'rental.contract'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Rental Contract Management'

    # Información del Contrato
    name = fields.Char(string='Contract', required=True, copy=False, readonly=True, default='New')
    contract_number = fields.Char(string='Contract Number', required=True)
    contract_date = fields.Date(string='Signature Date', required=True)
    property_id = fields.Many2one('rental.property', string='Property', required=True) # propiedad arrendada
    room_id = fields.Many2one('rental.room', string='Room', required=True) # habitación arrendada
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    agency_id = fields.Many2one('res.partner', string='Agency', required=False)
    contract_start_date = fields.Date(string='Start Date', required=True)
    contract_end_date = fields.Date(string='End Date', required=True)
    renewal_terms = fields.Text(string='Renewal or Termination Conditions')

    # Términos Financieros
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    security_deposit = fields.Float(string='Security Deposit', required=True)
    payment_frequency = fields.Selection(
        [('monthly', 'Monthly'), ('quarterly', 'Quarterly')],
        string='Payment Frequency',
        required=True,
        default='monthly'
    )
    penalty_terms = fields.Text(string='Penalty for Non-payment or Early Termination')

    # Obligaciones de las Partes
    owner_responsibilities = fields.Text(string='Owner Responsibilities')
    tenant_responsibilities = fields.Text(string='Tenant Responsibilities')
    agency_responsibilities = fields.Text(string='Agency Responsibilities')

    # Documentación
    signed_contract = fields.Binary(string='Signed Contract') # Firma del contrato
    contract_attachments = fields.One2many(
        'ir.attachment', 'res_id',
        domain=[('res_model', '=', 'rental.contract')],
        string='Contract Attachments'
    )
    is_active = fields.Boolean(string='Active', compute='_compute_is_active')

    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_is_active(self):
        for record in self:
            today = date.today()
            record.is_active = record.contract_start_date <= today <= record.contract_end_date

    @api.constrains('contract_start_date', 'contract_end_date')
    def _check_dates(self):
        for record in self:
            if record.contract_start_date > record.contract_end_date:
                raise models.ValidationError('The contract end date must be after the start date.')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.contract') or 'New'
        return super(RentalContract, self).create(vals)