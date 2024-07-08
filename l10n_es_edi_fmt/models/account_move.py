import os

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    # TODO Llenar cuando se ejecuta el wizard
    electronic_invoice_xml = fields.Html(required=False)
    edi_invoice_xml = fields.Binary(string="Electronic Invoice XML", attachment=True)
    edi_invoice_xml_url = fields.Char()
    xml_filename = fields.Char(string="XML Filename")

    binary_data = fields.Binary('Binary Data')
    filename = fields.Char('Filename')
    file_format = fields.Char('File Format')
    attachment_id = fields.Many2one('ir.attachment', 'Attachment')

    def save_binary_file(self, file_path):
        with open(file_path, 'rb') as f:
            binary_data = f.read()

        filename = os.path.basename(file_path)
        file_format = filename.split('.')[-1]

        attachment = self.env['attachment'].create({
            'name': filename,
            'mimetype': file_format,
            'data': binary_data,
        })

        self.attachment_id = attachment.id

    def get_filename(self):
        return self.attachment_id.name if self.attachment_id else ''

    def get_file_format(self):
        return self.attachment_id.mimetype if self.attachment_id else ''

    def action_open_invoice_electronic_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Generar Factura-Electronica",
            "res_model": "electronic.invoice.wizard",
            "view_mode": "form",
            "target": "new",
        }
