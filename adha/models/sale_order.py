from odoo import models, fields, api

# -*- coding: utf-8 -*-

from collections import defaultdict
from contextlib import ExitStack, contextmanager
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from hashlib import sha256
from json import dumps
import re
from textwrap import shorten
from unittest.mock import patch

#ADHA

import requests
import re
import qrcode
import base64
from io import BytesIO
from odoo.http import request
from PIL import Image
from pyzbar import pyzbar
from urllib.parse import quote


ADHA_API_URL = "https://api.adhagroup.com/v1/public"

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    adha_qr_code = fields.Binary("QR Code", compute='create_item_in_adha_generate_qr_code', store=True)

    @api.depends('adha_qr_code')
    def create_item_in_adha_generate_qr_code(self):
        print('\n')
        

        pattern = r"\[([^\]]+)\]"
        print("Create invoice in adha")
        print("askjdlajsdklajs ldajs dlkajsd ")
        data = {
            "nombre": "",
            "tipo_equipo": "",
            "otros_datos": "",
            "centro": "",
            "tipo_activo": "factura", # Usado para crear el tipo activo en adha
            "cliente": {}
        }

        line_references = []
        for record in self:
            print("redocr --> ", record)
            for line in record.line_ids:
                if line.display_type == 'product':
                    text = line.name
                    reference = None
                    if text:
                        reference = re.search(pattern, text)
                    if reference:
                        line_references.append(reference.group(1))
                    
                    # remove_ref_from_text = re.sub(pattern, "", text)

            #if len(line_references) == 0:
            #    continue

            data["nombre"] = record.name
            if len(line_references) > 0:
                data["otros_datos"] = ','.join(line_references)

            print("\n\n\n recorparner", dir(record.partner_id))

            data["tipo_equipo"] = "factura_venta"
            data["centro"] = record.company_id.email
            data["cliente"] = {
                "nombre": record.partner_id.display_name,
                "apellidos": "",
                "nif": record.partner_id.vat,
                "direccion": record.partner_id.contact_address,
            }
            print("data --> ", data)

            url_qr = ""
            if self.env.context.get('from_button_click', False):
                print("Create asset in adha")
                data = dumps(data)
                response = requests.post(f"{ADHA_API_URL}/equipos/create-external/?is_from_odoo=true", 
                    data=data,
                    headers={"Content-Type": "application/json"},
                )
                response_data = response.json() 
                extra_data = response_data['extra_data']
                url_qr = extra_data.get("url_qr")
                id_equipo_adha = extra_data.get("id")
                # url_qr = "https://google.com"

            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4,
            )
            qr.add_data(url_qr)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            record.update({'adha_qr_code': qr_image})

            # Save QR CODE into ADHA
            if self.env.context.get('from_button_click', False):
                print("Save QR into adha")
                # Generar el informe PDF de la factura
                binary_pdf, type_file = self.env['ir.actions.report']._render_qweb_pdf("account.report_invoice", self.id)
                pdf_buffer = BytesIO(binary_pdf)
                files = {'binary_pdf': ('document.pdf', pdf_buffer, 'application/pdf')}

                print("data_pdf --> ", files)
                response_data_pdf = requests.post(f"{ADHA_API_URL}/{id_equipo_adha}/equipos/guardar-documento/?is_binary=true&tipo_odoo=factura",
                    files=files,
                )
                print("response_data --> ", response_data_pdf)
                if response_data_pdf.status_code == 200:
                    print("Guardado el pdf en adha")


        print('\n')
        return True

    def _get_adha_qr_code(self):
        """ Return the adha QR CODE """
        self.ensure_one()

        if self.adha_qr_code:
            return f"data:image/png;base64,{self.adha_qr_code.decode('utf-8')}"

        return False


    def envio_whatsapp(self):
        self.ensure_one()

        if not self.env.context.get('from_button_click', False):
            return False

        if not self.partner_id or not self.partner_id.mobile:
            return False

        if not self.adha_qr_code:
            return False
        
        adha_qr_code = self.adha_qr_code
        decode_b64_qr = base64.b64decode(adha_qr_code)
        image_qr = Image.open(BytesIO(decode_b64_qr))

        decoded_qr = pyzbar.decode(image_qr)
        if not len(decoded_qr) or "data" in decoded_qr[0]:
            print("No se encontraron datos válidos en el QR")
            return False

        url_qr_data = decoded_qr[0].data.decode("utf-8")
        phone_number_whatsapp = self.partner_id.mobile
        text_message_whatsapp = f"Hola, con este link puedes acceder al estado de la reparación: {url_qr_data}"

        # Codificar los parámetros
        phone_param = f'phone={phone_number_whatsapp}'
        text_param = f'text={quote(text_message_whatsapp)}'

        # Construyo la URL completa
        url_whatsapp = f"https://api.whatsapp.com/send/?{phone_param}&{text_param}"
        
        return {
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url_whatsapp,
        }
