# -*- coding: utf-8 -*-
# Eco-clic Ing. yadier Abel De Quesada

{
    "name": "Product Discount points",
    "version": "1.0",
    "category": "Accounting",
    "summary": "Make discounts on order lines and invoices according to product points",
    "depends": [
        "product",
        "sale",
        "account",
    ],
    "data": [
        "views/product_template_view.xml",
        "views/account_move_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
