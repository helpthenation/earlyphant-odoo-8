import logging
from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)


class loyalty_program(osv.osv):
    _name = 'loyalty.program'
    _columns = {
        'name': fields.char('Loyalty Program Name', size=32, select=1,
                            required=True, help="An internal identification for the loyalty program configuration"),
        'pp_currency': fields.float('Points per currency',
                                    help="How many loyalty points are given to the customer by sold currency"),
        'pp_product': fields.float('Points per product',
                                   help="How many loyalty points are given to the customer by product sold"),
        'pp_order': fields.float('Points per order',
                                 help="How many loyalty points are given to the customer for each sale or order"),
        'rounding': fields.float('Points Rounding', readonly=True,
                                 help="The loyalty point amounts are rounded to multiples of this value."),
        'rule_ids': fields.one2many('loyalty.rule', 'loyalty_program_id', 'Rules'),
        'reward_ids': fields.one2many('loyalty.reward', 'loyalty_program_id', 'Rewards'),

    }
    _defaults = {
        'rounding': 1,
    }


class loyalty_rule(osv.osv):
    _name = 'loyalty.rule'
    _columns = {
        'name': fields.char('Name', size=32, select=1, required=True,
                            help="An internal identification for this loyalty program rule"),
        'loyalty_program_id': fields.many2one('loyalty.program', 'Loyalty Program',
                                              help='The Loyalty Program this exception belongs to'),
        'type': fields.selection((('product', 'Product'), ('category', 'Category')), 'Type', required=True,
                                 help='Does this rule affects products, or a category of products ?'),
        'product_id': fields.many2one('product.product', 'Target Product', help='The product affected by the rule'),
        'category_id': fields.many2one('pos.category', 'Target Category', help='The category affected by the rule'),
        'pp_product': fields.float('Points per product',
                                   help='How many points the product will earn per product ordered'),
        'pp_currency': fields.float('Points per currency', help='How many points the product will earn per value sold'),
        'wh_categ': fields.many2one('product.category', 'Product Category')
    }
    _defaults = {
        'type': 'product',
    }


class loyalty_reward(osv.osv):
    _name = 'loyalty.reward'
    _columns = {
        'name': fields.char('Name', size=32, select=1, required=True,
                            help='An internal identification for this loyalty reward'),
        'loyalty_program_id': fields.many2one('loyalty.program', 'Loyalty Program',
                                              help='The Loyalty Program this reward belongs to'),
        'minimum_points': fields.float('Minimum Points',
                                       help='The minimum amount of points the customer must have to qualify for this '
                                            'reward'),
        'type': fields.selection((('gift', 'Gift'), ('discount', 'Discount')), 'Type', required=True,
                                 help='The type of the reward'),
        'gift_product_id': fields.many2one('product.product', 'Gift Product', help='The product given as a reward'),
        'point_cost': fields.float('Point Cost', help='The cost of the reward'),
        'discount_product_id': fields.many2one('product.product', 'Discount Product',
                                               help='The product used to apply discounts'),
        'discount': fields.float('Discount', help='The discount percentage'),
        'point_product_id': fields.many2one('product.product', 'Point Product',
                                            help='The product that represents a point that is sold by the customer'),
    }

    def _check_gift_product(self, cr, uid, ids, context=None):
        _logger.warning('_check_gift_product')
        for reward in self.browse(cr, uid, ids, context=context):
            if reward.type == 'gift':
                return bool(reward.gift_product_id)
            else:
                return True

    def _check_discount_product(self, cr, uid, ids, context=None):
        _logger.warning('_check_discount_product')
        for reward in self.browse(cr, uid, ids, context=context):
            if reward.type == 'discount':
                return bool(reward.discount_product_id)
            else:
                return True

    # def _check_point_product(self, cr, uid, ids, context=None):
    #     _logger.warning('_check_point_product')
    #     for reward in self.browse(cr, uid, ids, context=context):
    #         if reward.type == 'resale':
    #             return bool(reward.point_product_id)
    #         else:
    #             return True

    _constraints = [
        (_check_gift_product, "The gift product field is mandatory for gift rewards", ["type", "gift_product_id"]),
        (_check_discount_product, "The discount product field is mandatory for discount rewards",
         ["type", "discount_product_id"]),
        # (_check_point_product,    "The point product field is mandatory for point resale rewards", ["type",
        # "discount_product_id"]),
    ]


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'loyalty_points': fields.float('Loyalty Points', readonly=True,
                                       help='The loyalty points the user won as part of a Loyalty Program'),
        'loyalty_id': fields.many2one('loyalty.program', 'Loyalty Program',
                                      help='The loyalty program used by this point_of_sale'),
    }


class pos_order(osv.osv):
    _inherit = 'pos.order'

    _columns = {
        'loyalty_points': fields.float('Loyalty Points',
                                       help='The amount of Loyalty points the customer won or lost with this order'),
    }

    def _order_fields(self, cr, uid, ui_order, context=None):
        fields = super(pos_order, self)._order_fields(cr, uid, ui_order, context)
        fields['loyalty_points'] = ui_order.get('loyalty_points', 0)
        return fields

    def create_from_ui(self, cr, uid, orders, context=None):
        ids = super(pos_order, self).create_from_ui(cr, uid, orders, context=context)
        for order in orders:
            if order['data']['loyalty_points'] != 0 and order['data']['partner_id']:
                partner = self.pool.get('res.partner').browse(cr, uid, order['data']['partner_id'], context=context)
                partner.write({'loyalty_points': partner['loyalty_points'] + order['data']['loyalty_points']})

        return ids


# class sale_order(osv.osv):
#     _inherit = 'sale.order'
#     _columns = {
#         'loyalty_points': fields.float('Loyalty Points',
#                                        help='The loyalty points the user won as part of a Loyalty Program')
#     }
#
#
# class hotel_folio(models.Model):
#     _inherit = 'hotel.folio'
#     _columns = {
#         'points_won': fields.float('Earned Points', readonly=True),
#         'points_spent': fields.float('Points Cost', readonly=True),
#         'isbutton': fields.boolean('IsButton', readonly=True)
#     }
#
#     @api.model
#     def create(self, vals, check=True):
#         folio_id = super(hotel_folio, self).create(vals)
#
#         amount_total = folio_id['amount_total']
#         client = folio_id['partner_id']
#         loyalty_id = client['loyalty_id']
#         for reward in loyalty_id['reward_ids']:
#             if reward['type'] == 'discount':
#                 discount_rate = reward['discount'] * amount_total
#                 point_cost = discount_rate * reward["point_cost"]
#
#                 if point_cost <= client['loyalty_points']:
#                     _logger.warning('ready to render')
#                     super(hotel_folio, folio_id).write({'isbutton': True})
#         return folio_id
#
#     @api.multi
#     def write(self, vals):
#         folio_id = super(hotel_folio, self).write(vals)
#         points_spent = vals.get('points_spent')
#         _logger.warning(vals)
#
#         for f in self:
#             amount_total = f['amount_total']
#             client = f['partner_id']
#             loyalty_id = client['loyalty_id']
#             check_spent_point = 0
#
#             if not loyalty_id:
#                 super(hotel_folio, self).write({'isbutton': False})
#
#             # loop to check whether render discount button or not
#             for reward in loyalty_id['reward_ids']:
#                 if reward['type'] == 'discount':
#                     discount_rate = reward['discount'] * amount_total
#                     point_cost = discount_rate * reward["point_cost"]
#
#                     if point_cost <= client['loyalty_points']:
#                         super(hotel_folio, self).write({'isbutton': True})
#                     else:
#                         super(hotel_folio, self).write({'isbutton': False})
#
#             if f['state'] != 'draft':
#                 super(hotel_folio, self).write({'isbutton': False})
#
#             for service in f['service_lines']:
#                 for reward in loyalty_id['reward_ids']:
#                     if reward['type'] == 'discount':
#                         _logger.warning('check_spent_point')
#                         _logger.warning(service['product_id'])
#                         if service['product_id'] == reward['discount_product_id']:
#                             check_spent_point = 1
#             _logger.warning(check_spent_point)
#             if check_spent_point == 0:
#                 if points_spent == None:
#                     super(hotel_folio, self).write({'points_spent': 0})
#         return folio_id
#
#     @api.multi
#     def discount_by_point(self):
#         global discount_rate, discount_product
#         for h_f in self:
#             amount_total = h_f['amount_total']
#             client = h_f['partner_id']
#             loyalty_id = client['loyalty_id']
#             for service in h_f['service_lines']:
#                 for reward in loyalty_id['reward_ids']:
#                     if reward['type'] == 'discount':
#                         if service['product_id'] == reward['discount_product_id']:
#                             return
#
#             for reward in loyalty_id['reward_ids']:
#                 if reward['type'] == 'discount':
#                     discount_rate = reward['discount'] * amount_total
#                     point_spent = round(discount_rate * reward["point_cost"])
#                     discount_product = reward['discount_product_id']
#                     h_f.write({'points_spent': point_spent})
#
#             hsl_obj = self.env['hotel.service.line']
#             so_line_obj = self.env['sale.order.line']
#             values = {
#                 'order_id': h_f['order_id'].id,  # this is the id of sale order
#                 'name': discount_product.name,
#                 'product_id': discount_product.id,
#                 'product_uom': discount_product.uom_id.id,
#                 'product_uom_qty': 1,
#                 'price_unit': -discount_rate
#             }
#             sol_rec = so_line_obj.create(values)
#             hsl_obj.create({'folio_id': h_f.id, 'service_line_id': sol_rec.id})
#
#     def action_wait(self, cr, uid, ids, context=None):
#         super(hotel_folio, self).action_wait(cr, uid, ids, context=context)
#         points = 0
#         room_totalQty = 0
#         service_totalQty = 0
#         for h_f in self.browse(cr, uid, ids, context=context):
#             client = h_f['partner_id']
#             loyalty_program = client['loyalty_id']
#             room_lines = h_f['room_lines']
#             service_lines = h_f['service_lines']
#             for room in room_lines:
#                 room_subtotal = room['price_subtotal']
#                 room_totalQty = room_totalQty + room['product_uom_qty']
#                 for rule in loyalty_program['rule_ids']:
#                     if room['product_id']['categ_id'] == rule['wh_categ']:
#                         points = points + room_subtotal * rule['pp_currency']
#                         points = points + room['product_uom_qty'] * rule['pp_product']
#                     elif room['product_id'] == rule['product_id']:
#                         points = points + room['product_uom_qty'] * rule['pp_product']
#                         points = points + room_subtotal * rule['pp_currency']
#             for service in service_lines:
#                 service_subtotal = service['price_subtotal']
#                 if service_subtotal <= 0:
#                     continue
#                 service_totalQty = service_totalQty + service['product_uom_qty']
#                 for rule in loyalty_program['rule_ids']:
#                     if service['product_id']['categ_id'] == rule['wh_categ']:
#                         points = points + service_subtotal * rule['pp_currency']
#                         points = points + service['product_uom_qty'] * rule['pp_product']
#                     elif service['product_id'] == rule['product_id']:
#                         points = points + service['product_uom_qty'] * rule['pp_product']
#             total_qty = room_totalQty + service_totalQty
#             if loyalty_program:
#                 points = points + h_f['amount_total'] * loyalty_program['pp_currency']
#                 points = points + total_qty * loyalty_program['pp_product']
#                 points = points + loyalty_program['pp_order']
#             h_f.write({'points_won': round(points)})
#
#     @api.multi
#     def action_done(self):
#         super(hotel_folio, self).action_done()
#         for f in self:
#             client = f['partner_id']
#             new_point = round(client['loyalty_points'] - f['points_spent'] + f['points_won'])
#             client.write({'loyalty_points': new_point})
