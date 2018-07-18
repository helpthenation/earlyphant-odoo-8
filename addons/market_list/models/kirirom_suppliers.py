from openerp import models, fields, api

class kirirom_suppliers(models.Model):
    _name = 'kirirom.supplier'

    name = fields.Char('Name')
    tel = fields.Char('Telephone')
    supplier_id = fields.Char('Id')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        domain = [('supplier_id', operator, name)]
        picks = self.search(domain + args, limit=limit)
        return picks.name_get()