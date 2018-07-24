from openerp import fields, models, api, osv, _
from openerp.osv import osv

class StockOutBarcode(models.Model):
	_inherit = 'stock.move'

	barcode = fields.Char(String='EAN13 Scan', help="International Article Number used for product identification.")

	def onchangeBarcode(self, cr, uid, ids, barcode, context=None):
		product_obj = self.pool.get('product.product')
		product_ids = product_obj.search(cr, uid, ['|',('ean13','=',barcode),('default_code','=', barcode)], context)
		result = {}
		if len(product_ids) == 1:
			for product in product_obj.browse(cr, uid, product_ids[0], context):
				result['product_id'] = product.id
		return {'value':result}

	@api.onchange('barcode')
	def _barcodeOnchange(self):
		if self.barcode != False:
			product = self.env['product.product'].search([('ean13','=',self.barcode)])
			self.product_id = product
			self.product_uom_qty = 0
			self.product_uom = product.uom_id.id
			self.product_uos_qty = 0
			self.name = product.name

	@api.onchange('product_id')
	def _product_onchange(self):
		if self.product_id.id != False:
			product = self.env['product.product'].search([('id', '=', self.product_id.id)])
			self.product_uom_qty = 0
			self.product_uom = product.uom_id.id
			self.product_uos_qty = 0
			self.name = product.name
