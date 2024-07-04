from odoo import models, fields


class ElectronicInvoice(models.TransientModel):
    _name = "electronic.invoice.wizard"
    _description = "Generar Factura-Electronica"

    initial_date = fields.Date(string="Fecha inicio")
    end_date = fields.Date(string="Fecha fin")
    legal_references = fields.Char(string="Referencias legales")
    include_invoices_ref = fields.Boolean(string="Incluir albaranes referenciados")

    code_account_office = fields.Char(string="Código de oficina contable")
    code_manager_company = fields.Char(string="Código de órgano gestor")
    code_processing_unit = fields.Char(string="Código de unidad tramitadora")
    code_proposing_unit = fields.Char(string="Código de órgano proponente")
    assignment_code = fields.Char(string="Código de asignación")
    res_state_id = fields.Many2one(
        comodel_name="res.country.state",
        domain=[("country_id", "=", "es")],  # Filter by country code 'es' (Spain)
        string="Provincias",
        required=False,
    )

    def generate_electronic_invoice(self):
        # Aquí puedes agregar la lógica para generar la factura-e
        return {"type": "ir.actions.act_window_close"}
