#Modelo Odoo: Gestión de Viviendas
from odoo import models, fields, api

class RentalProperty(models.Model):
    _name = 'rental.property'
    _description = 'Property Management'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Información Básica
    name = fields.Char(string='Property', required=True, copy=False, readonly=True, default='New')
    address = fields.Char(string='Full Address', required=True)
    property_type = fields.Selection(
        [('apartment', 'Apartment'), ('house', 'House')],
        string='Property Type',
        required=True
    )
    status = fields.Selection(
        [
            ("available", "Available"),
            ("occupied", "Occupied"),
            ("maintenance", "Under Maintenance"),
        ],
        string="Current Status",
        required=True,
        default="available",
    )
    rooms = fields.One2many("rental.room","rental_id", string="Rooms")
    number_of_rooms = fields.Integer(string='Number of Rooms', required=True)
    number_of_bathrooms = fields.Integer(string='Number of Bathrooms', required=True)
    size_m2 = fields.Float(string='Surface Area (m²)', required=True)
    floor = fields.Char(string='Floor (if applicable)')
    door_number = fields.Char(string='Door Number (if applicable)')
    is_property = fields.Boolean(string="is_property",default=True)

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
    tenant_history_count = fields.Integer(compute="_compute_tenant_history")

    # Historial de Mantenimiento
    maintenance_history_ids = fields.One2many(
        'rental.property.maintenance', 'property_id',
        string='Maintenance History'
    )
    maintenance_history_count = fields.Integer(compute="_compute_maintenance_history")
    # Historial de Contratos
    contract_history_ids = fields.One2many(
        'rental.contract', 'property_id',
        string='Contract History'
    )
    contract_history_count = fields.Integer(compute="_compute_contract_history")
    # Documentación
    property_deed = fields.Binary(string='Property Deed')
    energy_certificate = fields.Binary(string='Energy Efficiency Certificate')
    energy_certificate_list = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ],
        string='Energy Efficiency Certificate'
    )
    habitability_certificate = fields.Binary(string='Habitability Certificate')
    special_permits = fields.Binary(string='Special Permits or Licenses')
    image_1920 = fields.Binary("Imagen", attachment=True)  # Campo para la imagen del avatar
    image_filename = fields.Char("Image Filename")  # Campo para el nombre del archivo de la imagen
    # Nuevo campo para publicar en el sitio web
    website_published = fields.Boolean(string="Published on Website", default=False)
    tenant_id = fields.Many2one('res.partner', string='Inquilino Actual', store=True)
    contract_open = fields.Many2one("rental.contract", string="Contrato Abierto", store=True)
    description = fields.Text(string='Descripción')

    @api.constrains('number_of_rooms', 'number_of_bathrooms', 'size_m2')
    def _check_validations(self):
        for property in self:
            if property.number_of_rooms <= 0:
                raise models.ValidationError('The property must have at least one room.')
            if property.number_of_bathrooms <= 0:
                raise models.ValidationError('The property must have at least one bathroom.')
            if property.size_m2 <= 0:
                raise models.ValidationError('The surface area must be greater than 0 m².')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.property') or 'New'
        return super(RentalProperty, self).create(vals)


    def return_action_view_xml_id(self):
        """Return action window for xml_id passed through context"""
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id is not None:
            action = self.env['ir.actions.act_window']._for_xml_id(f'alquileres.{xml_id}')
            action.update(
                context=dict(self.env.context, default_rental_property_id=self.id, group_by=False),
                domain=[('property_id', '=', self.id)]
            )
            return action
        return False

    @api.depends('tenant_history_ids')
    def _compute_tenant_history(self):
        self.tenant_history_count = len(self.tenant_history_ids) if self.tenant_history_ids else 0

    @api.depends('maintenance_history_ids')
    def _compute_maintenance_history(self):
        self.maintenance_history_count = len(self.maintenance_history_ids) if self.maintenance_history_ids else 0

    @api.depends('contract_history_ids')
    def _compute_contract_history(self):
        self.contract_history_count = len(self.contract_history_ids) if self.contract_history_ids else 0

    def action_change_status(self):
        for record in self:
            if record.status == 'available':
                record.status = 'occupied'
            elif record.status == 'occupied':
                record.status = 'maintenance'
            else:
                record.status = 'available'
                record.tenant_id = False

    def action_open_check_in_wizard(self):
        # Acción para abrir el wizard de Check-In
        return {
            'name': 'Check-In Wizard',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.check.in.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_property_id': self.id,
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
                'default_property_id': self.id,
            }
        }


# para los registros de historial de inquilinos
class RentalPropertyTenantHistory(models.Model):
    _name = 'rental.property.tenant.history'
    _description = 'Tenant History'

    name = fields.Char(string='Tenant History', required=True, copy=False, readonly=True, default='New')
    property_id = fields.Many2one('rental.property', string='Property', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    contract_id = fields.Many2one('rental.contract', string='Contract', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.tenant.history') or 'New'
        return super(RentalPropertyTenantHistory, self).create(vals)


# para los registros de historial de mantenimiento
class RentalPropertyMaintenance(models.Model):
    _name = 'rental.property.maintenance'
    _description = 'Maintenance History'

    name = fields.Char(string='Maintenance History', required=True, copy=False, readonly=True, default='New')
    property_id = fields.Many2one('rental.property', string='Property', required=True)
    maintenance_date = fields.Date(string='Maintenance Date', required=True)
    description = fields.Text(string='Description of Maintenance or Repair')
    made_by = fields.Char(string='Maintenance Made By')
    cost = fields.Float(string='Cost of Maintenance or Repair')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.property.maintenance') or 'New'
        return super(RentalPropertyMaintenance, self).create(vals)