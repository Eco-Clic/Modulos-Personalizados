from odoo import models, fields, api

class MaintenanceReportWizard(models.TransientModel):
    _name = 'maintenance.report.wizard'
    _description = 'Wizard para Generar Reporte de Mantenimiento'

    report_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'Excel')],
        string="Formato del Reporte", required=True, default='pdf'
    )

    def action_generate_report(self):
        # Aquí defines la lógica para generar el reporte basado en el formato
        if self.report_format == 'pdf':
            return self.env.ref('module_name.maintenance_pdf_report').report_action(self)
        elif self.report_format == 'xlsx':
            return self.env['maintenance.line']._generate_excel_report()
