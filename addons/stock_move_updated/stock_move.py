from openerp.osv import osv, fields

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {'project_id':fields.many2one('account.analytic.account','Project'),}
class stock_picking(osv.osv):

	_inherit = 'stock.picking'

	_columns = {
	'project_id':fields.many2one('account.analytic.account','Project'),
	'source_loc':fields.many2one('stock.location','Source Location'),
	'destination_loc':fields.many2one('stock.location','Destination Location')
	}


class pos_order(osv.osv):
	_inherit = 'pos.order'

	_columns = {
	'number_of_customer':fields.char('Numbers of Customer'),
	}