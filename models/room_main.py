import random
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date

class RoomMain(models.Model):
    _name = "room.main"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Room Management"

    name = fields.Char(
        string="Room", required=True, copy=False, readonly=True, default=lambda self: 'Nuevo'
    )
    property_id = fields.Many2one('property.main', string='Propiedad Asociada', readonly=True)
    tenant_id = fields.Many2one('res.partner', string='Inquilino Actual', store=True) 
    tenant_ids = fields.One2many(
        "res.partner",
        "room_id",
        domain="[('owner_or_tenant', '=', 'tenant')]",
    )
    num_recibo = fields.Char(string="Número de Recibo")
    booking_amount = fields.Float(string="Importe de Reserva")
    issue_date = fields.Date(string="Fecha de Emisión")
    due_date = fields.Date(string="Fecha de Vencimiento")
    iva = fields.Many2one(
        'account.tax',
        string="Impuesto",
        domain="[('type_tax_use', 'in', ['sale', 'purchase'])]",
        help="Selecciona el impuesto aplicable."
    )

    company_id = fields.Many2one(
        'res.company', string='Compañía',
        default=lambda self: self.env.company
    )

    irpf = fields.Float(string="IRPF (%)", digits=(6, 2))
    size_m2 = fields.One2many("room.sections", "room_id", string="Seciones")
    responsible_id = fields.Many2one("res.users", string="Responsable")
    room_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("double", "Doble"),
            ("triple", "Triple"),
            ("other", "Otros"),
        ],
        string="Tipo de habitación",
    )
    status = fields.Selection(
        [   
            ("draft", "Borrador"),
            ("available", "Disponible"),
            ("booked", "Reservado"),
            ("occupied", "Ocupado"),
            ("maintenance", "Bajo Mantenimiento"),
        ],
        string="Estado actual",
        required=True,
        default="available",
    )
    rental_price = fields.Float(string="Precio de la renta")

    
    # furniture_list = fields.Many2many(
    #     comodel_name="furniture.item",
    #     string="Furniture List",
    #     options={"color_field": "color"},
    # )  
    # services_included = fields.Many2many(
    #     comodel_name="services.item",
    #     string="Services List",
    #     options={"color_field": "color"},
    # )  

    occupancy_history_ids = fields.One2many(
        "room.main.occupancy", "room_id", string="Historial de occupacion"
    )
    occupancy_history_count = fields.Integer(compute="_compute_occupancy_history")

    maintenance_history_ids = fields.One2many(
        "maintenance.main",  
        "room_propierty_reference",
        string="Historial de mantenimeinto"
    )

    maintenance_history_count = fields.Integer(
        compute="_compute_maintenance_history",
        string="Maintenance Count"
    )


    room_photos = fields.Many2many(
        comodel_name="ir.attachment",
        relation="m2m_ir_attachment_relation",
        column1="m2m_id",
        column2="attachment_id",
        string="Fotos de la habitación",
    )
    image_1920 = fields.Binary(
        "Imagen", attachment=True
    )
    image_filename = fields.Char(
        "Image Filename"
    )
    has_a_tenant = fields.Boolean(compute="_compute_occupants")
    description = fields.Html(string="Descripción")
    color = fields.Integer(string="Color Index")
    is_room = fields.Boolean(string="is_room", default=True)

    #Reservas
    booking_history_count = fields.Integer(compute="_compute_booking_history")
    booking_history_ids = fields.One2many('booking.history', 'room_id', string = 'Historila de reservas')

    cosginer_ids = fields.Many2one('cosigner_main', string='Prestamos', related='tenant_id')

    #Contratos
    contract_history_ids = fields.One2many(
        'room.contract', 'room_id',
        string='Contract History'
    )
    contract_history_count = fields.Integer(compute="_compute_contract_history")
    contract_open = fields.Many2one("room.contract", string="Contrato Abierto", store=True)

    #Seguro de Pago 
    payment_insurance = fields.Boolean(string="Seguro de Pago")
    additional_delivery = fields.Boolean(string="Entrega adicional", default=False)
    insurance_date = fields.Date(string="Fecha seguro")
    policy_amount = fields.Integer(string="Monto del Seguro")
    months_remaining = fields.Integer(string="Meses de contrato", compute="_compute_month_remaining", store=True)

    furniture_list = fields.Many2many(comodel_name="furniture.item", string="Lista de Muebles")
    
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

    def open_payment_insurance(self):
        """Abrir el wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wizard para Seguro de Pago',
            'res_model': 'wizard.payment.insurance',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_room_id': self.id,
            },
        }
    
    @api.onchange('property_id')
    def onchange_property_id(self):
        if self.property_id:
            self.env['property.main'].browse(self.property_id.id).write({
                'room_ids': [(4, self.id)]
            })
    
    @api.depends("tenant_ids")
    def _compute_occupants(self):
        for record in self:
            record.has_a_tenant = bool(record.tenant_ids)

    def return_action_view_xml_id_occupacity(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if (xml_id is not None):
            action = self.env["ir.actions.act_window"]._for_xml_id(
                f"alquileres.{xml_id}"
            )
            action.update(
                context=dict(
                    self.env.context, default_rental_room_id=self.id, group_by=False
                ),
                domain=[("room_id", "=", self.id)],
            )
            return action
        return False

    def return_action_view_xml_id_contract(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id is not None:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                f"alquileres.{xml_id}"
            )
            action.update(
                context=dict(
                    self.env.context, default_rental_room_id=self.id, group_by=False
                ),
                domain=[("room_id", "=", self.id)],
            )
            return action
        return False

    def return_action_view_xml_id_maintenance(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id is not None:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                f"alquileres.{xml_id}"
            )
            action.update(
                context=dict(
                    self.env.context, default_rental_room_id=self.id, group_by=False
                ),
                domain=[("room_propierty_reference", "=", f"room.main,{self.id}")],
            )
            return action
        return False

    def return_action_view_xml_id_booking(self):
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id is not None:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                f"alquileres.{xml_id}"
            )
            action.update(
                context=dict(
                    self.env.context, default_rental_room_id=self.id, group_by=False
                ),
                domain=[("room_id", "=", self.id)],
            )
            return action
        return False
    
    @api.model
    def create(self, vals):
        """Crea la habitación con su número de secuencia, asigna un color aleatorio y agrega un mensaje en el chatter."""
        with self.env.cr.savepoint():
            # Generar secuencia y asignar color aleatorio si es necesario
            if vals.get("name", "Nuevo") == "Nuevo":
                vals["name"] = self.env["ir.sequence"].next_by_code("room.main.sequence") or "Nuevo"
                vals["color"] = random.randint(1, 11)
            
            # Crear el registro
            record = super(RoomMain, self).create(vals)
            
            # Publicar mensaje en el chatter
            record.message_post(
                body=_("La habitación '%s' ha sido creada con éxito con el color asignado.") % record.name,
                subject=_("Nueva Habitación Creada"),
                message_type="notification"
            )
            
        return record


    @api.depends("maintenance_history_ids")
    def _compute_maintenance_history(self):
        self.maintenance_history_count = (
            len(self.maintenance_history_ids) if self.maintenance_history_ids else 0
        )

    @api.depends("occupancy_history_ids")
    def _compute_occupancy_history(self):
        self.occupancy_history_count = (
            len(self.occupancy_history_ids) if self.occupancy_history_ids else 0
        )
    
    @api.depends('contract_history_ids')
    def _compute_contract_history(self):
        self.contract_history_count = len(self.contract_history_ids) if self.contract_history_ids else 0

    def action_change_status(self):
        for record in self:
            if record.status == "draft":
                record.status = "available"
            elif record.status == "available":
                record.status = "booked"            
            elif record.status == "booked":
                if not record.tenant_id:
                    raise ValueError(_("El campo 'Inquilino' es obligatorio para crear una reserva."))

                booking_vals = {
                    'tenant_id': record.tenant_id.id,  # Correcto porque es Many2one
                    'room_id': record.id,  # Correcto porque es el ID del registro actual
                    'booking_amount': record.booking_amount,  # Solo el valor flotante
                    'issue_date': record.issue_date,  # Solo el valor de la fecha
                    'due_date': record.due_date,  # Solo el valor de la fecha
                    'iva': record.iva,  # Solo el valor flotante
                    'irpf': record.irpf,  # Solo el valor flotante
}


                self.env['booking.history'].create(booking_vals)
                record.status = "occupied"
            elif record.status == "occupied":
                record.status = "maintenance"
            else:
                record.status = "draft"
                record.tenant_id = False
    
    def print_booking_recipe(self):
        return self.env.ref('alquileres.print_booking_recipe').report_action(self)

    def print_booked_room(self):
        return self.env.ref('alquileres.print_booked_room').report_action(self)
    
    def action_termination_room(self):
        return self.env.ref('alquileres.print_termination_room').report_action(self)
    
    @api.depends("booking_history_ids")
    def _compute_booking_history(self):
        self.booking_history_count = (
            len(self.booking_history_ids) if self.booking_history_ids else 0
        )

class RoomSections(models.Model):
    _name = "room.sections"
    _description = "Sections"

    name = fields.Char(string="Seccion", required=True)
    height = fields.Float(string="Altura (m)", required=True)
    width = fields.Float(string="Anchura (m)", required=True)
    area = fields.Float(compute="_compute_area", string="Área (m²)")
    room_id = fields.Many2one("rental.room", string="Room")

    @api.depends("height", "width")
    def _compute_area(self):
        if self.height > 0 and self.width > 0:
            self.area = float(self.height * self.width)
        else:
            self.area = 0

