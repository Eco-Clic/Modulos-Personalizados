from odoo import models, fields, api, exceptions

class CoSigner(models.Model):
    _name = 'tenant.co_signer'
    _description = 'Avalista del Inquilino'

    tenant_id = fields.Many2one(
        'res.partner', 
        string='Inquilino', 
        required=True
    )

    # Información del Avalista
    name = fields.Char(
        string='Nombre Completo', 
        required=True
    )
    identification_number = fields.Char(
        string='DNI/NIE', 
        required=True
    )
    phone = fields.Char(
        string='Número de Teléfono'
    )
    email = fields.Char(
        string='Correo Electrónico'
    )
    bank_account_number = fields.Char(
        string='Número de Cuenta Bancaria'
    )
    employment_status = fields.Selection(
        [
            ('employed', 'Empleado'), 
            ('unemployed', 'Desempleado'), 
            ('self_employed', 'Autónomo'),
            ('student', 'Estudiante')
        ],
        string='Estado Laboral'
    )
    monthly_income = fields.Float(
        string='Ingresos Mensuales'
    )
