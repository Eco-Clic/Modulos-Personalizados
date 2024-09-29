from odoo import models, fields, api

class MaintenanceApartment(models.Model):
    _name = "maintenance.apartment"
    _description = "Mantenimiento"

    name = fields.Char(string="Name")
    details = fields.Text(string="Detalles del Mantenimiento")
    description = fields.Char(string="Descripcion")
    employer = fields.Many2one('hr.employee', string="Empleado", required=True)

