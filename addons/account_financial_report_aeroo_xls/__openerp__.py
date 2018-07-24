# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) BrowseInfo (http://browseinfo.in)
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
    'name': 'Accounting Excel Reports',
    'version': '1.0',
    'category': 'Accounting',
    'description': """	
		Balance Sheet Excel Report, General Ledger Excel Report, Trial Balance Excel report, Profit and Loss Excel report, Profit & loss Excel Report, Balance Sheet XLS Report, General Ledger XLS Report, Trial Balance XLS report, Profit and Loss XLS report, Profit & loss XLS Report, Accounting Reports, Aeroo reports, 

""",
    'author': 'BrowseInfo',
    'website': 'www.browseinfo.in',
    'depends': ['account','report_aeroo'],
    'summary': 'All Accounting reports in XLS Format',
    'data': [
        'wizard/wizard_trail_balance_view.xml',
        'report/report_general_ledger_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
