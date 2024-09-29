# -*- coding: utf-8 -*-
{
    "name": "Mantenimiento",
    "summary": "Gestión de Viviendas Mantenimiento",
    "description": """
    Gestión de Viviendas Mantenimiento
    """,
    "author": "Eco-clic",
    "category": "House",
    "version": "0.1",
    "depends": [
        "base",
        "contacts",
        "account",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/maintenance_views.xml', 
        'views/maintenance_actions.xml',
        'views/maintenance_menus.xml',
        
    ],
    "installable": True,
    "application": False,
}
