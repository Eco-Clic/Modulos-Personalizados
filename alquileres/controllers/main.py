from odoo import http
from odoo.http import request


class RentalController(http.Controller):

    @http.route(['/properties'], type='http', auth="public", website=True)
    def list_properties(self, **kw):
        # Obtener las propiedades y cuartos que están publicados y disponibles
        properties = request.env['rental.property'].sudo().search([
            ('website_published', '=', True),
            ('status', '=', 'available')
        ])
        return request.render('alquileres.property_list', {
            'properties': properties,
        })

    @http.route(['/property/<model("rental.property"):property>'], type='http', auth="public", website=True)
    def property_details(self, property, **kw):
        # Detalles de una propiedad individual
        return request.render('alquileres.property_details', {
            'property': property,
        })
