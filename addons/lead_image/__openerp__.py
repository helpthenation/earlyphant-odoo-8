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
    'name': 'Salesperson Card',
    'version': '1.0',
    'category': 'Customer Relationship Management',
    'sequence': 2,
    'summary': 'Enable user to attach namecard in the Leads',
    'description': """
    This will create another important field which allow user to attach the informative image of the sales person name card or profile which help 
    management layer to control the KPI of their under employees's performance.
""",
    'author': 'Earlyphant',
    'website': '',
    'depends': [
      'crm',
    ],
    'data': [
        'views/update_lead_form_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
