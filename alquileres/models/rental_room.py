from odoo import models, fields, api


# Gestionar habitaciones dentro de una vivienda, como un piso compartido
class RentalRoom(models.Model):
    _name = "rental.room"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Room Management"

    # Información Básica
    name = fields.Char(
        string="Room", required=True, copy=False, readonly=True, default="New"
    )
    size_m2 = fields.Float(string="Size (m²)")
    room_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("double", "Double"),
            ("triple", "Triple"),
            ("other", "Other"),
        ],
        string="Room Type",
        required=True,
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
    rental_price = fields.Float(string="Rental Price")

    # Equipamiento
    furniture_list = fields.Many2many(
        comodel_name="furniture.room.item", string="Furniture List"
    )  # E.g. Bed, Desk, Wardrobe, etc.
    services_included = fields.Many2many(
        comodel_name="services.room.item", string="Furniture List"
    )  # E.g. Internet, Heating, etc.

    # Historial
    occupancy_history_ids = fields.One2many(
        "rental.room.occupancy", "room_id", string="Occupancy History"
    )
    maintenance_history_ids = fields.One2many(
        "rental.room.maintenance", "room_id", string="Maintenance History"
    )

    # Documentación
    room_inventory = fields.Text(
        string="Room Inventory"
    )  # List of furniture and their conditions
    room_photos = fields.Many2many(
        comodel_name="ir.attachment",
        relation="m2m_ir_attachment_relation",
        column1="m2m_id",
        column2="attachment_id",
        string="Room Pictures",
    )

    @api.constrains("size_m2")
    def _check_room_size(self):
        for room in self:
            if room.size_m2 <= 0:
                raise models.ValidationError("Room size must be greater than 0 m².")

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("rent.room") or "New"
        return super(RentalRoom, self).create(vals)


# furniture.room.item y services.room.item son modelos que se crean en el siguiente snippet
class FurnitureRoomItem(models.Model):
    _name = "furniture.room.item"
    _description = "Furniture Items for Room"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


class ServicesRoomItem(models.Model):
    _name = "services.room.item"
    _description = "Services Items for Room"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")


# para los registros de historial de ocupación
class RentalRoomOccupancy(models.Model):
    _name = "rental.room.occupancy"
    _description = "Room Occupancy History"

    name = fields.Char(
        string="Room Occupancy History",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    room_id = fields.Many2one("rental.room", string="Room", required=True)
    tenant_id = fields.Many2one("res.partner", string="Tenant", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date")

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise models.ValidationError(
                    "The end date must be after the start date."
                )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("rent.room.occupancy") or "New"
            )
        return super(RentalRoomOccupancy, self).create(vals)


# para los registros de historial de mantenimiento
class RentalRoomMaintenance(models.Model):
    _name = "rental.room.maintenance"
    _description = "Room Maintenance History"

    name = fields.Char(
        string="Room Maintenance History",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )
    room_id = fields.Many2one("rental.room", string="Room", required=True)
    maintenance_date = fields.Date(string="Maintenance Date", required=True)
    made_by = fields.Char(string="Made By", required=True)
    description = fields.Text(string="Description of Maintenance or Repair")

    @api.constrains("maintenance_date")
    def _check_maintenance_date(self):
        for record in self:
            if record.maintenance_date > fields.Date.today():
                raise models.ValidationError(
                    "Maintenance date cannot be in the future."
                )

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("rent.room.maintenance") or "New"
            )
        return super(RentalRoomMaintenance, self).create(vals)
