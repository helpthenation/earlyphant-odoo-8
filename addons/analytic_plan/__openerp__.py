# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    'name': 'Analytic Plan',
    'version': '8.0.1.1.2',
    'author':   'Eficent, '
                'Project Expert Team',
    'contributors': [
        'Jordi Ballester <jordi.ballester@eficent.com>',
        'Matjaž Mozetič <m.mozetic@matmoz.si>',
    ],
    'website': 'http://project.expert',
    'category': 'Project Management',
    'license': 'AGPL-3',
    'depends': ['account', 'analytic', 'project', 'project_wbs'],
    'data': [
        'account_analytic_plan_version_view.xml',
        'account_analytic_plan_version_data.xml',
        'account_analytic_plan_journal_view.xml',
        'account_analytic_line_plan_view.xml',
        'account_analytic_account_view.xml',
        'security/ir.model.access.csv',
        'account_analytic_plan_journal_data.xml',
        'project_view.xml',
        'wizard/analytic_plan_copy_version.xml',
    ],
    'test': [
    ],
    'installable': True,
    'active': False,
    'certificate': '',
}
