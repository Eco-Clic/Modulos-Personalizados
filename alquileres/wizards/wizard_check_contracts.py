from odoo import api, fields, models

class RentalCheckInWizard(models.TransientModel):
    _name = 'rental.check.in.wizard'
    _description = 'Wizard for Rental Check-In Contracts'

    property_id = fields.Many2one('rental.property', string='Property', required=True)
    room_id = fields.Many2one('rental.room', string='Room', required=True)
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    agency_id = fields.Many2one('res.partner', string='Agency', required=False)
    contract_start_date = fields.Date(string='Start Date', required=True)
    contract_end_date = fields.Date(string='End Date', required=True)
    renewal_terms = fields.Text(string='Renewal or Termination Conditions')

    def action_create_contract(self):
        # Crear el contrato basado en los datos del wizard
        contract = self.env['rental.contract'].create({
            'property_id': self.property_id.id,
            'room_id': self.room_id.id,
            'owner_id': self.owner_id.id,
            'tenant_id': self.tenant_id.id,
            'agency_id': self.agency_id.id,
            'contract_start_date': self.contract_start_date,
            'contract_end_date': self.contract_end_date,
            'renewal_terms': self.renewal_terms,
            'status': 'draft',
        })

        # Abrir el contrato recién creado en vista de formulario
        return {
            'name': 'Rental Contract',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.contract',
            'view_mode': 'form',
            'res_id': contract.id,
            'target': 'current',
        }

class RentalCheckOutWizard(models.TransientModel):
    _name = 'rental.check.out.wizard'
    _description = 'Wizard for Rental Check-Out Contracts'

    property_id = fields.Many2one('rental.property', string='Property', required=True)
    room_id = fields.Many2one('rental.room', string='Room', required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', required=True)
    contract_id = fields.Many2one('rental.contract', string='Contract', required=True)

    def action_terminate_contract(self):
        # Encontrar el contrato y marcarlo como terminado
        contract = self.contract_id
        if contract:
            contract.write({'status': 'closed'})
        # Abrir el contrato terminado en vista de formulario
        return {
            'name': 'Rental Contract',
            'type': 'ir.actions.act_window',
            'res_model': 'rental.contract',
            'view_mode': 'form',
            'res_id': contract.id,
            'target': 'current',
        }
