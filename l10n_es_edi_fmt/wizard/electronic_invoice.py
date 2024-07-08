import base64
from lxml import etree

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

    # http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml
    def generate_electronic_invoice(self):
        invoice_data = self.env["account.move"].browse(
            self.env.context.get("active_id")
        )

        # Crear el root del XML
        root = etree.Element("Batch")

        # Añadir los elementos al XML
        batch_identifier = etree.SubElement(root, "BatchIdentifier")
        batch_identifier.text = self.assignment_code

        invoices_count = etree.SubElement(root, "InvoicesCount")
        invoices_count.text = "1"

        total_invoices_amount = etree.SubElement(root, "TotalInvoicesAmount")
        total_amount = etree.SubElement(total_invoices_amount, "TotalAmount")
        total_amount.text = str(invoice_data.amount_total)

        total_outstanding_amount = etree.SubElement(root, "TotalOutstandingAmount")
        total_amount_outstanding = etree.SubElement(
            total_outstanding_amount, "TotalAmount"
        )
        total_amount_outstanding.text = str(invoice_data.amount_total)

        total_executable_amount = etree.SubElement(root, "TotalExecutableAmount")
        total_amount_executable = etree.SubElement(
            total_executable_amount, "TotalAmount"
        )
        total_amount_executable.text = str(invoice_data.amount_total)

        invoice_currency_code = etree.SubElement(root, "InvoiceCurrencyCode")
        invoice_currency_code.text = invoice_data.currency_id.name

        # Añadir los detalles del vendedor
        seller_party = etree.SubElement(root, "SellerParty")
        tax_identification = etree.SubElement(seller_party, "TaxIdentification")
        person_type_code = etree.SubElement(tax_identification, "PersonTypeCode")
        person_type_code.text = "F"

        residence_type_code = etree.SubElement(tax_identification, "ResidenceTypeCode")
        residence_type_code.text = "R"

        tax_identification_number = etree.SubElement(
            tax_identification, "TaxIdentificationNumber"
        )
        tax_identification_number.text = invoice_data.partner_id.vat or "-"

        individual = etree.SubElement(seller_party, "Individual")
        name = etree.SubElement(individual, "Name")
        name.text = invoice_data.partner_id.name

        first_surname = etree.SubElement(individual, "FirstSurname")
        first_surname.text = (
            invoice_data.partner_id.name.split()[0]
            if invoice_data.partner_id.name
            else ""
        )

        second_surname = etree.SubElement(individual, "SecondSurname")
        second_surname.text = (
            invoice_data.partner_id.name.split()[1]
            if len(invoice_data.partner_id.name.split()) > 1
            else ""
        )

        address_in_spain = etree.SubElement(individual, "AddressInSpain")
        address = etree.SubElement(address_in_spain, "Address")
        address.text = invoice_data.partner_id.street

        post_code = etree.SubElement(address_in_spain, "PostCode")
        post_code.text = invoice_data.partner_id.zip

        town = etree.SubElement(address_in_spain, "Town")
        town.text = invoice_data.partner_id.city

        province = etree.SubElement(address_in_spain, "Province")
        province.text = invoice_data.partner_id.state_id.name

        country_code = etree.SubElement(address_in_spain, "CountryCode")
        country_code.text = invoice_data.partner_id.country_id.code or ""

        contact_details = etree.SubElement(individual, "ContactDetails")
        electronic_mail = etree.SubElement(contact_details, "ElectronicMail")
        electronic_mail.text = invoice_data.partner_id.email

        # Añadir los detalles del comprador
        buyer_party = etree.SubElement(root, "BuyerParty")
        tax_identification_buyer = etree.SubElement(buyer_party, "TaxIdentification")
        person_type_code_buyer = etree.SubElement(
            tax_identification_buyer, "PersonTypeCode"
        )
        person_type_code_buyer.text = "J"

        residence_type_code_buyer = etree.SubElement(
            tax_identification_buyer, "ResidenceTypeCode"
        )
        residence_type_code_buyer.text = "R"

        tax_identification_number_buyer = etree.SubElement(
            tax_identification_buyer, "TaxIdentificationNumber"
        )
        tax_identification_number_buyer.text = self.code_account_office

        administrative_centres = etree.SubElement(buyer_party, "AdministrativeCentres")

        # Añadir los centros administrativos
        for role, code in [
            ("01", self.code_account_office),
            ("02", self.code_manager_company),
            ("03", self.code_processing_unit),
        ]:
            administrative_centre = etree.SubElement(
                administrative_centres, "AdministrativeCentre"
            )
            centre_code = etree.SubElement(administrative_centre, "CentreCode")
            centre_code.text = code
            role_type_code = etree.SubElement(administrative_centre, "RoleTypeCode")
            role_type_code.text = role

            address_in_spain_centre = etree.SubElement(
                administrative_centre, "AddressInSpain"
            )
            # Company Info in Invoice
            address_centre = etree.SubElement(address_in_spain_centre, "Address")
            address_centre.text = invoice_data.company_id.partner_id.street
            post_code_centre = etree.SubElement(address_in_spain_centre, "PostCode")
            post_code_centre.text = invoice_data.company_id.partner_id.zip
            town_centre = etree.SubElement(address_in_spain_centre, "Town")
            town_centre.text = invoice_data.company_id.partner_id.city
            province_centre = etree.SubElement(address_in_spain_centre, "Province")
            province_centre.text = self.res_state_id.name
            country_code_centre = etree.SubElement(
                address_in_spain_centre, "CountryCode"
            )
            country_code_centre.text = invoice_data.country_code or ""

            centre_description = etree.SubElement(
                administrative_centre, "CentreDescription"
            )
            centre_description.text = (
                "Oficina contable"
                if role == "01"
                else "Órgano gestor"
                if role == "02"
                else "Unidad tramitadora"
            )

        # Añadir la entidad legal del comprador
        legal_entity = etree.SubElement(buyer_party, "LegalEntity")
        corporate_name = etree.SubElement(legal_entity, "CorporateName")
        corporate_name.text = invoice_data.partner_id.display_name
        address_in_spain_legal = etree.SubElement(legal_entity, "AddressInSpain")
        address_legal = etree.SubElement(address_in_spain_legal, "Address")
        address_legal.text = (
            f"{invoice_data.partner_id.street},{invoice_data.partner_id.street2} "
        )
        post_code_legal = etree.SubElement(address_in_spain_legal, "PostCode")
        post_code_legal.text = invoice_data.partner_id.zip or ""
        town_legal = etree.SubElement(address_in_spain_legal, "Town")
        town_legal.text = invoice_data.partner_id.city or ""
        province_legal = etree.SubElement(address_in_spain_legal, "Province")
        province_legal.text = invoice_data.partner_id.state_id.name or ""
        country_code_legal = etree.SubElement(address_in_spain_legal, "CountryCode")
        country_code_legal.text = invoice_data.partner_id.country_id.code or ""

        contact_details_legal = etree.SubElement(legal_entity, "ContactDetails")
        electronic_mail_legal = etree.SubElement(
            contact_details_legal, "ElectronicMail"
        )
        electronic_mail_legal.text = invoice_data.partner_id.email or ""

        invoices_element = etree.SubElement(root, "Invoices")
        invoice_element = etree.SubElement(invoices_element, "Invoice")

        # Invoice Header
        invoice_header_element = etree.SubElement(invoice_element, "InvoiceHeader")
        invoice_number_element = etree.SubElement(
            invoice_header_element, "InvoiceNumber"
        )
        invoice_number_element.text = invoice_data.name
        invoice_series_code_element = etree.SubElement(
            invoice_header_element, "InvoiceSeriesCode"
        )
        invoice_series_code_element.text = self.assignment_code
        invoice_document_type_element = etree.SubElement(
            invoice_header_element, "InvoiceDocumentType"
        )
        invoice_document_type_element.text = invoice_data.move_type
        invoice_class_element = etree.SubElement(invoice_header_element, "InvoiceClass")
        invoice_class_element.text = invoice_data.state

        # Invoice Issue Data
        invoice_issue_data_element = etree.SubElement(
            invoice_element, "InvoiceIssueData"
        )
        issue_date_element = etree.SubElement(invoice_issue_data_element, "IssueDate")
        issue_date_element.text = invoice_data.invoice_date.strftime("%Y-%m-%d")
        invoice_currency_code_element = etree.SubElement(
            invoice_issue_data_element, "InvoiceCurrencyCode"
        )
        invoice_currency_code_element.text = invoice_data.currency_id.name
        tax_currency_code_element = etree.SubElement(
            invoice_issue_data_element, "TaxCurrencyCode"
        )
        tax_currency_code_element.text = invoice_data.tax_country_id.code
        language_name_element = etree.SubElement(
            invoice_issue_data_element, "LanguageName"
        )
        language_name_element.text = "LanguageName"

        # Convertir el árbol XML a una cadena de texto
        xml_string = etree.tostring(
            root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )

        # Codificar el XML en base64
        xml_base64 = base64.b64encode(xml_string)

        # Guardar el XML en el campo binary de la factura
        invoice_data.write(
            {
                "edi_invoice_xml": xml_base64,
                "xml_filename": f"xml_invoice_{invoice_data.name}.xml",
                "electronic_invoice_xml": root,
            }
        )
