from odoo import models, fields, api

class MantenimientoCalendar(models.Model):
    _name = "calendar.maintenance"
    _description = "Calendario del Mantenimeinto de Viviendas/Habitaciones"

    name = fields.Char('Nombre del evento', required=True)
    start_day = fields.Datetime('Dia inicio', required=True)
    end_day = fields.Datetime('Dia final', required=True)
    description = fields.Text('Descripción')
    employer = fields.Many2one('hr.employee', string="Empleado", required=True)

