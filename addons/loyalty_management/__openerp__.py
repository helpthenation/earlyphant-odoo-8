# -*- coding: utf-8 -*-

{
    'author': "OpenERP SA and EARLYPHANT",
    'name': 'Loyalty Program',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Loyalty Program for the Point of Sale and Hotel ',
    'description': """

=======================

This module allows you to define a loyalty program in
for point of sale and hotel, where the customers earn loyalty points
and get rewards.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
        'security/ir.model.access.csv',
        'views/templates.xml'
    ],
    'qweb': ['static/src/xml/loyalty.xml'],
    'installable': True,
    'auto_install': False,
}
