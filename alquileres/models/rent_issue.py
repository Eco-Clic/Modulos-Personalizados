from odoo import models, fields,api

# Registro de problemas en la renta
class Issue(models.Model):
    _name = 'rent.issue'
    _description = 'Issue Management'

    name = fields.Char(string='Issue', required=True, copy=False, readonly=True, default='New')
    rental_id = fields.Many2one('rental.property', string='Rental')
    room_id = fields.Many2one('rental.room', string='Room')
    description = fields.Text(string='Issue Description', required=True)
    report_date = fields.Date(string='Report Date', required=True)
    status = fields.Selection([
        ('reported', 'Reported'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ], string='Status', default='reported')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('rent.issue') or 'New'
        return super(Issue, self).create(vals)
