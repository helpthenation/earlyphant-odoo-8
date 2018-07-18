from dateutil.parser import parse

import datetime

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time

class Activity(models.Model):
    _name = 'activity'

    @api.constrains('booking_items')
    def _set_sub_total(self):
        amount_subtotal = 0
        for line in self.booking_items:
            amount_subtotal += line.price_subtotal
        self.amount_subtotal = amount_subtotal
         
    @api.constrains('amount_subtotal')
    def set_vat_value(self):
        if self.amount_subtotal:
            value = self.amount_subtotal * 0.1
            self.vat_value = value
        else:
            self.vat_value = 0.0
        self.amount_total = self.amount_subtotal + self.vat_value
    
    
    name=fields.Char('Reference No',readonly=True)
    partner_id=fields.Many2one('res.partner','Customer',readonly=True,required=True,
                             states={'draft': [('readonly', False)]})
    date_order=fields.Datetime('Date Ordered', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 default=(lambda *a:
                                          time.strftime
                                          (DEFAULT_SERVER_DATETIME_FORMAT)))
    folio_id=fields.Many2one('hotel.folio','Folio No',readonly=True,
                             states={'draft': [('readonly', False)]},required=True,
                             domain=[('state', '=', 'draft')])
    room_no=fields.Many2one('product.product',"Room Number",readonly=True,required=True,
                             states={'draft': [('readonly', False)]})
    booking_items=fields.One2many('activity.item','order_id','Items Line',readonly=True,required=True,
                              states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('manual_invoice','Progress'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')])
    amount_subtotal = fields.Float('Subtotal')
    vat_value = fields.Float("VAT")
    amount_total = fields.Float("Total")

    _defaults = {'state': 'draft'}


    @api.multi
    def confirm(self):
        self.write({'state':'confirm'})

        line_list = []
        for line in self.booking_items:
            line_dict = dict()
            line_dict.update({
                'reference':self.name,
                'name': self.partner_id.name,
                'email': self.partner_id.email,
                'phone': self.partner_id.phone,
                'destination_id': line.destination.id,
                'amount': int(line.qty),
                'status': self.state
            })
            line_list.append(line_dict)

    @api.multi
    def write(self, vals):
        res = super(Activity, self).write(vals)
        # if self.state!='draft':
        #     line_list = []
        #     for line in self.booking_items:
        #         line_dict = dict()
        #         line_dict.update({
        #             'reference': self.name,
        #             'name': self.partner_id.name,
        #             'email': self.partner_id.email,
        #             'phone': self.partner_id.phone,
        #             'destination_id': line.destination.id,
        #             'amount': int(line.qty),
        #             'status':self.state
        #         })
        #         line_list.append(line_dict)
        return res

    @api.multi
    def generate_to_folio(self):
        hotel_folio_obj = self.env['hotel.folio']
        hsl_obj = self.env['hotel.service.line']
        so_line_obj = self.env['sale.order.line']
        for order in self.booking_items:
            values = {'order_id':self.folio_id.order_id.id,
                      'name': order.destination.name,
                      'product_id': order.destination.id,
                      'product_uom_qty': order.qty,
                      'price_unit': order.unit_price,
                      #'price_subtotal': (order.qty * order.unit_price),
                      'discount':order.discount
                      }
            sol_rec = so_line_obj.create(values)

            # change o_date to ser_checkin_date, ser_checkout_date, for hotel_folio_report data
            o_date = self.date_order
            o_time = o_date[11] + o_date[12]
            check_time = int(o_time) + 7

            if check_time >= 12:
                in_date = parse(o_date).replace(hour=7, minute=00, second=00)
                out_date = (in_date + datetime.timedelta(days=1)).replace(hour=5, minute=00, second=00)

                hsl_obj.create({'folio_id': self.folio_id.id,
                                'service_line_id': sol_rec.id,
                                'ser_checkin_date': str(in_date),
                                'ser_checkout_date': str(out_date),
                                })
            else:
                date_obj = parse(o_date)
                in_date = (date_obj - datetime.timedelta(days=1)).replace(hour=7, minute=00, second=00)
                out_date = date_obj.replace(hour=5, minute=00, second=00)
                hsl_obj.create({'folio_id': self.folio_id.id,
                                'service_line_id': sol_rec.id,
                                'ser_checkin_date': str(in_date),
                                'ser_checkout_date': str(out_date),
                                })

            hf_rec = hotel_folio_obj.browse(self.folio_id.id)
            self.write({'state':'done'})

    @api.multi
    def done_cancel(self):
        names = []
        for line in self.booking_items:
            names.append(line.destination.id)
        for line in self.folio_id.service_lines:
            if line.product_id.id in names:
                line.unlink()
        self.write({'state': 'cancel'})
        return True

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('activity.sequence')
        return super(Activity, self).create(vals)

    @api.onchange('folio_id')
    def get_folio_partner_id(self):

        for rec in self:
            self.partner_id = False
            self.room_no = False
            if rec.folio_id:
                self.partner_id = rec.folio_id.partner_id.id
                if rec.folio_id.room_lines:
                    self.room_no = rec.folio_id.room_lines[0].product_id

class ActivityItem(models.Model):
    _name = 'activity.item'

    @api.one
    def _sub_total(self):
        discount_amount = (self.unit_price * self.qty)*(self.discount/100)
        self.price_subtotal = self.unit_price * self.qty - discount_amount

    name=fields.Char('Activity Line')
    destination=fields.Many2one('product.product','Product',required=True)
    order_id=fields.Many2one('activity','Reference')
    customer=fields.Many2one('res.partner','Customer')
    date_of_booking=fields.Datetime('Date of Booking')
    qty=fields.Float('Quantity',required=True)
    unit_price=fields.Float('Unit Price',required=True)
    price_subtotal = fields.Float('Sub Total',compute='_sub_total',readonly=True)
    discount = fields.Float('Discount')

    


   
