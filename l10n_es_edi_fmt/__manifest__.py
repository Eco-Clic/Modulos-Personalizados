{
    "name": "Generar Factura-Electronica",
    "version": "1.0",
    "category": "Accounting",
    "author": "Eco-Clic",  # Ing. Yadier Abel
    "summary": "Módulo para generar Factura-electronica",
    "depends": ["base", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "wizard/electronic_invoice_views.xml",
    ],
}
