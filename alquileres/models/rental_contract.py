from datetime import date

from odoo import models, fields, api

class RentalContract(models.Model):
    _name = 'rental.contract'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Rental Contract Management'

    # Información del Contrato
    name = fields.Char(string='Contract', required=True, copy=False, readonly=True, default='New')
    contract_number = fields.Char(string='Contract Number')
    contract_date = fields.Date(string='Signature Date', required=True,default=date.today())
    property_id = fields.Many2one('rental.property', string='Property', ) # propiedad arrendada
    room_id = fields.Many2one('rental.room', string='Room', domain="[('rental_id', '=', property_id)]") # habitación arrendada
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    agency_id = fields.Many2one('res.partner', string='Agency', required=False)
    contract_start_date = fields.Date(string='Start Date', required=True, default=date.today())
    contract_end_date = fields.Date(string='End Date', required=True, default=date.today())
    renewal_terms = fields.Text(string='Renewal or Termination Conditions')

    # Términos Financieros
    monthly_rent = fields.Float(string='Monthly Rent', )
    security_deposit = fields.Float(string='Security Deposit', )
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
    status = fields.Selection(
        [('draft', 'Draft'), ('open', 'Active'), ('closed', 'Closed')],
        string='Status',
        default='draft',
    )
    active = fields.Boolean(string='Active', default=True)

    def action_contract_open(self):
        self.status = 'open'
        if self.property_id and not self.room_id:
            self.property_id.status = 'occupied'
            self.property_id.tenant_id = self.tenant_id.id
            self.property_id.contract_open = self.id
        elif self.property_id and self.room_id:
            self.room_id.status = 'occupied'
            self.room_id.tenant_id = self.tenant_id.id
            self.room_id.contract_open = self.id
        self.active = True

    def action_contract_closed(self):
        self.status = 'closed'
        if self.property_id and not self.room_id:
            self.property_id.status = 'available'
            self.property_id.tenant_id = False
            self.property_id.contract_open = False
        elif self.property_id and self.room_id:
            self.room_id.status = 'available'
            self.room_id.tenant_id = False
            self.room_id.contract_open = False

    def action_contract_draft(self):
        self.status = 'draft'
        self.active = True

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