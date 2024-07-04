from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    # TODO Llenar cuando se ejecuta el wizard
    electronic_invoice_xml = fields.Html(required=False)

    def action_open_invoice_electronic_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Generar Factura-Electronica",
            "res_model": "electronic.invoice.wizard",
            "view_mode": "form",
            "target": "new",
        }
