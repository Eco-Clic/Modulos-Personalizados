{
    'name': 'test2',
    'version': '1.1',
    'depends': ['base'],
    'author': 'xavier',
    'category': 'Test',
    'description': """
    Módulo de prueba para añadir un menú principal a un modulo
    """,
    'installable': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
