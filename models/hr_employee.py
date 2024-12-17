from odoo import fields, models, api 

class HrEmployers(models.Model):
    _inherit = "hr.employee"

    property_id = fields.Many2one("property.main", string="Propiedad asignada")
