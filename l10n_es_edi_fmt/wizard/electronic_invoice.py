import base64
import datetime

from lxml import etree
from odoo.exceptions import ValidationError
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

# Codes enumerators from Facturaev3_2_2.xml
countries = ['AFG', 'ALB', 'DZA', 'ASM', 'AND', 'AGO', 'AIA', 'ATG', 'ARG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN', 'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR', 'CAN', 'CPV', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'COD', 'COL', 'COM', 'COG', 'COK', 'CRI', 'CIV', 'HRV', 'CUB', 'CYP', 'CZE', 'DNK', 'DJI', 'DMA', 'DOM', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'ETH', 'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'PYF', 'GAB', 'GMB', 'GEO', 'GGY', 'DEU', 'GHA', 'GIB', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GIN', 'GNB', 'GUY', 'HTI', 'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IDN', 'IMN', 'IRN', 'IRQ', 'IRL', 'ISR', 'ITA', 'JAM', 'JEY', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR', 'PRK', 'KOR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LIE', 'LTU', 'LUX', 'MAC', 'MKD', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MHL', 'MTQ', 'MRT', 'MUS', 'MYT', 'MEX', 'FSM', 'MDA', 'MCO', 'MNE', 'MNG', 'MSR', 'MAR', 'MOZ', 'MMR', 'NAM', 'NRU', 'NPL', 'NLD', 'ANT', 'NCL', 'NZL', 'NIC', 'NER', 'NGA', 'NIU', 'NFK', 'MNP', 'NOR', 'OMN', 'PAK', 'PLW', 'PAN', 'PNG', 'PRY', 'PSE', 'PER', 'PHL', 'PCN', 'POL', 'PRT', 'PRI', 'QAT', 'REU', 'ROU', 'RUS', 'RWA', 'KNA', 'LCA', 'VCT', 'WSM', 'SMR', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'ESP', 'LKA', 'SHN', 'SPM', 'SDN', 'SUR', 'SJM', 'SWZ', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'TZA', 'THA', 'TGO', 'TKL', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'TLS', 'TCA', 'TUV', 'UGA', 'UKR', 'ARE', 'GBR', 'USA', 'URY', 'UZB', 'VUT', 'VAT', 'VEN', 'VNM', 'VGB', 'VIR', 'WLF', 'ESH', 'YEM', 'ZAR', 'ZMB', 'ZWE']
tax_currency_codes = ['AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAD', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BRR', 'BSD', 'BWP', 'BYR', 'BZD', 'CAD', 'CDF', 'CDP', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DRP', 'DZD', 'EEK', 'EGP', 'ESP', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEK', 'GHC', 'GIP', 'GMD', 'GNF', 'GTQ', 'GWP', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'INR', 'IQD', 'IRR', 'ISK', 'JMD', 'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MGF', 'MNC', 'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZM', 'NGN', 'NIC', 'NIO', 'NIS', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEI', 'PEN', 'PES', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RMB', 'RON', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDP', 'SEK', 'SGD', 'SHP', 'SKK', 'SLL', 'SOL', 'SOS', 'SRD', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMM', 'TND', 'TOP', 'TPE', 'TRY', 'TTD', 'TWD', 'TZS', 'UAH', 'UGS', 'USD', 'UYP', 'UYU', 'VEF', 'VND', 'VUV', 'WST', 'XAF', 'XCD', 'XOF', 'YER', 'ZAR', 'ZMK', 'ZWD']

units_measures = {'01': 'Units', '02': 'Hours-HUR', '03': 'Kilograms-KGM', '04': 'Liters-LTR', '05': 'Other', '06': 'Boxes-BX', '07': 'Trays, one layer no cover, plastic-DS', '08': 'Barrels-BA', '09': 'Jerricans, cylindrical-JY', '10': 'Bags-BG', '11': 'Carboys, non-protected-CO', '12': 'Bottles, non-protected, cylindrical-BO', '13': 'Canisters-CI', '14': 'Tetra Briks', '15': 'Centiliters-CLT', '16': 'Centimeters-CMT', '17': 'Bins-BI', '18': 'Dozens', '19': 'Cases-CS', '20': 'Demijohns, non-protected-DJ', '21': 'Grams-GRM', '22': 'Kilometers-KMT', '23': 'Cans, rectangular-CA', '24': 'Bunches-BH', '25': 'Meters-MTR', '26': 'Milimeters-MMT', '27': '6-Packs', '28': 'Packages-PK', '29': 'Portions', '30': 'Rolls-RO', '31': 'Envelopes-EN', '32': 'Tubs-TB', '33': 'Cubic meter-MTQ', '34': 'Second-SEC', '35': 'Watt-WTT', '36': 'Kilowatt per hora-KWh'}
payment_means_array = {'01': 'In cash', '02': 'Direct debit', '03': 'Receipt', '04': 'Credit transfer', '05': 'Accepted bill of exchange', '06': 'Documentary credit', '07': 'Contract award', '08': 'Bill of exchange', '09': 'Transferable promissory note', '10': 'Non transferable promissory note', '11': 'Cheque', '12': 'Open account reimbursement', '13': 'Special payment', '14': 'Set-off by reciprocal credits', '15': 'Payment by postgiro', '16': 'Certified cheque', '17': 'Banker’s draft', '18': 'Cash on delivery', '19': 'Payment by card'}

tax_type_code = {'01': 'Value-Added Tax', '02': 'Taxes on production, services and imports in Ceuta and Melilla', '03': 'IGIC:Canaries General Indirect Tax', '04': 'IRPF:Personal Income Tax', '05': 'Other', '06': 'ITPAJD:Tax on wealth transfers and stamp duty', '07': 'IE: Excise duties and consumption taxes', '08': 'Ra: Customs duties', '09': 'IGTECM: Sales tax in Ceuta and Melilla', '10': 'IECDPCAC: Excise duties on oil derivates in Canaries', '11': 'IIIMAB: Tax on premises that affect the environment in the Balearic Islands', '12': 'ICIO: Tax on construction, installation and works', '13': 'IMVDN: Local tax on unoccupied homes in Navarre', '14': 'IMSN: Local tax on building plots in Navarre', '15': 'IMGSN: Local sumptuary tax in Navarre', '16': 'IMPN: Local tax on advertising in Navarre', '17': 'REIVA: Special VAT for travel agencies', '18': 'REIGIC: Special IGIC: for travel agencies', '19': 'REIPSI: Special IPSI for travel agencies', '20': 'IPS: Insurance premiums Tax', '21': 'SWUA: Surcharge for Winding Up Activity', '22': 'IVPEE: Tax on the value of electricity generation', '23': 'Tax on the production of spent nuclear fuel and radioactive waste from the generation of nuclear electric power', '24': 'Tax on the storage of spent nuclear energy and radioactive waste in centralised facilities', '25': 'IDEC: Tax on bank deposits', '26': 'Excise duty applied to manufactured tobacco in Canaries', '27': 'IGFEI: Tax on Fluorinated Greenhouse Gases', '28': 'IRNR: Non-resident Income Tax', '29': 'Corporation Tax'}
tax_codes = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29']

invoice_document_type = {'FC': 'Complete Invoice.', 'FA': 'Abbreviated.', 'AF': 'Self invoice.'} # InvoiceDocumentType
invoice_class_type = {'OO': 'Original Invoice.', 'OR': 'Corrective.', 'OC': 'Summary.', 'CO': 'Copy of the Original.', 'CR': 'Copy of the Corrective.', 'CC': 'Copy of the Summary.'}

reason_code_type = {'01': '"Invoice number"', '02': '"Invoice serial number"', '03': '"Issue date"', '04': '"Name and surnames/Corporate name – Issuer (Sender)"', '05': '"Name and surnames/Corporate name - Receiver"', '06': '"Issuer’s Tax Identification Number"', '07': '"Receiver’s Tax Identification Number"', '08': '"Issuer’s address"', '09': '"Receiver’s address"', '10': '"Item line"', '11': '"Applicable Tax Rate"', '12': '"Applicable Tax Amount"', '13': '"Applicable Date/Period"', '14': '"Invoice Class"', '15': '"Legal literals"', '16': '"Taxable Base"', '80': '"Calculation of tax outputs"', '81': '"Calculation of tax inputs"', '82': '"Taxable Base modified due to return of packages and packaging materials"', '83': '"Taxable Base modified due to discounts and rebates"', '84': '"Taxable Base modified due to firm court ruling or administrative decision"', '85': '"Taxable Base modified due to unpaid outputs where there is a judgement opening insolvency proceedings"'}


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
        total_amount_executable.text = str(round(invoice_data.amount_total,4)) or ""

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
        code_spain = invoice_data.partner_id.country_id.code
        t_code_spain = next((country for country in countries if code_spain in country), None)
        country_code.text = t_code_spain or ""

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
            # buscar en el array code
            box_country_code = next((country for country in countries if invoice_data.country_code in country), None)
            country_code_centre.text = box_country_code or ""

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
        code_legal = invoice_data.partner_id.country_id.code
        t_code = next((country for country in countries if code_legal in country), None)
        country_code_legal.text = t_code or ""

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
        invoice_document_type_element.text = "FC"
        # InvoiceClass array invoice_class_type
        if invoice_data.move_type in ('out_refund','in_refund'):
            text_invoice_class_type = 'OR' # 'Rectificativa.'
        else:
            text_invoice_class_type = 'OO' # Original
        invoice_class_element = etree.SubElement(invoice_header_element, "InvoiceClass")
        invoice_class_element.text = text_invoice_class_type

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
        code_tax = invoice_data.currency_id.name
        tax_country_currency = next((country for country in tax_currency_codes if code_tax in country), None)

        tax_currency_code_element.text = tax_country_currency or ""
        language_name_element = etree.SubElement(
            invoice_issue_data_element, "LanguageName"
        )
        language_name_element.text = "es"

        # Invoice <TaxesOutputs>
        invoice_taxes_output = etree.SubElement(invoice_element, "TaxesOutputs")
        invoice_taxes = etree.SubElement(invoice_taxes_output, "Tax")
        taxes_info = []

        # Recorrer todas las líneas del Invoice para ver los taxes
        for line in invoice_data.invoice_line_ids:
            if line.display_type != 'product':
                continue
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
                # tax_code_str = f"{int(tax['amount'] ):02}" # convertirlo a formato '04'
                tax_type.text = "01" # tax_code_str
                tax_rate = etree.SubElement(invoice_taxes, "TaxRate")
                tax_rate.text = f"{ round(tax['amount'], 4)}" or ""
                tax_table = etree.SubElement(invoice_taxes, "TaxableBase")
                tax_total = etree.SubElement(tax_table, "TotalAmount")
                tax_total.text = f"{ round(tax['total'], 4)}" or ""

        tax_amount_tag = etree.SubElement(invoice_taxes, "TaxAmount")  # <TaxAmount>
        tax_amount_total = etree.SubElement(tax_amount_tag, "TotalAmount")  # <TotalAmount>
        tax_amount_total.text = f"{round(invoice_data.amount_tax, 4)}" if invoice_data.amount_tax else "0.00"

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
        # <InvoiceLine> mostrar solo las de display_type = product
        for line in invoice_data.line_ids:
            if line.display_type != 'product':
                continue
            invoice_line = etree.SubElement(invoice_items, "InvoiceLine")
            receiverContRef = etree.SubElement(invoice_line, "ReceiverContractReference")
            receiverTansRef = etree.SubElement(invoice_line, "ReceiverTransactionReference")

            item_description = etree.SubElement(invoice_line, "ItemDescription")
            item_description.text = line.product_id.name or ""
            item_qty = etree.SubElement(invoice_line, "Quantity")
            item_qty.text = f"{line.quantity}" or ""
            item_uom = etree.SubElement(invoice_line, "UnitOfMeasure")
            if line.product_id.uom_id:
                uom_code_str = f"{int(line.product_id.uom_id.id):02}"
            item_uom.text = uom_code_str if uom_code_str != "00" else "01"
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
                tax_code_type = tax.amount # Supongamos que es un float, por ejemplo, 4.000
                # Convertir a entero y luego a string con ceros delante si es necesario
                tax_code_str = f"{int(tax_code_type):02}"
                item_tax_code.text = "01"
                item_tax_rate = etree.SubElement(item_tax_line, "TaxRate")
                item_tax_rate.text = f"{tax.amount}" or ""
                # TaxaTable
                item_tax_table = etree.SubElement(item_tax_line, "TaxableBase")
                item_tax_total_amount = etree.SubElement(item_tax_table, "TotalAmount")
                item_tax_total_amount.text = f"{ round(line.price_total,4)}" or ""
                # TaxAmount
                item_tax_end_amount = etree.SubElement(item_tax_line, "TaxAmount")
                item_tax_end_total_amount = etree.SubElement(item_tax_end_amount, "TotalAmount")
                item_tax_end_total_amount.text = f"{round(line.price_total,4)}" or ""
        # <PaymentDetails>
        payment_details_tag = etree.SubElement(invoice_element, "PaymentDetails")
        payment_installment_tag = etree.SubElement(payment_details_tag, "Installment")
        installment_due_tag = etree.SubElement(payment_installment_tag, "InstallmentDueDate")
        installment_due_tag.text = invoice_data.payment_id.date.strftime("%Y-%m-%d") if invoice_data.payment_id else "" # date format ISO 8601:2004
        installment_mount = etree.SubElement(payment_installment_tag, "InstallmentAmount")
        installment_mount.text = f"{round(invoice_data.payment_id.amount, 2):0>6.2f}" if invoice_data.payment_id else ""
        payment_means = etree.SubElement(payment_installment_tag, "PaymentMeans") # del array payment_means_array
        #payment_means.text = f"{invoice_data.payment_id.payment_method_line_id}" if invoice_data.payment_id else ""
        payment_means.text = '01' # in cash

        account_credited_tag = etree.SubElement(payment_installment_tag, "AccountToBeCredited")
        iban_account_tag = etree.SubElement(account_credited_tag, "IBAN")
        iban_account_tag.text = f"{invoice_data.payment_id.partner_bank_id.acc_number}" if invoice_data.payment_id.partner_bank_id else ""
        #<LegalLiterals>
        legal_literals_tag = etree.SubElement(invoice_element, "LegalLiterals")
        legal_reference = etree.SubElement(legal_literals_tag, "LegalReference")
        legal_reference.text = self.legal_references or ""
        # <AdditionalData>
        additional_data_tag = etree.SubElement(invoice_element, "AdditionalData")
        additional_information = etree.SubElement(additional_data_tag, "InvoiceAdditionalInformation")
        additional_information.text = f"Factura Electrónica generada a través de Odoo"

        xml_string = etree.tostring(
            root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
        )

        # Dividir la cadena XML en líneas
        xml_lines = xml_string.decode("UTF-8").splitlines()

        # Cambiar las líneas necesarias
        xml_lines[0] = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        xml_lines[1] = '<ns3:Facturae xmlns:ns2="http://www.w3.org/2000/09/xmldsig#" xmlns:ns3="http://www.facturae.gob.es/formato/Versiones/Facturaev3_2_2.xml">'
        xml_lines[-1] = '</ns3:Facturae>'

        # Reconstruir el XML modificado
        modified_xml = "\n".join(xml_lines)

        # Codificar el XML en base64
        xml_base64 = base64.b64encode(modified_xml.encode("UTF-8"))

        # Guardar el XML en el campo binary de la factura
        invoice_data.write(
            {
                "edi_invoice_xml": xml_base64,
                "xml_filename": f"xml_invoice_{invoice_data.name}.xml",
                "electronic_invoice_xml": root,
            }
        )
        invoice_data.save_binary_file_attachment()
