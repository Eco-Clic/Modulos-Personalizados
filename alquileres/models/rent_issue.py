from odoo import models, fields

# Registro de problemas en la renta
class Issue(models.Model):
    _name = 'rent.issue'
    _description = 'Issue Management'

    rental_id = fields.Many2one('rental.property', string='Rental')
    room_id = fields.Many2one('rental.room', string='Rental')
    description = fields.Text(string='Issue Description', required=True)
    report_date = fields.Date(string='Report Date', required=True)
    status = fields.Selection([
        ('reported', 'Reported'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ], string='Status', default='reported')
