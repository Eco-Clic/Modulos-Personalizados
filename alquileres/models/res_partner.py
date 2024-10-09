# Modelo Odoo: Gestión de Inquilinos (Extendiendo res.partner)

from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = 'res.partner'

    # Información Personal
    birth_date = fields.Date(string='Date of Birth')
    owner_or_tenant= fields.Selection(
        [('owner', 'Owner'), ('tenant', 'Tenant')],
        string='Owner or Tenant'
    )
    identification_number = fields.Char(string='DNI/NIE', required=True)
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
        string='Marital Status'
    )
    nationality = fields.Many2one('res.country',string='Nationality')
    employment_status = fields.Selection(
        [('employed', 'Employed'), ('unemployed', 'Unemployed'), ('self_employed', 'Self-employed'),
         ('student', 'Student')],
        string='Employment Status'
    )
    monthly_income = fields.Float(string='Monthly Income')

    # Información de Alquiler
    property_id = fields.Many2one('rental.property', string='Rented Property')
    room_id = fields.Many2one('rental.room', string='Rented Room', domain="[('property_id', '=', property_id)]")
    lease_start_date = fields.Date(string='Lease Start Date')
    lease_end_date = fields.Date(string='Lease End Date')
    monthly_rent = fields.Float(string='Monthly Rent Amount')
    deposit_amount = fields.Float(string='Deposit Amount')
    guarantees = fields.Text(string='Additional Guarantees (Aval, Insurance, etc.)')

    # Historial
    rental_payment_history_ids = fields.One2many(
        'rental.payment.history', 'tenant_id', string='Rental Payment History'
    )
    rental_payment_count = fields.Integer(compute="_compute_rental_payment")
    incident_history_ids = fields.One2many(
        'rental.incident.history', 'tenant_id', string='Incident History'
    )
    incident_history_count = fields.Integer(compute="_compute_incident_history")
    communication_history_ids = fields.One2many(
        'rental.communication.history', 'tenant_id', string='Communication History'
    )
    communication_history_count = fields.Integer(compute="_compute_communication_history")

    # Información de los Avalistas (co-signers)
    co_signer_ids = fields.One2many('tenant.co_signer', 'tenant_id', string='Co-Signers')

    # Documentación
    signed_lease_contract = fields.Binary(string='Signed Lease Contract')
    id_document = fields.Binary(string='DNI/NIE or Passport')
    deposit_receipt = fields.Binary(string='Deposit Payment Receipt')
    income_proof = fields.Binary(string='Income Proof (Payslips, Tax Returns, etc.)')
    additional_guarantees = fields.Binary(string='Additional Guarantees (Aval, Insurance, etc.)')
    # si es Owner o es Tenant
    is_owner = fields.Boolean(compute='_compute_is_owner')
    is_tenant = fields.Boolean(compute='_compute_is_tenant')
    # Historial de Contratos
    rental_contracts_ids = fields.One2many(
        'rental.contract', 'tenant_id', string='Rental Contract History'
    )
    rental_contract_count = fields.Integer(compute="_compute_rental_contract")

    def _compute_rental_contract(self):
        for record in self:
            record.rental_contract_count = len(record.rental_contracts_ids) if record.rental_contracts_ids else 0

    def _compute_is_owner(self):
        for record in self:
            # recorrer todos los registros de rental.property o rental.room y verificar si es owner
            Properties = self.env['rental.property'].search([('owner_id', '=', record.id)])
            Rooms = self.env['rental.room'].search([('owner_id', '=', record.id)])
            if Properties or Rooms:
                record.is_owner = True

    def _compute_is_tenant(self):
        for record in self:
            Properties = self.env['rental.property'].search([('tenant_id', '=', record.id)])
            Rooms = self.env['rental.room'].search([('tenant_id', '=', record.id)])
            if Properties or Rooms:
                record.is_tenant = True

    @api.depends('monthly_income')
    def _compute_required_deposit(self):
        """
        Compute logic to determine if the tenant must pay one or two months of deposit
        based on the monthly income.
        """
        for tenant in self:
            if tenant.monthly_income and tenant.monthly_income < 1000:  # Threshold for extra deposit
                tenant.deposit_amount = tenant.monthly_rent * 2
            else:
                tenant.deposit_amount = tenant.monthly_rent


    def return_action_view_xml_id(self):
        """Return action window for xml_id passed through context"""
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id is not None:
            action = self.env['ir.actions.act_window']._for_xml_id(f'alquileres.{xml_id}')
            action.update(
                context=dict(self.env.context, default_res_partner_id=self.id, group_by=False),
                domain=[('tenant_id', '=', self.id)]
            )
            return action
        return False

    @api.depends('rental_payment_history_ids')
    def _compute_rental_payment(self):
        self.rental_payment_count = len(self.rental_payment_history_ids) if self.rental_payment_history_ids else 0

    @api.depends('communication_history_ids')
    def _compute_communication_history(self):
        self.communication_history_count = len(self.communication_history_ids) if self.communication_history_ids else 0

    @api.depends('incident_history_ids')
    def _compute_incident_history(self):
        self.incident_history_count = len(self.incident_history_ids) if self.incident_history_ids else 0

    def action_open_rental_payment_wizard(self):
        # Acción para abrir el wizard de de los Pagos de Alquiler
        return {
            'name': 'Rental Payment Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tenant_id': self.id,  # Pasa el partner como tenant
            }
        }

    def action_open_check_in_wizard(self):
        # Acción para abrir el wizard de Check-In
        return {
            'name': 'Check-In Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.check.in.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tenant_id': self.id,  # Pasa el partner como tenant
            }
        }

    def action_open_check_out_wizard(self):
        # Acción para abrir el wizard de Check-Out
        return {
            'name': 'Check-Out Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.check.out.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tenant_id': self.id,  # Pasa el partner como owner
            }
        }



class CoSigner(models.Model):
    _name = 'tenant.co_signer'
    _description = 'Tenant Co-Signer'

    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)

    # Información del Avalista (co-signer)
    name = fields.Char(string='Full Name', required=True)
    identification_number = fields.Char(string='DNI/NIE', required=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    bank_account_number = fields.Char(string='Bank Account Number')
    employment_status = fields.Selection(
        [('employed', 'Employed'), ('unemployed', 'Unemployed'), ('self_employed', 'Self-employed'),
         ('student', 'Student')],
        string='Employment Status'
    )
    monthly_income = fields.Float(string='Monthly Income')


class RentalPaymentHistory(models.Model):
    _name = 'rental.payment.history'
    _description = 'Rental Payment History'

    name = fields.Char(string='Rental Payment History', required=True, copy=False, readonly=True, default='New')
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    payment_date = fields.Date(string='Payment Date', required=True)
    amount_paid = fields.Float(string='Amount Paid', required=True)
    payment_method = fields.Selection(
        [('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('card', 'Credit/Debit Card')],
        string='Payment Method'
    )
    is_on_time = fields.Boolean(string='Payment On Time', default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.payment.history') or 'New'
        return super(RentalPaymentHistory, self).create(vals)

class RentalIncidentHistory(models.Model):
    _name = 'rental.incident.history'
    _description = 'Incident History'

    name = fields.Char(string='Incident History', required=True, copy=False, readonly=True, default='New')
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    incident_date = fields.Date(string='Incident Date', required=True)
    description = fields.Text(string='Description of the Incident')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.incident.history') or 'New'
        return super(RentalIncidentHistory, self).create(vals)

class RentalCommunicationHistory(models.Model):
    _name = 'rental.communication.history'
    _description = 'Communication History'

    name = fields.Char(string='Communication History', required=True, copy=False, readonly=True, default='New')
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    communication_date = fields.Date(string='Communication Date', required=True)
    communication_type = fields.Selection(
        [('email', 'Email'), ('phone', 'Phone Call'), ('in_person', 'In-Person')],
        string='Communication Type'
    )
    description = fields.Text(string='Details of Communication')
    attachment = fields.Binary(string='Attachment')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.communication.history') or 'New'
        return super(RentalCommunicationHistory, self).create(vals)