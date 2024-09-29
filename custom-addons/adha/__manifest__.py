{
    'name': "Modulo Conexion de ADHA",
    'version': '1.0',
    'depends': ['account', 'base', 'sale', 'repair'],
    'author': "Eco-Clic",
    'description': """
    Este modulo conecta Odoo con el software ADHA
    """,
    'data': [
        'views/account_move_view.xml',
        'views/repair_view.xml',
        'views/sale_order_view.xml',
    ],
    'assets': {
        'web.assets_backend':[
            'adha/static/src/css/account.css',
        ],
    },
    'installable': True,
}
