from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
from datetime import date
from dateutil.relativedelta import relativedelta

class PropiedadPrincipal(models.Model):
    _name = 'property.main'
    _description = 'Gestión de Propiedades'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Información Básica
    name = fields.Char(string='Propiedad', required=True, copy=False, readonly=True, default='Nuevo')
    address = fields.Char(string='Dirección Completa', required=True)
    property_type = fields.Selection(
        [('apartment', 'Apartamento'), ('house', 'Casa')],
        string='Tipo de Propiedad',
        required=True
    )
    status = fields.Selection(
        [
            ("available", "Disponible"),
            ("occupied", "Ocupada"),
            ("maintenance", "En Mantenimiento"),
        ],
        string="Estado Actual",
        required=True,
        default="available",
    )
    
    room_ids = fields.One2many("room.main", "property_id", string="Habitaciones")
    number_of_rooms = fields.Integer(string='Número de Habitaciones', required=True)
    number_of_bathrooms = fields.Integer(string='Número de Baños', required=True)
    size_m2 = fields.Float(string='Superficie (m²)', required=True)
    floor = fields.Char(string='Piso (si aplica)')
    door_number = fields.Char(string='Número de Puerta (si aplica)')
    is_property = fields.Boolean(string="Es Propiedad", default=True)

    furniture_list = fields.Many2many(comodel_name="furniture.item", string="Lista de Muebles")
    service_list = fields.Many2many(comodel_name="service.item", string="Lista de Servicios")

    number_of_keys = fields.Integer(string="Número de Llaves", default=0)

    # Datos de Propiedad
    owner_id = fields.Many2one('res.partner', string='Propietario', required=True)
    property_reference = fields.Char(string='Número de Referencia de la Propiedad', required=True)
    property_status = fields.Selection(
        [('available', 'Disponible'), ('rented', 'Alquilada'), ('maintenance', 'En Mantenimiento')],
        string='Estado Actual',
        required=True,
        default='available'
    )

    # Historial de Contratos
    contract_history_ids = fields.One2many(
        'property.contract', 'property_id',
        string='Historial de Contratos'
    )
    contract_history_count = fields.Integer(compute="_compute_contract_history")

    # Documentación
    property_deed = fields.Binary(string='Escritura de Propiedad')
    energy_certificate = fields.Binary(string='Certificado de Eficiencia Energética')
    energy_certificate_list = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G')],
        string='Clasificación de Eficiencia Energética'
    )
    habitability_certificate = fields.Binary(string='Certificado de Habitabilidad')
    special_permits = fields.Binary(string='Permisos o Licencias Especiales')
    image_1920 = fields.Binary(string="Imagen", attachment=True)  
    image_filename = fields.Char(string="Nombre del Archivo de Imagen") 
    contract_open = fields.Many2one("property.contract", string="Contrato Abierto", store=True)
    description = fields.Text(string='Descripción')

    months_remaining = fields.Integer(string="Meses de contrato", compute="_compute_month_remaining", store=True)

    @api.constrains('number_of_rooms', 'number_of_bathrooms', 'size_m2')
    def _check_validations(self):
        for property in self:
            if property.number_of_rooms <= 0:
                raise models.ValidationError('La propiedad debe tener al menos una habitación.')
            if property.number_of_bathrooms <= 0:
                raise models.ValidationError('La propiedad debe tener al menos un baño.')
            if property.size_m2 <= 0:
                raise models.ValidationError('La superficie debe ser mayor a 0 m².')

    @api.depends('contract_history_ids')
    def _compute_contract_history(self):
        self.contract_history_count = len(self.contract_history_ids) if self.contract_history_ids else 0

    @api.model
    def create(self, vals):
        # Deshabilitar el seguimiento temporalmente
        with self.env.cr.savepoint():
            self = self.with_context(tracking_disable=True)
            # Generar el nombre automáticamente si es "Nuevo"
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('property.main.sequence') or 'Nuevo'
            # Crear el registro
            record = super(PropiedadPrincipal, self).create(vals)
        
        # Publicar un mensaje personalizado en el Chatter
        record.message_post(
            body=_("La propiedad %s ha sido creada con éxito.") % record.name,
            subject=_("Nueva Propiedad Creada"),
            message_type="notification"
        )
        
        return record

    def return_action_view_xml_id_contract(self):
        """Devuelve la acción de ventana para el xml_id pasado a través del contexto"""
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

    def action_change_status(self):
        for record in self:
            if record.status == 'available':
                record.status = 'occupied'
            elif record.status == 'occupied':
                record.status = 'maintenance'
            else:
                record.status = 'available'

    @api.depends('contract_history_ids.status', 'contract_history_ids.contract_start_date', 'contract_history_ids.contract_end_date')
    def _compute_month_remaining(self):
        for record in self:
            # Filtrar contratos abiertos
            open_contracts = record.contract_history_ids.filtered(lambda c: c.status == 'open')
            # Seleccionar el contrato más reciente (ordenado por fecha de inicio)
            recent_contract = open_contracts.sorted(key=lambda c: c.contract_start_date, reverse=True)[:1]
            if recent_contract:
                contract = recent_contract[0]
                if contract.contract_start_date and contract.contract_end_date:
                    today = fields.Date.today()
                    if today <= contract.contract_end_date:
                        # Calcular meses restantes
                        diff = relativedelta(contract.contract_end_date, today)
                        months = (diff.months + diff.years * 12) + 2
                        record.months_remaining = months
                    else:
                        record.months_remaining = 0
                else:
                    record.months_remaining = 0
            else:
                record.months_remaining = 0
        

