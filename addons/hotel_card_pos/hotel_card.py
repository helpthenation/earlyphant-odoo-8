from openerp.exceptions import except_orm, ValidationError
from openerp import models, fields, api, _

class hotelOrder(models.Model):
    _inherit = 'hotel.restaurant.order'

    @api.model
    def create_table_order(self, orders):
        t_number=0;
        partner = 1
        # loop to get orders if there are more than one exists #
        for order in orders:
            partner_id = order['data']['folio_id']['partner_id'][0]
            folio_id = order['data']['folio_id']['id']
            waiter_name = order['data']['user_id']

            # create object for model hotel.restaurant.tables to get all the records#
            table_list_lines = self.env['hotel.restaurant.tables'].search([])

            # compare res.user with res.partner
            user_id = self.env['res.users'].search([('id', '=', waiter_name)])
            for i in self.env['res.partner'].search([]):
                if i.name == user_id.name:
                    partner = i.id

            # table number from POS order #
            table_number = order['data']['table_num']
            if table_number:
                # loop to find the particular table number #
                for each in table_list_lines:
                    if table_number in each.name:
                        t_number = each

                if t_number == 0:
                    raise ValidationError(_('This table number does not exist!'))
                else:
                    # write a dicts into hotel restaurant order table #
                    dicts = {
                        'is_folio': True,
                        'folio_id': folio_id,
                        'cname': partner_id,
                        'waiter_name': partner,
                        # way to write the value into many2many field #
                        'table_no': [(6, 0, [t_number.id])],
                    }
                    # get the id of the self object #
                    res =  self.create(dicts)

                    # create object for model hotel.restaurant.order.list #
                    ord_list_obj = self.env['hotel.restaurant.order.list']

                    # get array of product lines from JSON via 'orders' argument #
                    product_objs = order['data']['lines']

                    for each in product_objs:
                        id = each[2]['product_id']
                        # map product id with menucard in 'hotel.menucard' model #
                        menucard_lines = self.env['hotel.menucard'].search([('product_id','=', id)])
                        if menucard_lines:

                            # write a dicts into hotel_restaurant_order_list table#
                            dicts = {
                                'name': menucard_lines.id,
                                'item_qty': each[2]['qty'],
                                'item_rate':each[2]['price_unit'],
                                'o_list':res.id,
                            }
                            ord_list_obj.create(dicts)
                        else:
                            raise ValidationError(_('Some products do not exist in Hotel Menu Card!'))

                    # call function generate KOT button #
                    res.generate_kot()
                    # call function 'done' button #
                    res.done_order_kot()
            else:
                raise ValidationError(_('Please put table number!'))


       

       


