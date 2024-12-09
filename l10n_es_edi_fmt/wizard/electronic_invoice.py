import base64
from lxml import etree

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


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

        # Crear los root del XML
        root = etree.Element("ns3Facturae")
        header_tag = etree.SubElement(root, "FileHeader")
        parties_tag = etree.SubElement(root, "Parties")
        invoices_element = etree.SubElement(root, "Invoices")

        # FileHeader
        schema_tag = etree.SubElement(header_tag, "SchemaVersion")
        schema_tag.text = "3.2.2"
        modality_tag = etree.SubElement(header_tag, "Modality")
        modality_tag.text = "I"
        issuer_tag = etree.SubElement(header_tag, "InvoiceIssuerType")
        issuer_tag.text = "EM"

        # Añadir los elementos al XML <Batch>
        batch_tag = etree.SubElement(header_tag, "Batch")
        batch_identifier = etree.SubElement(batch_tag, "BatchIdentifier")
        batch_identifier.text = self.assignment_code or ""

        invoices_count = etree.SubElement(batch_tag, "InvoicesCount")
        invoices_count.text = "1"

        total_invoices_amount = etree.SubElement(batch_tag, "TotalInvoicesAmount")
        total_amount = etree.SubElement(total_invoices_amount, "TotalAmount")
        total_amount.text = str(invoice_data.amount_total) or ""

        total_outstanding_amount = etree.SubElement(batch_tag, "TotalOutstandingAmount")
        total_amount_outstanding = etree.SubElement(
            total_outstanding_amount, "TotalAmount"
        )
        total_amount_outstanding.text = str(invoice_data.amount_total)

        total_executable_amount = etree.SubElement(batch_tag, "TotalExecutableAmount")
        total_amount_executable = etree.SubElement(
            total_executable_amount, "TotalAmount"
        )
        total_amount_executable.text = str(invoice_data.amount_total) or ""

        invoice_currency_code = etree.SubElement(batch_tag, "InvoiceCurrencyCode")
        invoice_currency_code.text = invoice_data.currency_id.name

        # Añadir los detalles del vendedor in <Parties> <SellerParty>
        seller_party = etree.SubElement(parties_tag, "SellerParty")
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
        name.text = invoice_data.partner_id.name or ""

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
        address.text = invoice_data.partner_id.street or ""

        post_code = etree.SubElement(address_in_spain, "PostCode")
        post_code.text = invoice_data.partner_id.zip or ""

        town = etree.SubElement(address_in_spain, "Town")
        town.text = invoice_data.partner_id.city or ""

        province = etree.SubElement(address_in_spain, "Province")
        province.text = invoice_data.partner_id.state_id.name or ""

        country_code = etree.SubElement(address_in_spain, "CountryCode")
        country_code.text = invoice_data.partner_id.country_id.code or ""

        contact_details = etree.SubElement(individual, "ContactDetails")
        electronic_mail = etree.SubElement(contact_details, "ElectronicMail")
        electronic_mail.text = invoice_data.partner_id.email or ""

        # Añadir los detalles del comprador <Parties> <BuyerParty>
        buyer_party = etree.SubElement(parties_tag, "BuyerParty")
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
        tax_identification_number_buyer.text = self.code_account_office or ""

        administrative_centres = etree.SubElement(buyer_party, "AdministrativeCentres")

        # Añadir los centros administrativos
        for role, code in [
            ("01", self.code_account_office or ""),
            ("02", self.code_manager_company or ""),
            ("03", self.code_processing_unit or ""),
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
            province_centre.text = self.res_state_id.name or ""
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

        # Agregar el tag xml de los Invoices <Invoices>
        invoice_element = etree.SubElement(invoices_element, "Invoice")

        # Invoice Header
        invoice_header_element = etree.SubElement(invoice_element, "InvoiceHeader")
        invoice_number_element = etree.SubElement(
            invoice_header_element, "InvoiceNumber"
        )
        invoice_number_element.text = invoice_data.name or ""
        invoice_series_code_element = etree.SubElement(
            invoice_header_element, "InvoiceSeriesCode"
        )
        invoice_series_code_element.text = self.assignment_code or ""
        invoice_document_type_element = etree.SubElement(
            invoice_header_element, "InvoiceDocumentType"
        )
        invoice_document_type_element.text = invoice_data.move_type
        invoice_class_element = etree.SubElement(invoice_header_element, "InvoiceClass")
        invoice_class_element.text = invoice_data.state or ""

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
        language_name_element.text = "es"

        # Invoice <TaxesOutputs>
        invoice_taxes_output = etree.SubElement(invoice_element, "TaxesOutputs")
        invoice_taxes = etree.SubElement(invoice_taxes_output, "Tax")
        taxes_info = []

        # Recorrer todas las líneas del Invoice para ver los taxes
        for line in invoice_data.line_ids:
            tax_total_line = line.price_total
            for tax in line.tax_ids:
                taxes_info.append(
                    {
                        "name": tax.name,
                        "type": tax.type_tax_use,
                        "amount": tax.amount,
                        "total": ((tax.amount/100) * tax_total_line) * tax_total_line,
                    }
                )
        if len(taxes_info) > 0:
            for tax in taxes_info:
                tax_type = etree.SubElement(invoice_taxes, "TaxTypeCode")
                tax_type.text = tax['name'] or ""
                tax_rate = etree.SubElement(invoice_taxes, "TaxRate")
                tax_rate.text = f"{tax['amount']}" or ""
                tax_table = etree.SubElement(invoice_taxes, "TaxableBase")
                tax_total = etree.SubElement(tax_table, "TotalAmount")
                tax_total.text = f"{tax['total']}" or ""

        tax_amount_tag = etree.SubElement(invoice_taxes, "TaxAmount")  # <TaxAmount>
        tax_amount_total = etree.SubElement(tax_amount_tag, "TotalAmount")  # <TotalAmount>
        tax_amount_total.text = f"{invoice_data.amount_tax}" or ""

        # Invoice <InvoiceTotals>
        invoice_totals = etree.SubElement(invoice_element, "InvoiceTotals")
        invoice_gross = etree.SubElement(invoice_totals, "TotalGrossAmount")
        invoice_gross.text = f"{invoice_data.amount_total}" or ""
        invoice_before_tax = etree.SubElement(invoice_totals, "TotalGrossAmountBeforeTaxes")
        invoice_before_tax.text = f"{invoice_data.amount_untaxed}" or ""
        invoice_tax_out = etree.SubElement(invoice_totals, "TotalTaxOutputs")
        invoice_tax_out.text = f"{invoice_data.amount_tax}" or ""
        invoice_tax_held = etree.SubElement(invoice_totals, "TotalTaxesWithheld")
        invoice_tax_held.text = f"{invoice_data.amount_untaxed}" or ""
        invoice_total = etree.SubElement(invoice_totals, "InvoiceTotal")
        invoice_total.text = f"{invoice_data.amount_total}" or ""

        invoice_outs_amount = etree.SubElement(invoice_totals, "TotalOutstandingAmount")
        invoice_outs_amount.text = f"{invoice_data.amount_total}" or ""
        invoice_total_exe = etree.SubElement(invoice_totals, "TotalExecutableAmount")
        invoice_total_exe.text = f"{invoice_data.amount_total}" or ""

        # Start for <Items>
        invoice_items = etree.SubElement(invoice_element, "Items")
        # <InvoiceLine>
        for line in invoice_data.line_ids:
            invoice_line = etree.SubElement(invoice_items, "InvoiceLine")
            receiverContRef = etree.SubElement(invoice_line, "ReceiverContractReference")
            receiverTansRef = etree.SubElement(invoice_line, "ReceiverTransactionReference")

            item_description = etree.SubElement(invoice_line, "ItemDescription")
            item_description.text = line.product_id.name or ""
            item_qty = etree.SubElement(invoice_line, "Quantity")
            item_qty.text = f"{line.quantity}" or ""
            item_uom = etree.SubElement(invoice_line, "UnitOfMeasure")
            item_uom.text = f"{line.product_id.uom_id.id}" or ""
            item_price_untax = etree.SubElement(invoice_line, "UnitPriceWithoutTax")
            item_price_untax.text = f"{line.price_unit}" or ""
            item_total_cost = etree.SubElement(invoice_line, "TotalCost")
            item_total_cost.text = f"{line.price_subtotal}" or ""
            item_total_amount = etree.SubElement(invoice_line, "GrossAmount")
            item_total_amount.text = f"{line.price_total}" or ""
            # <TaxesOutputs>
            item_taxes_output = etree.SubElement(invoice_line, "TaxesOutputs")
            for tax in line.tax_ids:
                item_tax_line = etree.SubElement(item_taxes_output, "Tax")
                item_tax_code = etree.SubElement(item_tax_line, "TaxTypeCode")
                item_tax_code.text = f"{tax.id}" or ""
                item_tax_rate = etree.SubElement(item_tax_line, "TaxRate")
                item_tax_rate.text = f"{tax.amount}" or ""
                # TaxaTable
                item_tax_table = etree.SubElement(item_tax_line, "TaxableBase")
                item_tax_total_amount = etree.SubElement(item_tax_table, "TotalAmount")
                item_tax_total_amount.text = f"{line.price_total}" or ""
                # TaxAmount
                item_tax_end_amount = etree.SubElement(item_tax_line, "TaxAmount")
                item_tax_end_total_amount = etree.SubElement(item_tax_end_amount, "TotalAmount")
                item_tax_end_total_amount.text = f"{line.price_subtotal}" or ""
        # <PaymentDetails>
        payment_details_tag = etree.SubElement(invoice_element, "PaymentDetails")
        payment_installment_tag = etree.SubElement(payment_details_tag, "Installment")
        installment_due_tag = etree.SubElement(payment_installment_tag, "InstallmentDueDate")
        installment_due_tag.text = f"{line.payment_id.payment_date}" if line.payment_id else ""
        installment_mount = etree.SubElement(payment_installment_tag, "InstallmentAmount")
        installment_mount.text = f"{line.payment_id.amount}" if line.payment_id else ""
        payment_means = etree.SubElement(payment_installment_tag, "PaymentMeans")
        payment_means.text = f"{line.payment_id.payment_type}" if line.payment_id else ""
        account_credited_tag = etree.SubElement(payment_installment_tag, "AccountToBeCredited")
        iban_account_tag = etree.SubElement(account_credited_tag, "IBAN")
        iban_account_tag.text = f"{line.payment_id.partner_bank_id.acc_number}" if line.payment_id.partner_bank_id else ""
        #<LegalLiterals>
        legal_literals_tag = etree.SubElement(invoice_element, "LegalLiterals")
        legal_reference = etree.SubElement(legal_literals_tag, "LegalReference")
        legal_reference.text = self.legal_references or ""
        # <AdditionalData>
        additional_data_tag = etree.SubElement(invoice_element, "AdditionalData")
        additional_information = etree.SubElement(additional_data_tag, "InvoiceAdditionalInformation")
        additional_information.text = f"Factura Electrónica generada a través de Odoo"

        # Convertir el árbol XML a una cadena de texto
        xml_string = etree.tostring(
            root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )
        # Codificar el XML en base64
        xml_base64 = base64.b64encode(xml_string)
        _logger.info(f"ROOT INFO XML {root}")
        _logger.info(f"ROOT STRING XML {xml_string}")

        # Guardar el XML en el campo binary de la factura
        invoice_data.write(
            {
                "edi_invoice_xml": xml_base64,
                "xml_filename": f"xml_invoice_{invoice_data.name}.xml",
                "electronic_invoice_xml": root,
            }
        )
        invoice_data.save_binary_file_attachment()
