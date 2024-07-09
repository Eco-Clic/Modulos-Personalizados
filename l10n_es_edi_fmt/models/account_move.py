import os

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    # TODO Llenar cuando se ejecuta el wizard
    electronic_invoice_xml = fields.Html(required=False)
    edi_invoice_xml = fields.Binary(string="Electronic Invoice XML", attachment=True)
    xml_filename = fields.Char(string="XML Filename")
    attachment_id = fields.Many2one('ir.attachment', 'Attachment')
    edi_invoice_xml_url = fields.Char(compute="_get_edi_invoice_xml_url", store=True)

    def save_binary_file_attachment(self):
        """Save the binary file as attachment in the model"""
        if self.edi_invoice_xml and self.xml_filename:
            attachment = self.env['ir.attachment'].create({
                'name': self.xml_filename,
                'mimetype': "xml",
                'datas': self.edi_invoice_xml,
            })
            self.attachment_id = attachment.id

    @api.depends("edi_invoice_xml")
    def _get_edi_invoice_xml_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for item in self:
            if item.edi_invoice_xml:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", self._name),
                        ("res_field", "=", "edi_invoice_xml"),
                        ("res_id", "=", item.id),
                    ]
                )
                attachment.update({"public": True})
                item.edi_invoice_xml_url = f"{base_url}/web/content/" + str(attachment.id)

    def action_open_invoice_electronic_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Generar Factura-Electronica",
            "res_model": "electronic.invoice.wizard",
            "view_mode": "form",
            "target": "new",
        }
