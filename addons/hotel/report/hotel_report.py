# -*- coding: utf-8 -*-
#############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#############################################################################

import time

import datetime

from openerp import models
from openerp.report import report_sxw
import dateutil



class FolioReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(FolioReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({'time': time,
                                  'get_data': self.get_data,
                                  'get_Total': self.getTotal,
                                  'get_total': self.gettotal,
                                  })
        self.temp = 0.0

#In order to customize hotel folio report:
#hotel_wizard.py, hotel_wizard.xml change order_date, hotel.folio.line, and hotel.service.line add line payment
#hotel_restaurant.py
    def get_data(self, report_date):
        folio_line = self.pool.get('hotel.folio.line')
        room_lines = folio_line.read_group(self.cr,self.uid,groupby=["order_line_id"],fields=[],domain=[
            ('checkin_date','<=',report_date),
            ('checkout_date', '>', report_date),
            ('state', '!=', 'cancel'),
        ])

        res = []
        rep_date = dateutil.parser.parse(report_date).date()

        for line in room_lines:
            ids = folio_line.search(self.cr, self.uid, [('order_line_id', '=', line['order_line_id'][0])])
            line_ids = folio_line.browse(self.cr, self.uid, ids)

            dic = dict()

            dic['state'] = line_ids.state
            dic['cambodian'] = line_ids.folio_id.x_cambodian
            dic['foreigner'] = line_ids.folio_id.x_foreigner
            dic['name'] = line_ids.folio_id.name
            dic['partner_id'] = line_ids.folio_id.partner_id.name
            dic['ref_booking'] = line_ids.folio_id.ref_booking

            d = dict()
            d['price'] = line_ids.price_unit
            d['room_no'] = line_ids.product_id.name
            d['room_categ'] = line_ids.product_id.categ_id.name
            d['checkin'] = dateutil.parser.parse(line_ids.checkin_date).date()
            d['checkout'] = dateutil.parser.parse(line_ids.checkout_date).date()
            # print "sssssssssssssss", line_ids.price_subtotal, line_ids.tax_id

            dic.update({'room_lines': [d]})

            if len(res):
                for rec in res:
                    temp = 0
                    if rec['name'] == dic['name']:
                        rec['room_lines'].append(d)
                        break

                    else:
                        for folio in res[::-1]:
                            if folio['name'] == dic['name']:
                                folio['room_lines'].append(d)
                                temp =1

                    if temp == 0:
                        res.append(dic)
                    break

            else:
                res.append(dic)

            folio_obj = self.pool.get('hotel.folio')
            for folio in res:
                folio.update({'payment_amount':{}})
                id=folio_obj.search(self.cr,self.uid,[('name','=',folio['name'])])
                folio_ids=folio_obj.browse(self.cr,self.uid,id)

                if folio_ids.state =="draft":
                    subtotal = 0
                    folio['payment_amount'].update({'City Ledger':subtotal})
                else:
                    payment = {}
                    for payment_line in folio_ids.hotel_invoice_id.payment_ids:
                        name = payment_line.journal_id.name

                        if name in payment:
                            payment[name] += payment_line.credit
                        else:
                            payment.update({name:payment_line.credit})
                    line_checkout = dateutil.parser.parse(folio_ids.checkout_date).date() - datetime.timedelta(days=1)
                    ch_in = dateutil.parser.parse(folio_ids.checkin_date).date()
                    ch_out = dateutil.parser.parse(folio_ids.checkout_date).date()
                    # print "-------------arrived-----------------", rep_date, " ", line_checkout
                    if rep_date == line_checkout:
                        # print "-------------if----------------------", folio_ids.name
                        for p_n in payment:
                            folio['payment_amount'].update({p_n:payment[p_n]})
                        folio['payment_amount'].update({'City Ledger':folio_ids.hotel_invoice_id.residual, 'invoice': folio_ids.hotel_invoice_id.number, 'receipt': folio_ids.hotel_invoice_id.receipt_no})

                    elif rep_date == ch_in == ch_out:
                        print "-------------elif----------------------", folio_ids.name
                        for p_n in payment:
                            folio['payment_amount'].update({p_n: payment[p_n]})
                        folio['payment_amount'].update({'City Ledger': folio_ids.hotel_invoice_id.residual,
                                                        'invoice': folio_ids.hotel_invoice_id.number,
                                                        'receipt': folio_ids.hotel_invoice_id.receipt_no})

        for f in res:
            f.update({'service_lines': []})

        service_line = self.pool.get('hotel.service.line')
        product_lines = service_line.read_group(self.cr, self.uid, groupby=['service_line_id'], fields=[], domain=[
            ('ser_checkin_date', '<=', report_date),
            ('ser_checkout_date', '>', report_date),
            ('state', '!=', 'cancel'),
        ])

        for service in product_lines:
            is_folio=False
            ids = service_line.search(self.cr, self.uid, [('service_line_id', '=', service['service_line_id'][0])])
            line_ids = service_line.browse(self.cr, self.uid, ids)

            prod = dict()
            prod['categ'] = line_ids.service_line_id.product_id.categ_id.name
            prod['qty'] = line_ids.product_uom_qty
            prod['price'] = line_ids.service_line_id.price_unit

            for fol in res:
                if fol['name'] == line_ids.folio_id.name:
                    fol['service_lines'].append(prod)
                    is_folio=True

            if is_folio == False:
                payment = {}
                new_folio = {}
                new_folio.update({'payment_amount':{}})
                for payment_line in line_ids.folio_id.hotel_invoice_id.payment_ids:
                    name = payment_line.journal_id.name

                    if name in payment:
                        payment[name] += payment_line.credit
                    else:
                        payment.update({name: payment_line.credit})

                for p_n in payment:
                    new_folio['payment_amount'].update({p_n: payment[p_n]})

                new_folio['payment_amount'].update({'City Ledger': line_ids.folio_id.hotel_invoice_id.residual, 'invoice': line_ids.folio_id.hotel_invoice_id.number, 'receipt': line_ids.folio_id.hotel_invoice_id.receipt_no})

                new_folio.update({'state': line_ids.folio_id.state,
                            'cambodian': line_ids.folio_id.x_cambodian,
                            'foreigner': line_ids.folio_id.x_foreigner,
                            'ref_booking': line_ids.folio_id.ref_booking,
                            'name': line_ids.folio_id.name,
                            'service_lines': [prod],
                            'room_lines':[{'checkin': dateutil.parser.parse(line_ids.ser_checkin_date).date(),
                                            'checkout': dateutil.parser.parse(line_ids.ser_checkout_date).date(),
                                           'room_no': line_ids.product_id.name,
                                           'room_categ': line_ids.product_id.categ_id.name,
                                           'price': 0}],
                            'partner_id': line_ids.folio_id.partner_id.name,
                            })

                res.append(new_folio)

        print "------", res
        return res

    def gettotal(self, total):
        self.temp = self.temp + float(total)
        return total

    def getTotal(self):
        return self.temp

class ReportLunchorder(models.AbstractModel):
    _name = 'report.hotel.report_hotel_folio'
    _inherit = 'report.abstract_report'
    _template = 'hotel.report_hotel_folio'
    _wrapped_report_class = FolioReport
