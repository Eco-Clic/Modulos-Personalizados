from odoo import models, fields, api

class Registration(models.Model):
    _name = 'rent.empadronamiento'
    _description = 'Census'

    name = fields.Char(
        string="Registration number", required=True, copy=False, readonly=True, default="New"
    )
    tenant_name = fields.Char(string='Tenants Full Name', required=True)
    address = fields.Char(string='Exact Address of the Home', required=True)
    registration_date = fields.Date(string='Registration Date', required=True)
    id_number = fields.Char(string='Identification Number (DNI/NIE)', required=True)
    relationship = fields.Selection([
        ('family', 'Familiar'),
        ('roommate', 'Compañero de Piso'),
        ('other', 'Otro')
    ], string='Relationship with Other Registered Members', required=True)

    rental_contract = fields.Binary(string='Rental Contract')
    owner_authorization = fields.Binary(string='Authorization of the Owner for Registration')
    tenant_id_copy = fields.Binary(string='Copy of the Tenant DNI/NIE')
    status = fields.Selection([
        ('incomplete', 'Incomplete'),
        ('complete', 'Complete')
    ], string='Registration Status', compute='check_registration_status', store=True)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("rent.empadronamiento") or "New"
        return super(Registration, self).create(vals)

    # Método para verificar que todos los documentos están presentes
    @api.constrains('rental_contract', 'owner_authorization', 'tenant_id_copy')
    def _check_documents(self):
        for record in self:
            if not all([record.rental_contract, record.owner_authorization, record.tenant_id_copy]):
                raise models.ValidationError("Debe proporcionar todos los documentos requeridos.")

    # Método para calcular el estado del empadronamiento basado en la documentación
    def check_registration_status(self):
        for record in self:
            if all([record.rental_contract, record.owner_authorization, record.tenant_id_copy]):
                record.status = 'complete'
            else:
                record.status = 'incomplete'


