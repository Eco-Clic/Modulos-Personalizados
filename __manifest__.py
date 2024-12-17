# -*- coding: utf-8 -*-
{
    "name": "Alquileres",
    "summary": "Gestión de Viviendas en Alquiler",
    "description": """
    Gestión de Viviendas en Alquiler
    """,
    "author": "Eco-clic",
    "category": "House",
    "version": "0.1",
    "depends": [
        "base",
        "contacts",
        "account",
        "base",
        "mail",
        "calendar",
        "hr"
    ],

    "data": [

        'security/groups.xml',
        'security/ir_rules.xml',
        "security/ir.model.access.csv",

        #Parents
        "views/parents/property_management_parent.xml",
        "views/parents/rental_management_parent.xml",
        "views/parents/maintenance_parent.xml",
        
        #Bail Bound
        "data/bail_bounds_history_sequence.xml",
        "views/bail_bound/bail_bounds_actions.xml",
        "views/bail_bound/bail_bounds_views.xml",

        
        #Booking
        'data/booking_history_sequence.xml',
        "views/booking/booking_actions.xml",
        'views/booking/booking_views.xml',
        
        #Occupacity
        # "views/occupacity/occupacity_views.xml",
        "views/occupacity/occupacity_actions.xml",
        # "views/occupacity/occupacity_root.xml",


        #Respartner
        "views/res_partner/res_partner_views.xml",
        "views/res_partner/res_partner_search.xml",
        # "wizards/wizard_payment_insurence_partner.xml",

        #Employee
        "views/hr_employee/hr_employee_views.xml",

        #Lista de muebles/servicios
        # "views/furniture_services/furniture_services_actions.xml",
        # "views/furniture_services/furniture_services_views.xml",
        # "views/furniture_services/furniture_services_root.xml",

        #Propierties
        "data/property_main_sequence.xml",
        "views/property/property_views.xml",
        "views/property/property_actions.xml",
        "views/property/property_root.xml",
        
        #Propierties (rental management)
        "views/property/rental_property_views.xml",
        "views/property/rental_property_actions.xml",
        "views/property/rental_property_root.xml",

        #Contracts
        "data/property_contract_sequence.xml",
        "data/room_contract_sequence.xml",
        "views/contract/contract_views.xml",
        "views/contract/contract_actions.xml",
        "views/contract/contract_root.xml",
        "views/contract/termination_contract.xml",

        #Contracts (rental management)
        "views/contract/rental_contract_views.xml",
        "views/contract/rental_contract_actions.xml",
        "views/contract/rental_contract_root.xml",

        #Room
        "data/room_main_sequence.xml",
        "views/room/room_views.xml",
        "views/room/room_actions.xml",
        "views/room/room_root.xml",
        "wizards/wizard_payment_insurence.xml",
        "views/room/booking_receipt_pdf.xml",
        "views/room/booked_room_pdf.xml",
        "views/room/termination_room.xml",

        #Room (rental management)
        "views/room/rental_room_views.xml",
        "views/room/rental_room_actions.xml",
        "views/room/rental_room_root.xml",

        #Maintenance     
        "data/maintenance_sequence.xml",       
        "views/maintenance/bills_maintenance_views.xml",
        "views/maintenance/bills_maintenance_actions.xml",
        "views/maintenance/maintenance_views.xml",          
        "views/maintenance/maintenance_actions.xml",        
        "views/maintenance/maintenance_root.xml", 

        #Payment History
        "data/payment_sequence.xml",
        "views/payment/payment_actions.xml",
        "views/payment/payment_views.xml",

        #Cleaning   
        "data/cleaning_sequence.xml",
        "views/cleaning/cleaning_views.xml",
        "views/cleaning/cleaning_actions.xml",   
        "views/cleaning/cleaning_root.xml",

        #Reportes (Acciones)
        "views/contract/contract_report_pdf_property.xml",
        "views/contract/contract_report_pdf_room.xml",
        "views/contract/contract_anex_pdf_property.xml",
        "views/contract/contract_anex_pdf_room.xml",
        
        #Reportes (Templates)
        "report/contrato_template_property.xml",
        "report/contrato_template_room.xml",
        "report/booking_recipe_template.xml",
        "report/annexes_contract_property.xml",
        "report/annexes_contract_room.xml",
        "report/reserva_habitacion.xml",
        "report/finalizacion-ezebecto.xml",
        "report/contract_termination_room.xml",

        #Debts
        "data/debt_sequence.xml",
        "views/debt/debt_actions.xml",
        "views/debt/debt_views.xml",

        #Bills
        "views/bills/bills_actions.xml",
        "views/bills/bills_views.xml",
        "views/bills/bills_search.xml",
        "views/bills/bills_root.xml",
        

    ],

    "assets": {
        'web.assets_backend': [
            'alquileres/static/src/css/styles.css',
        ],
    },

    "installable": True,
    "application": True,
}
