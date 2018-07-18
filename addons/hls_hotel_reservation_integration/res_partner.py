from openerp.osv import osv, fields

class ResPartner(osv.Model):
    _inherit ='res.partner'

    _columns = {
        'last_name': fields.char("Last Name",required=True)
    }