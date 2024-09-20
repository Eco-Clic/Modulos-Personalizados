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
        "contacts",
        "account",
    ],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/rent_views.xml",
        "views/rent_room_views.xml",
        "data/rent_sequence.xml",
    ],
    "installable": True,
    "application": False,
}
