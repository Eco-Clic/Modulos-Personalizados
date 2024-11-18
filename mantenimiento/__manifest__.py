# -*- coding: utf-8 -*-
{
    "name": "Mantenimiento",
    "summary": "Mantenimiento de las Viviendas/Habitaciones",
    "description": """
    Mantenimiento de las Viviendas/Habitaciones
    """,
    "author": "Eco-clic",
    "category": "House",
    "version": "0.1",
    "depends": [
        "base",
        "mail",
        "calendar",
        "contacts",
        "alquileres",
        "product",
        "hr"
    ],
    "data": [
        "security/ir.model.access.csv",         
        "data/maintenance_sequence.xml",
        "data/cleaning_sequence.xml",      
        "views/maintenance_views.xml",          
        "views/maintenance_actions.xml",        
        "views/maintenance_root.xml",     
        "views/cleaning_views.xml",   
    ],
    "installable": True,
    "application": True,
}
