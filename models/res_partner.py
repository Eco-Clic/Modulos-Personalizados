from odoo import models, fields, api


class Tenant(models.Model):
    _inherit = 'res.partner'

    # Información Personal
    birth_date = fields.Date(string='Fecha de Nacimiento')
    owner_or_tenant = fields.Selection(
        [('owner', 'Propietario'), ('tenant', 'Inquilino')],
        string='Propietario o Inquilino'
    )
    identification_number = fields.Char(string='DNI/NIE', required=True)
    marital_status = fields.Selection(
        [('single', 'Soltero'), ('married', 'Casado'), ('divorced', 'Divorciado')],
        string='Estado Civil'
    )
    nationality = fields.Many2one('res.country', string='Nacionalidad')
    employment_status = fields.Selection(
        [('employed', 'Empleado'), ('unemployed', 'Desempleado'), ('self_employed', 'Autónomo'),
         ('student', 'Estudiante')],
        string='Estado Laboral'
    )
    monthly_income = fields.Float(string='Ingresos Mensuales')

    baild_bound_history_ids = fields.One2many(
        'bail.bounds.history', 'tenant_id', string='Historial de Contratos de Fianzas'
    )

    bail_bound_count = fields.Integer(compute="_compute_bail_bound_count")

    # Historial de pagos 
    payment_history_ids = fields.One2many("payment.history", "tenant_id", string="Historial de deudas")
    payment_count = fields.Integer(compute="_compute_payment_count")

    # Información de Alquiler
    property_id = fields.Many2one('property.main', string='Propiedad Alquilada')
    room_id = fields.Many2one('room.main', string='Habitación Alquilada', domain="[('property_id', '=', property_id)]")
    lease_start_date = fields.Date(string='Fecha de Inicio del Contrato')
    lease_end_date = fields.Date(string='Fecha de Fin del Contrato')
    monthly_rent = fields.Float(string='Monto de Renta Mensual')
    deposit_amount = fields.Float(string='Monto del Depósito')
    guarantees = fields.Text(string='Garantías Adicionales (Aval, Seguro, etc.)')

    # Información de los Avalistas (co-signers)
    co_signer_ids = fields.One2many('tenant.co_signer', 'tenant_id', string='Avalistas')

    # Documentación
    signed_lease_contract = fields.Binary(string='Contrato de Arrendamiento Firmado')
    id_document = fields.Binary(string='DNI/NIE o Pasaporte')
    deposit_receipt = fields.Binary(string='Recibo de Pago del Depósito')
    income_proof = fields.Binary(string='Prueba de Ingresos (Nóminas, Declaraciones, etc.)')
    additional_guarantees = fields.Binary(string='Garantías Adicionales (Aval, Seguro, etc.)')

    # si es Propietario o es Inquilino
    is_owner = fields.Boolean(compute='_compute_is_owner')
    is_tenant = fields.Boolean(compute='_compute_is_tenant')

    # Historial de Contratos
    room_contract_ids = fields.One2many(
        'room.contract', 'tenant_id', string='Historial de Contratos de Alquiler'
    )
    contract_count = fields.Integer(compute="_compute_contract_count")
    
    #Historial de deudas
    debt_hsitory_ids  = fields.One2many("debt.main", "tenant_id", string="Historial de deudas")
    debt_count = fields.Integer(compute="_compute_debt_count")

    #Seguro de pago 
    # payment_insurance = fields.Boolean(string="Seguro de Pago")
    # additional_delivery = fields.Boolean(string="Entrega adicional", default=False)
    # insurance_date = fields.Date(string="Fecha seguro")
    # departure_date = fields.Date(string="Fecha de salida")
    # policy_amount = fields.Integer(string="Monto del Seguro")

    # def open_payment_insurance(self):
    #     """Abrir el wizard"""
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Wizard para Seguro de Pago',
    #         'res_model': 'wizard.payment.insurance.partner',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_partner_id': self.id,
    #         },
    #     }
    
    
    def action_view_contracts(self):
        """Contratos segiun su tipo"""
        self.ensure_one()
        if self.owner_or_tenant == 'owner':
            action = self.env.ref('alquileres.action_property_contract').read()[0]
            action['domain'] = [('owner_id', '=', self.id)]
        elif self.owner_or_tenant == 'tenant':
            action = self.env.ref('alquileres.action_room_contract').read()[0]
            action['domain'] = [('tenant_id', '=', self.id)]
        else:
            action = {'type': 'ir.actions.act_window_close'} 
        return action
    
    @api.depends('room_contract_ids', 'contract_count')
    def _compute_contract_count(self):
        for partner in self:
            try:
                partner.contract_count = len(partner.room_contract_ids) + len(partner.contract_ids)
            except Exception:
                partner.contract_count = 0


    def return_action_view_xml_id(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id is not None:
            action = self.env['ir.actions.act_window']._for_xml_id(f'alquileres.{xml_id}')
            action.update(
                context=dict(self.env.context, default_res_partner_id=self.id, group_by=False),
                domain=[('tenant_id', '=', self.id)]
            )
            return action
        return False

    @api.depends('bail_bound_count')
    def _compute_bail_bound_count(self):
        self.bail_bound_count = len(self.baild_bound_history_ids) if self.baild_bound_history_ids else 0

    @api.depends('communication_history_ids')
    def _compute_communication_history(self):
        self.communication_history_count = len(self.communication_history_ids) if self.communication_history_ids else 0

    @api.depends('payment_count')
    def _compute_payment_count(self):
        self.payment_count = len(self.payment_history_ids) if self.payment_history_ids else 0

    @api.depends('debt_count')
    def _compute_debt_count(self):
        self.debt_count = len(self.debt_hsitory_ids) if self.debt_hsitory_ids else 0
