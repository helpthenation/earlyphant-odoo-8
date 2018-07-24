{
    'name': 'Accana report Parent',
    'version': '1.1',
    'description': '''
    * Add *parent_id* to the model, sql query and tree view
   ''',
    'depends': ['base', 'account'],
    'init_xml': [],
    'update_xml':  ['account_analytic_entries_report_view.xml'],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': True,
    'active': False,
    'certificate': '',
}
