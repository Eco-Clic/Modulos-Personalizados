{
    'name': "Modulo Notas Internas",
    'version': '1.0',
    'depends': ['account', 'base', 'sale', 'repair'],
    'author': "Eco-Clic",
    'description': """
    Este modulo crea campos y columnas para notas internas
    """,
    'data': [
        'view/account_move_view.xml',
        'view/repair_order_view.xml',
        'view/sale_order_view.xml',
    ],
    'installable': True,
}
