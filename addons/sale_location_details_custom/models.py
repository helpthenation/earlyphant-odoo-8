# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.addons.report_sale_location.pos_locationdetails import pos_detail

class PosDetailsCustom(pos_detail):

    def _pos_sales_details_custom(self, form):

        res = self.pool.get('report.pos.order').read_group(self.cr, self.uid, groupby=["product_categ_id"],
           fields=["product_categ_id", "product_qty", "price_total",
                   'total_discount'],
           domain=[('date', '>=', form['date_start'] + ' 00:00:00'),
                   ('date', '<=', form['date_end'] + ' 23:59:59'),
                   ('state', 'in', ['done', 'paid', 'invoiced']),
                   ('location_id','in',[form['location_id'][0]])
                   ])
        for r in res:
            self.qty += r['product_qty']
            self.total += r['price_total']
            self.discount += r['total_discount']

        return res

    # Hotel Card ########################
    def _is_restaurant(self,form):

        if form['location_id'][0] == 48:
            return True
        else:

            return False

    def _get_daily_hotel_card_order(self, form):
        order_obj = self.pool.get('hotel.restaurant.order')
        res = order_obj.read_group(self.cr,self.uid,groupby=["order_no"],fields=[],domain=[
            ('o_date','>=',form['date_start']+' 00:00:00'),
            ('o_date', '<=', form['date_end'] + ' 23:59:59'),
            ('state', '=','done'),
        ])
        data = []
        for order in res:
            dic = dict()
            ids=order_obj.search(self.cr,self.uid,[('order_no','=',order['order_no'])])
            order_ids = order_obj.browse(self.cr,self.uid,ids)
            dic.update({'order_date':order_ids.o_date,'order_no':order_ids.order_no,'subtotal':order_ids.amount_subtotal,
                        'vat':10*order_ids.amount_subtotal/100,'total':order_ids.amount_subtotal+10*order_ids.amount_subtotal/100})
            self.total_vat += dic['vat']
            data.append(dic)
        return data

    def _get_daily_hotel_card_details(self, form):
        order_obj = self.pool.get('hotel.restaurant.order')
        res = order_obj.read_group(self.cr,self.uid,groupby=["order_no"],fields=[],domain=[
            ('o_date','>=',form['date_start']+' 00:00:00'),
            ('o_date', '<=', form['date_end'] + ' 23:59:59'),
            ('state', '=','done'),
        ])
        categ={}
        for order in res:
            ids=order_obj.search(self.cr,self.uid,[('order_no','=',order['order_no'])])
            order_ids = order_obj.browse(self.cr,self.uid,ids)

            for list in order_ids.order_list:
                categ_name = list.name.categ_id.name
                if categ_name not in categ:
                    qty=float(list.item_qty)
                    categ.update({categ_name:[0]*3})
                    categ[categ_name][2]=list.price_subtotal
                    categ[categ_name][0]=qty
                    categ[categ_name][1]=float(list.discount * (float(list.item_rate)*qty)/100)
                else:
                    categ[categ_name][2] += list.price_subtotal
                    categ[categ_name][0] += float(list.item_qty)
                    categ[categ_name][1] += float(float(list.discount) * (float(list.item_rate) * float(list.item_qty)) / 100)

        for cat in categ:
            self.hc_total_discount += categ[cat][1]
            self.total_revenue += categ[cat][2]
            self.total_item_qty += categ[cat][0]
        return categ

    def _get_total_qty(self):
        return self.total_item_qty
    def _get_total_discount(self):
        return self.hc_total_discount

    def _get_total_vat(self):
        return self.total_vat

    def _get_total_revenue(self):
        return self.total_revenue
    #############
    def _is_activity(self,form):
        if form['location_id'][0] == 32:
            return True
        else:
            return False

    def _get_daily_activity_order(self, form):
        order_obj = self.pool.get('activity')
        res = order_obj.read_group(self.cr,self.uid,groupby=["name"],fields=[],domain=[
            ('date_order','>=',form['date_start']+' 00:00:00'),
            ('date_order', '<=', form['date_end'] + ' 23:59:59'),
            ('state', '=','done'),
        ])
        data = []
        for order in res:
            dic = dict()
            ids=order_obj.search(self.cr,self.uid,[('name','=',order['name'])])
            order_ids = order_obj.browse(self.cr,self.uid,ids)
            dic.update({
                'order_date':order_ids.date_order,
                'order_no':order_ids.name,
                'subtotal': order_ids.amount_subtotal,
                'vat': 10 * order_ids.amount_subtotal / 100,
                'total': order_ids.amount_subtotal + 10 * order_ids.amount_subtotal / 100
            })
            self.activity_total_vat += dic['vat']
            data.append(dic)

        print data
        return data

    def _get_daily_activity_details(self, form):
        order_obj = self.pool.get('activity')
        res = order_obj.read_group(self.cr,self.uid,groupby=["name"],fields=[],domain=[
            ('date_order','>=',form['date_start']+' 00:00:00'),
            ('date_order', '<=', form['date_end'] + ' 23:59:59'),
            ('state', '=','done'),
        ])
        categ={}
        for order in res:
            ids=order_obj.search(self.cr,self.uid,[('name','=',order['name'])])
            order_ids = order_obj.browse(self.cr,self.uid,ids)

            for list in order_ids.booking_items:
                categ_name = list.destination.categ_id.name
                if categ_name not in categ:
                    qty=float(list.qty)
                    categ.update({categ_name:[0]*3})
                    categ[categ_name][2]=list.price_subtotal
                    categ[categ_name][0]=qty
                    categ[categ_name][1]=float(list.discount * (float(list.unit_price)*qty)/100)
                else:
                    categ[categ_name][2] += list.price_subtotal
                    categ[categ_name][0] += float(list.qty)
                    categ[categ_name][1] += float(float(list.discount) * (float(list.unit_price) * float(list.qty)) / 100)
        for cat in categ:
            self.activity_total_discount += categ[cat][1]
            self.activity_total_revenue += categ[cat][2]
            self.activity_total_item_qty += categ[cat][0]
        return categ

    def _get_activity_total_qty(self):
        return self.activity_total_item_qty

    def _get_activity_activity_total_discount(self):
        return self.activity_total_discount

    def _get_activity_total_vat(self):
        return self.activity_total_vat

    def _get_activity_activity_total_revenue(self):
        return self.activity_total_revenue

    def __init__(self, cr, uid, name, context):
        super(PosDetailsCustom, self).__init__(cr, uid, name, context=context)
        self.total_vat = 0.0
        self.hc_total_discount = 0.0
        self.total_revenue = 0.0
        self.total_item_qty = 0.0
        self.activity_total_vat = 0.0
        self.activity_total_discount = 0.0
        self.activity_total_revenue = 0.0
        self.activity_total_item_qty = 0.0
        self.localcontext.update({
            'pos_sales_details_custom': self._pos_sales_details_custom,
            'get_daily_hotel_card_details':self._get_daily_hotel_card_details,
            'get_daily_hotel_card_order':self._get_daily_hotel_card_order,
            'get_total_vat':self._get_total_vat,
            'get_total_discount':self._get_total_discount,
            'get_total_revenue':self._get_total_revenue,
            'get_total_item_qty':self._get_total_qty,
            'is_restaurant':self._is_restaurant,
            'get_daily_activity_details': self._get_daily_activity_details,
            'get_daily_activity_order': self._get_daily_activity_order,
            'get_activity_vat': self._get_activity_total_vat,
            'get_activity_total_discount': self._get_activity_activity_total_discount,
            'get_activity_total_revenue': self._get_activity_activity_total_revenue,
            'get_activity_total_item_qty': self._get_activity_total_qty,
            'is_activity': self._is_activity
        })

class ReportPosDetails(osv.AbstractModel):
    _inherit = 'report.report_sale_location.report_detailsofsales_location'
    _wrapped_report_class = PosDetailsCustom
