# -*- coding: utf-8 -*-
{
    "name": "Alquileres",
    "summary": "Gestión de Viviendas en Alquiler",
    "description": """
    Gestión de Viviendas en Alquiler
    """,
    "author": "Eco-clic",
    # for the full list
    "category": "House",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "stock",
        "contacts",
        "account",
        "website",
    ],
    # always loaded
    "data": [
        "data/rent_sequence.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/rent_issue_views.xml",
        "views/rental_empadronamiento_views.xml",
        "views/rental_contract_views.xml",
        "views/rent_payment_history_views.xml",
        "views/rental_property_views.xml",
        "views/rental_room_views.xml",
        "views/res_partner_inh_views.xml",
        "views/menu_alquiler.xml",
        "views/rental_website_templates.xml",
        "views/account_move_view.xml",
        "wizards/wizard_check_contracts.xml",
        "wizards/rental_payment_wizard.xml",
    ],
    "installable": True,
    "application": True,
}
