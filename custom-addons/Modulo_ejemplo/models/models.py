from odoo import models, fields

class Producto(models.Model):
    _name = 'modelo.producto'
    _description = 'modelo_de_producto_generico'

    name = fields.Char(string='Nombre', required=True)
    price = fields.Float(string='Precio', required=True)
    stock = fields.Integer(string='Stock', required=True)
    category_id = fields.Many2one('modelo.producto.categoria', string='Categoría')

class ProductCategory(models.Model):
    _name = 'modelo.producto.categoria'
    _description = 'Categoría de Producto'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    producto_ids = fields.One2many('modelo.producto', 'category_id', string='Productos')
