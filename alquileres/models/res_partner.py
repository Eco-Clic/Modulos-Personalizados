# Modelo Odoo: Gestión de Inquilinos (Extendiendo res.partner)

from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = 'res.partner'

    # Información Personal
    birth_date = fields.Date(string='Date of Birth')
    identification_number = fields.Char(string='DNI/NIE', required=True)
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced')],
        string='Marital Status'
    )
    nationality = fields.Char(string='Nationality')
    phone = fields.Char(string='Phone Number', required=True)
    email = fields.Char(string='Email', required=True)
    bank_account_number = fields.Char(string='Bank Account Number')
    address = fields.Char(string='Address')
    employment_status = fields.Selection(
        [('employed', 'Employed'), ('unemployed', 'Unemployed'), ('self_employed', 'Self-employed'),
         ('student', 'Student')],
        string='Employment Status'
    )
    monthly_income = fields.Float(string='Monthly Income')

    # Información de Alquiler
    property_id = fields.Many2one('rental.property', string='Rented Property')
    room_id = fields.Many2one('rental.room', string='Rented Room')
    lease_start_date = fields.Date(string='Lease Start Date')
    lease_end_date = fields.Date(string='Lease End Date')
    monthly_rent = fields.Float(string='Monthly Rent Amount')
    deposit_amount = fields.Float(string='Deposit Amount')
    guarantees = fields.Text(string='Additional Guarantees (Aval, Insurance, etc.)')

    # Historial
    rental_payment_history_ids = fields.One2many(
        'rental.payment.history', 'tenant_id', string='Rental Payment History'
    )
    incident_history_ids = fields.One2many(
        'rental.incident.history', 'tenant_id', string='Incident History'
    )
    communication_history_ids = fields.One2many(
        'rental.communication.history', 'tenant_id', string='Communication History'
    )

    # Información de los Avalistas (co-signers)
    co_signer_ids = fields.One2many('tenant.co_signer', 'tenant_id', string='Co-Signers')

    # Documentación
    signed_lease_contract = fields.Binary(string='Signed Lease Contract')
    id_document = fields.Binary(string='DNI/NIE or Passport')
    deposit_receipt = fields.Binary(string='Deposit Payment Receipt')
    income_proof = fields.Binary(string='Income Proof (Payslips, Tax Returns, etc.)')
    additional_guarantees = fields.Binary(string='Additional Guarantees (Aval, Insurance, etc.)')

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

    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    payment_date = fields.Date(string='Payment Date', required=True)
    amount_paid = fields.Float(string='Amount Paid', required=True)
    payment_method = fields.Selection(
        [('bank_transfer', 'Bank Transfer'), ('cash', 'Cash'), ('card', 'Credit/Debit Card')],
        string='Payment Method'
    )
    is_on_time = fields.Boolean(string='Payment On Time', default=True)


class RentalIncidentHistory(models.Model):
    _name = 'rental.incident.history'
    _description = 'Incident History'

    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    incident_date = fields.Date(string='Incident Date', required=True)
    description = fields.Text(string='Description of the Incident')


class RentalCommunicationHistory(models.Model):
    _name = 'rental.communication.history'
    _description = 'Communication History'

    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    communication_date = fields.Date(string='Communication Date', required=True)
    communication_type = fields.Selection(
        [('email', 'Email'), ('phone', 'Phone Call'), ('in_person', 'In-Person')],
        string='Communication Type'
    )
    description = fields.Text(string='Details of Communication')
    attachment = fields.Binary(string='Attachment')