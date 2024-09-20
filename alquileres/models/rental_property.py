#Modelo Odoo: Gestión de Viviendas
from odoo import models, fields, api

class RentalProperty(models.Model):
    _name = 'rental.property'
    _description = 'Property Management'

    # Información Básica
    name = fields.Char(string='Full Address', required=True)
    property_type = fields.Selection(
        [('apartment', 'Apartment'), ('house', 'House')],
        string='Property Type',
        required=True
    )
    number_of_rooms = fields.Integer(string='Number of Rooms', required=True)
    number_of_bathrooms = fields.Integer(string='Number of Bathrooms', required=True)
    size_m2 = fields.Float(string='Surface Area (m²)', required=True)
    floor = fields.Char(string='Floor (if applicable)')
    door_number = fields.Char(string='Door Number (if applicable)')

    # Datos de Propiedad
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    property_reference = fields.Char(string='Property Reference Number', required=True)
    property_status = fields.Selection(
        [('available', 'Available'), ('rented', 'Rented'), ('maintenance', 'Under Maintenance')],
        string='Current Status',
        required=True,
        default='available'
    )
    rental_price_per_room = fields.Float(string='Rental Price per Room')

    # Historial de Propiedad
    tenant_history_ids = fields.One2many(
        'rental.property.tenant.history', 'property_id',
        string='Tenant History'
    )
    # Historial de Mantenimiento
    maintenance_history_ids = fields.One2many(
        'rental.property.maintenance', 'property_id',
        string='Maintenance History'
    )
    # Historial de Contratos
    contract_history_ids = fields.One2many(
        'rental.contract', 'property_id',
        string='Contract History'
    )

    # Documentación
    property_deed = fields.Binary(string='Property Deed')
    energy_certificate = fields.Binary(string='Energy Efficiency Certificate')
    habitability_certificate = fields.Binary(string='Habitability Certificate')
    special_permits = fields.Binary(string='Special Permits or Licenses')

    @api.constrains('number_of_rooms', 'number_of_bathrooms', 'size_m2')
    def _check_validations(self):
        for property in self:
            if property.number_of_rooms <= 0:
                raise models.ValidationError('The property must have at least one room.')
            if property.number_of_bathrooms <= 0:
                raise models.ValidationError('The property must have at least one bathroom.')
            if property.size_m2 <= 0:
                raise models.ValidationError('The surface area must be greater than 0 m².')


# para los registros de historial de inquilinos
class RentalPropertyTenantHistory(models.Model):
    _name = 'rental.property.tenant.history'
    _description = 'Tenant History'

    property_id = fields.Many2one('rental.property', string='Property', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    contract_id = fields.Many2one('rental.contract', string='Contract', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')


# para los registros de historial de mantenimiento
class RentalPropertyMaintenance(models.Model):
    _name = 'rental.property.maintenance'
    _description = 'Maintenance History'

    property_id = fields.Many2one('rental.property', string='Property', required=True)
    maintenance_date = fields.Date(string='Maintenance Date', required=True)
    description = fields.Text(string='Description of Maintenance or Repair')
    made_by = fields.Char(string='Maintenance Made By')
    cost = fields.Float(string='Cost of Maintenance or Repair')
