from openerp import fields, models, api, _



#Class
class lead_images(models.Model):
	_inherit = 'crm.lead'

	salesperson_card = fields.Binary(string='Image Attachment')
