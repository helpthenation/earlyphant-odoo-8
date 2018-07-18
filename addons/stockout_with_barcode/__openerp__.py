# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'StockMove Barcode',
    'version': '1.0',
    'category': 'Warehouse',
    'sequence': 2,
    'summary': 'Make stock out using barcode scanner',
    'description': """
Warehouse > All Operations
While create a picking you can add your move vai barcode scanner which are set to all the product.
While scanning the code, it will look for the match code and then return the required field to the move.
Note: Barcode of the products are EAN13 format.
""",
    'author': 'Earlyphant',
    'website': '',
    'depends': [
      'stock',
    ],
    'data': [
        'views/stock_picking_barcode_form.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
