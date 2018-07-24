from openerp import models, fields, api, _
import datetime
import time
import logging
import requests
import yaml
import xmltodict, json
import xml.etree.cElementTree as ET
from dateutil.parser import parse
from openerp.exceptions import except_orm, ValidationError
import requests.exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)


class GetBooking(models.Model):
    _name = 'schedulling.getbooking.hls'
    

    @api.model
    def request_to_hls(self):
        hls_booking = dict()
        _logger.info('request_to_hls======>')

        GetBooking = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/booking/soap">
            <soapenv:Header/>
            <soapenv:Body>
            <soap:GetBookings>
            <Request>
            <StartDate></StartDate>
            <EndDate></EndDate>
            <DateFilter>LastModifiedDate</DateFilter>
            <BookingStatus></BookingStatus>
            <BookingId></BookingId>
            <ExtBookingRef></ExtBookingRef>
            <NumberBookings></NumberBookings>
            <Credential>
            <ChannelManagerUsername>vkirirom</ChannelManagerUsername> 
            <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword> 
            <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId> 
            <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey> 
            </Credential>
            <Language>en</Language>
            </Request>
            </soap:GetBookings>
            </soapenv:Body>
            </soapenv:Envelope>
            """
        ReadNotification = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/booking/soap" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
            <soapenv:Header/>
            <soapenv:Body>
            <soap:ReadNotification>
            <Request>
            <Bookings>
            </Bookings>
            <Credential>
            <ChannelManagerUsername>vkirirom</ChannelManagerUsername> 
            <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword> 
            <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId> 
            <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey> 
            </Credential>
            <Language>en</Language>
            </Request>
            </soap:ReadNotification>
            </soapenv:Body>
            </soapenv:Envelope>
            """

        today = datetime.date.today()
        body_req = ET.fromstring(GetBooking)
        for statDate in body_req.getiterator('StartDate'):
            statDate.text = str(today)
        for endDate in body_req.getiterator('EndDate'):
            endDate.text = str(today)
        xmlstr = ET.tostring(body_req, encoding='utf8', method='xml')
        headers = {"Content-Type": "application/xml"}  # set what your server accepts

        try:
            response = requests.post("https://api.hotellinksolutions.com/services/booking/soap", data=xmlstr,
                                     headers=headers)
            str_xml = xmltodict.parse(response.content)
            str_json = json.dumps(str_xml)
            booking_hls = yaml.load(str_json)

            if booking_hls['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:GetBookingsResponse']['GetBookingsResult'][
                'Bookings'] == None:
                _logger.info("No Booking Transaction")
            
            else:
                booking_resp = \
                    booking_hls['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:GetBookingsResponse']['GetBookingsResult'][
                        'Bookings']['ns1:Booking']
                else_data = dict()
                dict_ids = ""
                else_case = "False"

                ### update data to hls_booking dictionary
                for booking in booking_resp:
                    if type(booking) == dict:
                        booking_id = booking['BookingId']
                        data = dict()
                        for val in booking:
                            if val == 'BookingId':
                                continue
                            data.update({val: booking[val]})
                            hls_booking.update({booking_id: data})
                    else:
                        else_case = "True"
                        if booking == "BookingId":
                            dict_ids = booking_resp[booking]
                        else:
                            else_data.update({booking: booking_resp[booking]})
                if else_case == "True":
                    hls_booking.update({dict_ids: else_data})
                ###############################################

                categ_obj = self.env['product.category']
                reservation_obj = self.env['hotel.reservation']
                partner_obj = self.env['res.partner']
                warehouse_obj = self.env['stock.warehouse']
                hotel_room_obj = self.env['hotel.room']
                room_reservation_line_obj = self.env['hotel.room.reservation.line']
                hotel_reservation_line_obj = self.env['hotel_reservation.line']
                element_notification = ET.fromstring(ReadNotification)

                for hls_id in hls_booking:
                    _logger.info(hls_id)
                    #### add item ReadNotification
                    for request in element_notification.getiterator('Request'):
                        for data in request:
                            if data.tag == "Bookings":
                                item_element = ET.fromstring("<item></item>")
                                data.append(item_element)
                                for item in data:
                                    if item.text == None:
                                        item.text = hls_id
                                break
                    ###############################
                    booking_status = ""
                    if hls_booking[hls_id]['BookingStatus'] == "Confirmed":
                        booking_status = "confirm"
                    elif hls_booking[hls_id]['BookingStatus'] == "Operational":
                        booking_status = "done"
                    elif hls_booking[hls_id]['BookingStatus'] == "Cancelled":
                        booking_status = "cancel"
                    elif hls_booking[hls_id]['BookingStatus'] == "Completed":
                        _logger.info("HLS COMPLETED")
                        continue
                    booking_id = hls_id
                    hotel_reservation_id = reservation_obj.search([('booking_id', '=', hls_id)])

                    if hotel_reservation_id.id:
                        if hotel_reservation_id.state != booking_status:
                            if booking_status == "cancel":
                                hotel_reservation_id.write({'state': 'cancel','check_write':'cancelbysystem'})

                                room_reservation_line = room_reservation_line_obj.search([('reservation_id',
                                                                                           'in',
                                                                                           hotel_reservation_id.ids)])
                                room_reservation_line.write({'state': 'unassigned'})
                                reservation_lines = hotel_reservation_line_obj.search([('line_id',
                                                                                        'in',
                                                                                        hotel_reservation_id.ids)])
                                # for reservation_line in reservation_lines:
                                #     reservation_line.reserve.write({'isroom': True,
                                #                                     'status': 'available'})
                            elif booking_status == "done":
                                #hotel_reservation_id._create_folio()
                                _logger.info("**********done")
                                hotel_folio_obj = self.env['hotel.folio']
                                room_obj = self.env['hotel.room']
                                for reservation in hotel_reservation_id:
                                    folio_lines = []
                                    checkin_date = reservation['checkin']
                                    checkout_date = reservation['checkout']
                                    if not hotel_reservation_id.checkin < hotel_reservation_id.checkout:
                                        raise except_orm(_('Error'),
                                                         _('Checkout date should be greater \
                                                                 than the Checkin date.'))
                                    duration_vals = (hotel_reservation_id.onchange_check_dates
                                                     (checkin_date=checkin_date,
                                                      checkout_date=checkout_date, duration=False))
                                    duration = duration_vals.get('duration') or 0.0
                                    folio_vals = {
                                        'date_order': reservation.date_order,
                                        'warehouse_id': reservation.warehouse_id.id,
                                        'partner_id': reservation.partner_id.id,
                                        'pricelist_id': reservation.pricelist_id.id,
                                        'partner_invoice_id': reservation.partner_invoice_id.id,
                                        'partner_shipping_id': reservation.partner_shipping_id.id,
                                        'checkin_date': reservation.checkin,
                                        'checkout_date': reservation.checkout,
                                        'duration': duration,
                                        'reservation_id': reservation.id,
                                        'service_lines': reservation['folio_id']
                                    }
                                    date_a = (datetime.datetime
                                              (*time.strptime(reservation['checkout'],
                                                              DEFAULT_SERVER_DATETIME_FORMAT)[:5]))
                                    date_b = (datetime.datetime
                                              (*time.strptime(reservation['checkin'],
                                                              DEFAULT_SERVER_DATETIME_FORMAT)[:5]))
                                    for line in reservation.reservation_line:
                                        for r in line.reserve:
                                            prod = r.product_id.id
                                            partner = reservation.partner_id.id
                                            price_list = reservation.pricelist_id.id
                                            folio_line_obj = hotel_reservation_id.env['hotel.folio.line']
                                            prod_val = folio_line_obj.product_id_change(
                                                pricelist=price_list, product=prod,
                                                qty=0, uom=False, qty_uos=0, uos=False,
                                                name='', partner_id=partner, lang=False,
                                                update_tax=True, date_order=False
                                            )
                                            prod_uom = prod_val['value'].get('product_uom', False)
                                            price_unit = prod_val['value'].get('price_unit', False)
                                            folio_lines.append((0, 0, {
                                                'checkin_date': checkin_date,
                                                'checkout_date': checkout_date,
                                                'product_id': r.product_id and r.product_id.id,
                                                'name': reservation['reservation_no'],
                                                'product_uom': prod_uom,
                                                'price_unit': price_unit,
                                                'product_uom_qty': ((date_a - date_b).days) + 1}))
                                            res_obj = room_obj.browse([r.id])
                                            #res_obj.write({'status': 'occupied', 'isroom': False})
                                    folio_vals.update({'room_lines': folio_lines})
                                    folio = hotel_folio_obj.create(folio_vals)
                                    self._cr.execute('insert into hotel_folio_reservation_rel'
                                                     '(order_id, invoice_id) values (%s,%s)',
                                                     (reservation.id, folio.id)
                                                     )
                                reservation.write({'state': 'done','check_write':'cancelbysystem'})
                        else:
                            _logger.info("The same status")
                            #CheckIn = hls_booking[hls_id]["CheckIn"] + "T07:00:00"
                            hls_checkin= parse(hls_booking[hls_id]["CheckIn"] + "T07:00:00")
                            hls_checkout = parse(hls_booking[hls_id]["CheckOut"] + "T05:00:00")

                            for booking_item in hls_booking[hls_id]["Rooms"]:
                                odoo_room_type_id = []
                                deleteId = []
                                addId = []
                                hls_roomId = []
                                check_id = []

                                ############ add room.id deleteId[], add room_type_id to addId[]
                                for arr_room in hls_booking[hls_id]["Rooms"][booking_item]:

                                    if type(arr_room) != dict:
                                        hls_roomId.append(hls_booking[hls_id]["Rooms"][booking_item]["RoomId"])
                                        break
                                    else:

                                        hls_roomId.append(arr_room["RoomId"])

                                for reservation_line in hotel_reservation_id.reservation_line:
                                    for room in reservation_line.reserve:
                                        odoo_room_type_id.append(room.room_type_id)

                                for reservation_line in hotel_reservation_id.reservation_line:
                                    loop_again = 0
                                    rang = 0
                                    for room in reservation_line.reserve:
                                        if room.room_type_id not in check_id:
                                            odoo_count = odoo_room_type_id.count(room.room_type_id)
                                            hls_count = hls_roomId.count(room.room_type_id)
                                            if hls_count == 0:
                                                deleteId.append(room.id)
                                            elif hls_count < odoo_count:
                                                loop_again = 1
                                                rang = odoo_count - hls_count
                                            check_id.append(room.room_type_id)
                                            break
                                    if loop_again == 1:
                                        for room in reservation_line.reserve:
                                            if room.room_type_id == check_id[-1]:
                                                if rang == 0:
                                                    break
                                                else:
                                                    deleteId.append(room.id)
                                                    rang = rang - 1
                                check_id = []
                                for id in hls_roomId:
                                    if id not in check_id:
                                        temp = odoo_room_type_id.count(id)
                                        hls_count = hls_roomId.count(id)
                                        if temp == 0:
                                            addId.append(id)
                                        elif temp == hls_count:
                                            print "nothing"
                                        elif temp < hls_count:
                                            for i in range(0, hls_count - temp):
                                                addId.append(id)
                                        check_id.append(id)
                                ####################################################

                                line_ids = room_reservation_line_obj.search(
                                    [('reservation_id.id', '=', hotel_reservation_id.id)])
                                for line in line_ids:
                                    if line.room_id.id in deleteId:
                                        line.unlink()

                                hr_line_ids = hotel_reservation_line_obj.search(
                                    [('line_id', '=', hotel_reservation_id.id)])
                                for line_type in hr_line_ids:
                                    ##### we use raw query because we want to delete line many2many relationship
                                    for room in line_type.reserve:
                                        if room.id in deleteId:
                                            reservation_line_id = line_type.id
                                            roomId = room.id
                                            self._cr.execute(
                                                "delete from hotel_reservation_line_room_rel where (hotel_reservation_line_id=%s and room_id=%s)",
                                                (reservation_line_id, roomId))
                                            #############################################################################

                                for room_type_id in addId:
                                    room_ids = hotel_room_obj.search([('room_type_id', '=', room_type_id)])
                                    for r in room_ids:
                                        available = 1
                                        for line in r.room_reservation_line_ids:
                                            # if ((parse(CheckIn) >= parse(line.check_in) and parse(CheckIn) <= parse(
                                            #         line.check_out)) and line.status != "cancel"):
                                            #     available = 0
                                            #     break
                                            if (hls_checkin in (parse(line.check_in),parse(line.check_out)) or hls_checkout in (parse(line.check_in),parse(line.check_out)) or( hls_checkin < parse(line.check_in) and hls_checkout > parse(line.check_out)))  and line.status != "cancel":
                                                available = 0
                                                break
                                            else:
                                                available = 1
                                        if available == 1:
                                            vals = {
                                                'line_id': hotel_reservation_id.id,
                                                'categ_id': r.categ_id.id,
                                                'name': False,
                                                'reserve': [[6, False, [r.id]]]}
                                            hotel_reservation_line_obj.create(vals)
                                            vals = {
                                                'room_id': r.id,
                                                'reservation_id': hotel_reservation_id.id,
                                                'check_in': hotel_reservation_id.checkin,
                                                'check_out': hotel_reservation_id.checkout,
                                                'state': 'assigned',
                                            }
                                            r.write({'isroom': False, 'status': 'occupied'})
                                            room_reservation_line_obj.create(vals)
                                            break
                    else:
                        _logger.info("Create new Reservation")
                        warehouse_ids = warehouse_obj.browse([4])
                        warehouse_id = {}
                        date_orderd = ""
                        checkIn = ""
                        checkOut = ""
                        array_type = []
                        warehouse_id = warehouse_ids.id
                        check_vals = ""
                        guest = dict()
                        for data in hls_booking[hls_id]:
                            if hls_booking[hls_id]['BookingStatus'] == "Cancelled":
                                # checking if the reservation from HLS created and immediatedly cancel
                                check_vals = "Skip"
                                break
                            else:
                                if data == "BookingDate":
                                    date_orderd = hls_booking[hls_id][data]
                                if data == "CheckIn":
                                    checkIn = hls_booking[hls_id][data] + "T07:00:00"
                                elif data == "CheckOut":
                                    checkOut = hls_booking[hls_id][data] + "T05:00:00"

                                ######### Mapping Room ##########
                                elif data == "Rooms":
                                    for booking_items in hls_booking[hls_id][data]:
                                        for arr_room in hls_booking[hls_id][data][booking_items]:
                                            if type(arr_room) == dict:
                                                for each_room_data in arr_room:
                                                    if each_room_data == "RoomId":
                                                        RoomId = arr_room[each_room_data]
                                                        type_id = categ_obj.search([('room_type_id', '=', RoomId)])
                                                        array_type.append(type_id.id)
                                            else:
                                                if arr_room == "RoomId":
                                                    RoomId = hls_booking[hls_id][data][booking_items][arr_room]
                                                    type_id = categ_obj.search([('room_type_id', '=', RoomId)])
                                                    array_type.append(type_id.id)
                                ################################

                                elif data == "Guests":
                                    guest = {
                                        'name': hls_booking[hls_id][data]['FirstName'],
                                        'last_name': hls_booking[hls_id][data]['LastName'],
                                        'email': hls_booking[hls_id][data]['Email'],
                                        'phone': hls_booking[hls_id][data]['Phone'],
                                        'city': hls_booking[hls_id][data]['City'],
                                        'zip': hls_booking[hls_id][data]['PostalCode'],
                                    }
                        if check_vals == "Skip":
                            continue
                        else:
                            ################# select available room by type_id after mapped room
                            hls_checkin = parse(checkIn)
                            hls_checkout = parse(checkOut)
                            room_dic = {}
                            for id in array_type:
                                if id not in room_dic:
                                    room_dic.update({id: [id]})
                                else:
                                    room_dic[id].append(id)
                            reservation_line = []
                            for id in room_dic:
                                arr_room = []
                                room_ids = hotel_room_obj.search([('categ_id', '=', id)])
                                len_room = len(room_dic[id])
                                t = 0
                                for r in room_ids:
                                    available = 1
                                    for line in r.room_reservation_line_ids:
                                        if (hls_checkin in (parse(line.check_in),parse(line.check_out)) or hls_checkout in (parse(line.check_in),parse(line.check_out)) or( hls_checkin < parse(line.check_in) and hls_checkout > parse(line.check_out)))  and line.status != "cancel":
                                            available = 0
                                            break
                                        else:
                                            available = 1

                                    if available == 1:
                                        if t < len_room:
                                            arr_room.append(r.id)
                                            t = t + 1
                                        else:
                                            break
                                reservation_line.append(
                                    [0, False, {'categ_id': id, 'name': False, 'reserve': [[6, False, arr_room]]}])
                            #################################

                            partner_ids = self.env['res.partner']
                            if guest['email']:
                                partner_ids = partner_obj.search([('email', '=', guest['email'])])

                            if partner_ids.id:
                                partner_id = partner_ids.id
                            else:
                                partner_id = partner_obj.create(guest).id
                            vals = {
                                'date_order': date_orderd,
                                'checkin': checkIn,
                                'checkout': checkOut,
                                'warehouse_id': warehouse_id,
                                'booking_id': booking_id,
                                'partner_id': partner_id,
                                'partner_shipping_id': partner_id,
                                'partner_order_id': partner_id,
                                'partner_invoice_id': partner_id,
                                'pricelist_id': 1,
                                'reservation_line': reservation_line
                            }
                            reservation_id = reservation_obj.create(vals)

                            self._cr.execute("select count(*) from hotel_reservation as hr "
                                 "inner join hotel_reservation_line as hrl on \
                                 hrl.line_id = hr.id "
                                 "inner join hotel_reservation_line_room_rel as \
                                 hrlrr on hrlrr.room_id = hrl.id "
                                 "where (checkin,checkout) overlaps \
                                 ( timestamp %s, timestamp %s ) "
                                 "and hr.id <> cast(%s as integer) "
                                 "and hr.state = 'confirm' "
                                 "and hrlrr.hotel_reservation_line_id in ("
                                 "select hrlrr.hotel_reservation_line_id \
                                 from hotel_reservation as hr "
                                 "inner join hotel_reservation_line as \
                                 hrl on hrl.line_id = hr.id "
                                 "inner join hotel_reservation_line_room_rel \
                                 as hrlrr on hrlrr.room_id = hrl.id "
                                 "where hr.id = cast(%s as integer) )",
                                 (reservation_id.checkin, reservation_id.checkout,
                                  str(reservation_id.id), str(reservation_id.id)))
                            res = self._cr.fetchone()

                            roomcount = res and res[0] or 0.0
                            if roomcount:
                                raise except_orm(_('Warning'), _('You tried to confirm \
                                                reservation with room those already reserved in this \
                                                reservation period'))
                            else:
                                reservation_id.write({'state': 'confirm'})
                                for line_id in reservation_id.reservation_line:
                                    line_id = line_id.reserve
                                    for room_id in line_id:
                                        vals = {
                                            'room_id': room_id.id,
                                            'reservation_id': reservation_id.id,
                                            'check_in': reservation_id.checkin,
                                            'check_out': reservation_id.checkout,
                                            'state': 'assigned',
                                        }
                                        #room_id.write({'isroom': False, 'status': 'occupied'})
                                        room_reservation_line_obj.create(vals)
                            vals.clear()

                notification_str = ET.tostring(element_notification)
                _logger.info(notification_str)

                # try:
                #     inform_to_hls = requests.post("https://api.hotellinksolutions.com/services/booking/soap",
                #                                   data=notification_str,
                #                                   headers=headers)
                # except requests.exceptions.ConnectTimeout as e:
                #     _logger.info(e)
                
                # except requests.exceptions.ConnectionError as e:
                #     _logger.info(e)

            return True

#        except requests.exceptions.ConnectTimeout as e:
#            _logger.warning(e)

        except requests.exceptions.ConnectionError as e:
            _logger.info(e)


class save_booking(models.Model):
    _inherit = 'hotel.reservation'
    booking_id = fields.Char('HLS Reference', readonly=True)

    @api.multi
    def define_notifybooking(self):
        NotifyBooking = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/booking/soap" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
            <soapenv:Header/>
            <soapenv:Body>
            <soap:NotifyBookings>
            <Request>
            <Bookings>
                <Booking>
                <NotificationType>New</NotificationType>
                <BookingId></BookingId>
                <ExtBookingRef>test-ext-ref</ExtBookingRef>
                <Currency>USD</Currency>
                <CheckIn></CheckIn>
                <CheckOut></CheckOut>
                <AdditionalComments></AdditionalComments>
                <GuestDetail>
                <Title>Mr</Title>
                <FirstName></FirstName>
                <LastName></LastName>
                <Email></Email>
                <Phone></Phone>
                <Address></Address>
                <City></City>
                <State></State>
                <Country></Country>
                <PostalCode></PostalCode>
                </GuestDetail>
                <Rooms>
                <BookingItem>
                <RatePlanId></RatePlanId>
                <Adults></Adults>
                <Children></Children>
                <ExtraAdults></ExtraAdults>
                <ExtraChildren></ExtraChildren>
                <TaxFee></TaxFee>
                <TaxFeeArrival></TaxFeeArrival>
                <Discount></Discount>
                <Deposit></Deposit>
                <Amount></Amount>
                </BookingItem>
                </Rooms>
                <ServiceCharge></ServiceCharge>
                <ServiceChargeArrival></ServiceChargeArrival>
                </Booking>
                </Bookings>
                <Credential>
                <ChannelManagerUsername>vkirirom</ChannelManagerUsername> 
                <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword> 
                <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId> 
                <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey> 
                </Credential>
                <Language>en</Language>
                </Request>
                </soap:NotifyBookings>
               </soapenv:Body>
            </soapenv:Envelope>
        """
        xmlstr = ET.fromstring(NotifyBooking)
        price_list_items = self.pricelist_id.version_id.items_id
        reservation_line = self.reservation_line
        hotel_room_obj = self.env['hotel.room']
        sale_price = []
        array_room_id = []
        for lines in reservation_line:
            for room in lines.reserve:
                for items_id in price_list_items:
                    if items_id.categ_id == room.categ_id:
                        sale_price.append((1 + items_id.price_discount) * room.list_price + items_id.price_surcharge)
                    elif not items_id.categ_id:
                        sale_price.append(room.list_price)
                array_room_id.append(room.id)

        booking_item_xml = """
            <BookingItem>
                <RatePlanId></RatePlanId>
                <Adults></Adults>
                <Children></Children>
                <ExtraAdults></ExtraAdults>
                <ExtraChildren></ExtraChildren>
                <TaxFee></TaxFee>
                <TaxFeeArrival></TaxFeeArrival>
                <Discount></Discount>
                <Deposit></Deposit>
                <Amount></Amount>
            </BookingItem>
            """
        for booking in xmlstr.getiterator('Booking'):
            for tag in booking:
                if tag.tag == "Rooms":
                    for i in range(1, len(array_room_id)):
                        elementTree = ET.fromstring(booking_item_xml)
                        tag.append(elementTree)
                    break

        for booking in xmlstr.getiterator('Booking'):
            for tag in booking:
                if tag.tag == "CheckIn":
                    check_in = ""
                    for i in self.checkin:
                        if i == " ":
                            break
                        else:
                            check_in = check_in + i
                    tag.text = check_in
                elif tag.tag == "CheckOut":
                    check_out = ""
                    for i in self.checkout:
                        if i == " ":
                            break
                        else:
                            check_out = check_out + i
                    tag.text = check_out
                elif tag.tag == "GuestDetail":
                    for guest_info in tag:
                        if guest_info.tag == "FirstName":
                            guest_info.text = self.partner_id.name
                        elif guest_info.tag == "LastName":
                            guest_info.text = self.partner_id.last_name
                        elif guest_info.tag == "Email":
                            guest_info.text = self.partner_id.email
                        elif guest_info.tag == "Phone":
                            guest_info.text = self.partner_id.phone

                elif tag.tag == "Rooms":
                    i = 0
                    for booking_item in tag:
                        for room_info in booking_item:
                            RatePlanId = ""
                            if room_info.tag == "Amount":
                                amount_str = str(sale_price[i])
                                room_info.text = amount_str
                            elif room_info.tag == "RatePlanId":
                                category = hotel_room_obj.browse([array_room_id[i]]).categ_id
                                for rate_plan_line in category.rate_plan_line:
                                    RatePlanId = rate_plan_line.rate_plan_id
                                room_info.text = RatePlanId
                        i = i + 1

        body_req = ET.tostring(xmlstr, encoding='utf8', method='xml')
        return body_req

    @api.multi
    def define_inventory_form(self):
        hotel_room_obj = self.env['hotel.room']

        SaveInventory = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/inventory/soap" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
            <soapenv:Header/>
            <soapenv:Body>
            <soap:SaveInventory>
            <Request>
            <Inventories>
            </Inventories>
            <Credential>
            <ChannelManagerUsername>vkirirom</ChannelManagerUsername> 
            <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword> 
            <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId> 
            <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey> 
            </Credential> 
            <Language>en</Language>
            </Request>
            </soap:SaveInventory>
            </soapenv:Body>
            </soapenv:Envelope>
            """
        element_saveInventory = ET.fromstring(SaveInventory)
        inventory = """
            <Inventory>
                <RoomId></RoomId>
                <Availabilities>
                </Availabilities>
            </Inventory>
            """
        room_qty = """
            <Availability>
                <DateRange>
                    <From></From>
                    <To></To>
                </DateRange>
                <Quantity></Quantity>
                <Action>Set</Action>
            </Availability>
            """

        ################### defined SaveInventory form
        room_dict = dict()
        availability = dict()
        for lines in self.reservation_line:
            for room in lines.reserve:
                if room.room_type_id in room_dict:
                    room_dict[room.room_type_id] = room_dict[room.room_type_id] + 1
                    continue
                else:
                    room_dict.update({room.room_type_id: 1})

        for type in room_dict:
            checkin = parse(self.checkin).date()
            checkout = parse(self.checkout).date()
            date_qty = dict()
            while True:
                date_qty.update({checkin.isoformat(): 0})
                room_ids = hotel_room_obj.search([('room_type_id', '=', type)])
                for r in room_ids:
                    available = 1
                    for line in r.room_reservation_line_ids:
                        if ((checkin >= parse(line.check_in).date() and checkin < parse(
                                line.check_out).date()) and line.status != "cancel"):
                            available = 0
                            break
                        else:
                            available = 1

                    if available == 1:
                        date_qty[checkin.isoformat()] = date_qty[checkin.isoformat()] + 1

                checkin = checkin + datetime.timedelta(days=1)
                if checkin == checkout:
                    break
            availability.update({type: date_qty})

        for room_id in availability:
            r = 0
            if room_id == "a5190207-c2a4-47a0-af40-a1c027beeee7":
                r = 1
            # if room_id == "8ceca99d-f593-400e-af47-ae56ba56aff6" or room_id == "52292b22-259f-4257-ba1d-2f901502481c" \
            #         or room_id == "91e8533d-6901-4984-bd96-c146b0beff67" or room_id == "a5190207-c2a4-47a0-af40-a1c027beeee7":
                
            # elif room_id == "6781f3c9-93d2-1502181553-4450-9cae-41f26162d513" \
            #         or room_id == "6ea0fe92-e3f0-464c-bf4a-03c799cd475c":
            #     r = 2
            # elif room_id == "bd697e6c-912f-4a72-af73-c3a754da8677":
            #     r = 4
            # elif room_id == "9ce49877-f934-409f-9711-0a2806c89de4" or room_id == "2a224d81-c2a5-4b7a-91ab-d04a0e5a68b3":
            #     r = 0
            inventory_element = ET.fromstring(inventory)
            for i in inventory_element.getiterator('RoomId'):
                i.text = room_id
            for i in inventory_element.getiterator('Availabilities'):
                for date in availability[room_id]:
                    element = ET.fromstring(room_qty)
                    for data in element.getiterator('From'):
                        data.text = date
                    for data in element.getiterator('To'):
                        data.text = date
                    for data in element.getiterator('Quantity'):
                        if (availability[room_id][date]-r) < 0:
                            data.text = str(0)
                        else:
                            data.text = str(availability[room_id][date]-r)
                    i.append(element)

            for Inventories in element_saveInventory.getiterator('Inventories'):
                Inventories.append(inventory_element)

        Inventory_Body = ET.tostring(element_saveInventory, encoding='utf8', method='xml')
        ###############################################
        return Inventory_Body

    @api.multi
    def confirmed_reservation(self):
        create_booking = super(save_booking, self).confirmed_reservation()

        headers = {"Content-Type": "application/xml"}  # set what your server accepts
        body_req = self.define_notifybooking()
        _logger.info(body_req)
        try:
            response = requests.post("https://api.hotellinksolutions.com/services/booking/soap",
                                     data=body_req, headers=headers)
            _logger.info("==>confirmed_reservation")
            _logger.info(response.content)

            str_xml = xmltodict.parse(response.content)
            str_json = json.dumps(str_xml)
            booking_hls = yaml.load(str_json)
            booking_resp = \
                booking_hls['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:NotifyBookingsResponse']['NotifyBookingsResult'][
                    'Bookings']['ns1:BookingResponse']
            if booking_resp[0]['Success'] == "true":
                super(save_booking, self).write({'booking_id': booking_resp[0]['BookingId']})

                Inventory_Body = self.define_inventory_form()
                response = requests.post("https://api.hotellinksolutions.com/services/inventory/soap",
                                         data=Inventory_Body, headers=headers)
            return create_booking

        # except requests.exceptions.ConnectTimeout:
        #     raise except_orm(_('Connection Timeout'), _('Please Try again later'))

        except requests.exceptions.ConnectionError:
            raise except_orm(_('Warning'), _('You tried to confirm reservation with no internet connection'))

    @api.multi
    def write(self, vals):
        write_con = ["BO", "AG", "BW","cancel","done","MO"]
        booking_id_checking="xxx"

        #used for case generate folio and cancel by system 
        if "check_write" in vals:
            del vals["check_write"]
            res = super(save_booking, self).write(vals)
            return res
        ##################################################

        if self.booking_id:
            booking_id_checking=self.booking_id[0] + self.booking_id[1]
            #update booking_id_checking into xxx because this reservation created by request_to_hls
            if self.state == "draft":
                booking_id_checking="xxx"
            #######################################################################################

        if (self.state in write_con) or (booking_id_checking in write_con):
            raise except_orm(_('Warning'), _("You cant edit this reservation!"))

        if self.state !="draft":
            new_room_ids = []
            pre_room_ids = []
            addId = []
            deleteId = []
            room_reservation_line_obj = self.env['hotel.room.reservation.line']
            hotel_room_obj = self.env['hotel.room']

            SaveInventory = """
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/inventory/soap" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <soap:SaveInventory>
                        <Request>
                        <Inventories>
                        </Inventories>
                        <Credential>
                        <ChannelManagerUsername>vkirirom</ChannelManagerUsername>
                        <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword>
                        <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId>
                        <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey>
                        </Credential>
                        <Language>en</Language>
                    </Request>
                  </soap:SaveInventory>
               </soapenv:Body>
            </soapenv:Envelope>
            """
            element_saveInventory = ET.fromstring(SaveInventory)
            inventory = """
                <Inventory>
                    <RoomId></RoomId>
                    <Availabilities>
                    </Availabilities>
                </Inventory>
                """
            room_qty = """
                <Availability>
                    <DateRange>
                        <From></From>
                        <To></To>
                    </DateRange>
                    <Quantity></Quantity>
                    <Action>Set</Action>
                </Availability>
                """

            for lines in self.reservation_line:
                for room in lines.reserve:
                    pre_room_ids.append(room.id)

            #check_draft = self.state
            res = super(save_booking, self).write(vals)

            ###### define new_room_ids and compare with pre_room_ids then delete or add hotel_room_line_reservation
            for line in self.reservation_line:
                for room in line.reserve:
                    new_room_ids.append(room.id)

            for i in new_room_ids:
                if i not in pre_room_ids:
                    addId.append(i)
            for i in pre_room_ids:
                if i not in new_room_ids:
                    deleteId.append(i)

            line_ids = room_reservation_line_obj.search(
                [('reservation_id.id', '=', self.id)])
            for line in line_ids:
                if line.room_id.id in deleteId:
                    line.unlink()

            availability_delete = dict()
            type_dict = dict()

            for id in deleteId:
                r = hotel_room_obj.browse([id])
                if r.room_type_id in type_dict:
                    continue
                else:
                    type_dict.update({r.room_type_id: 0})
            for type in type_dict:
                checkin = parse(self.checkin).date()
                checkout = parse(self.checkout).date()
                date_qty = dict()
                while True:
                    date_qty.update({checkin.isoformat(): 0})
                    room_ids = hotel_room_obj.search([('room_type_id', '=', type)])
                    for r in room_ids:
                        available = 1
                        for line in r.room_reservation_line_ids:
                            if ((checkin >= parse(line.check_in).date() and checkin < parse(
                                    line.check_out).date()) and line.status != "cancel"):
                                available = 0
                                break
                            else:
                                available = 1

                        if available == 1:
                            date_qty[checkin.isoformat()] = date_qty[checkin.isoformat()] + 1

                    checkin = checkin + datetime.timedelta(days=1)
                    availability_delete.update({type: date_qty})
                    if checkin == checkout:
                        break
            for room_id in availability_delete:
                r = 0
                if room_id =="a5190207-c2a4-47a0-af40-a1c027beeee7":
                    r = 1
                # if room_id == "8ceca99d-f593-400e-af47-ae56ba56aff6" or room_id == "52292b22-259f-4257-ba1d-2f901502481c" or room_id == "91e8533d-6901-4984-bd96-c146b0beff67" or room_id == "a5190207-c2a4-47a0-af40-a1c027beeee7":
                    
                # elif room_id == "6781f3c9-93d2-1502181553-4450-9cae-41f26162d513" or room_id == "6ea0fe92-e3f0-464c-bf4a-03c799cd475c":
                #     r = 2
                # elif room_id == "bd697e6c-912f-4a72-af73-c3a754da8677":
                #     r = 4
                # elif room_id == "9ce49877-f934-409f-9711-0a2806c89de4" or room_id =="2a224d81-c2a5-4b7a-91ab-d04a0e5a68b3":
                #     r = 0

                inventory_element = ET.fromstring(inventory)
                for i in inventory_element.getiterator('RoomId'):
                    i.text = room_id
                for i in inventory_element.getiterator('Availabilities'):
                    for date in availability_delete[room_id]:
                        element = ET.fromstring(room_qty)
                        for data in element.getiterator('From'):
                            data.text = date
                        for data in element.getiterator('To'):
                            data.text = date
                        for data in element.getiterator('Quantity'):
                            if (availability_delete[room_id][date]-r) < 0:
                                data.text = str(0)
                            else:
                                data.text = str(availability_delete[room_id][date]-r)
                        i.append(element)

                for Inventories in element_saveInventory.getiterator('Inventories'):
                    Inventories.append(inventory_element)

            delete_inventory_body = ET.tostring(element_saveInventory, encoding='utf8', method='xml')
            exception=False
            headers = {"Content-Type": "application/xml"}

            if len(availability_delete):
                try:
                    response = requests.post("https://api.hotellinksolutions.com/services/inventory/soap",
                                         data=delete_inventory_body,headers=headers)
                # except requests.exceptions.ConnectTimeout:
                #     exception=True
                #     raise except_orm(_('Connection Timeout'), _('Please Try again later'))

                except requests.exceptions.ConnectionError:
                    exception = True
                    raise except_orm(_('No Internet Connection'), _('Please Try again later'))
            if not exception:
                for r in addId:
                    vals = {
                        'room_id': r,
                        'reservation_id': self.id,
                        'check_in': self.checkin,
                        'check_out': self.checkout,
                        'state': 'assigned',
                    }
                    hotel_room_obj.browse([r]).write({'isroom': False, 'status': 'occupied'})
                    room_reservation_line_obj.create(vals)
            ######################################################################################################
                #if self.state == "confirm" and not check_draft == "draft":
                print "=====***********+++++++++++"
                body_req = self.define_notifybooking()
                body_req_element = ET.fromstring(body_req)
                for BookingId in body_req_element.getiterator('BookingId'):
                    BookingId.text = self.booking_id
                for NotificationType in body_req_element.getiterator('NotificationType'):
                    NotificationType.text = "Update"
                write_data = ET.tostring(body_req_element, encoding='utf8', method='xml')

                try:

                    response = requests.post("https://api.hotellinksolutions.com/services/booking/soap",
                                             data=write_data, headers=headers)

                # except requests.exceptions.ConnectTimeout:
                #     raise except_orm(_('Connection Timeout'), _('Please Try again later'))

                except requests.exceptions.ConnectionError:
                    raise except_orm(_('No Internet Connection'), _('Please Try again later'))

                Inventory_Body = self.define_inventory_form()
                try:

                    response = requests.post("https://api.hotellinksolutions.com/services/inventory/soap",
                                             data=Inventory_Body,headers=headers)

                # except requests.exceptions.ConnectTimeout:
                #     raise except_orm(_('Connection Timeout'), _('Please Try again later'))

                except requests.exceptions.ConnectionError:
                    raise except_orm(_('No Internet Connection'), _('Please Try again later'))
        else:
            res = super(save_booking, self).write(vals)
        return res

    @api.multi
    def cancel_reservation(self):
        cancel_con = ["BO", "AG", "BW", "MO"]
        if self.booking_id:
	        if (self.booking_id[0] + self.booking_id[1]) in cancel_con:
	             raise except_orm(_('Warning'), _('You tried to cancel reservation which from OTA partner!'))
	        res = super(save_booking, self).cancel_reservation()

	        cancel_booking_str = """
	            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soap="https://api.hotellinksolutions.com/services/booking/soap" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/">
	                <soapenv:Header/>
	                <soapenv:Body>
	                <soap:NotifyBookings>
	                <Request>
	                <Bookings>
	                    <Booking>
	                    <NotificationType>Cancel</NotificationType>
	                    <BookingId></BookingId>
	                    </Booking>
	                </Bookings>
	                <Credential>
	                <ChannelManagerUsername>vkirirom</ChannelManagerUsername>
	                <ChannelManagerPassword>[y>sGzC6s2J=L#K</ChannelManagerPassword>
	                <HotelId>ea3bbb2b-8b09-45cb-b465-7d4d5c9c6626</HotelId>
	                <HotelAuthenticationChannelKey>6f5328e40b2c729c534a0ccbeacb0abd</HotelAuthenticationChannelKey>
	                </Credential>
	                <Language>en</Language>
	                <Language>en</Language>
	                </Request>
	                </soap:NotifyBookings>
	                </soapenv:Body>
	            </soapenv:Envelope>
	        """
	        cancel_element = ET.fromstring(cancel_booking_str)

	        for Id in cancel_element.getiterator('BookingId'):
	            Id.text = self.booking_id
	        body_req = ET.tostring(cancel_element, encoding='utf8', method='xml')

	        headers = {"Content-Type": "application/xml"}
	        exception = False
	        try:
	            response = requests.post("https://api.hotellinksolutions.com/services/booking/soap",
	                                    data=body_req, headers=headers)
	        # except requests.exceptions.ConnectTimeout:
	        #     exception = True
	        #     raise except_orm(_('Connection Timeout'), _('Please Try again later'))

	        except requests.exceptions.ConnectionError:
	            exception = True
	            raise except_orm(_('Warning'), _('You tried to cancel reservation with No internet connection'))
	        if not exception:
	            Inventory_Body = self.define_inventory_form()
	            response = requests.post("https://api.hotellinksolutions.com/services/inventory/soap",
	                                      data=Inventory_Body, headers=headers)
        	return res
        else:
        	raise except_orm(_('Warning'), _('You can not cancel this reservation Please delete it.'))


class HotelRoomType(models.Model):
    _inherit = 'product.category'
    rate_plan_line = fields.One2many('room_type.rate_plan', 'hotel_room_type_id', 'Lines')
    room_type_id = fields.Char('Room TypeID')


class RatePlant(models.Model):
    _name = 'room_type.rate_plan'
    name = fields.Char('Name', select=True, required=True)
    rate_plan_id = fields.Char('Id', required=True)
    hotel_room_type_id = fields.Many2one('product.category')


class HotelRoom(models.Model):
    _inherit = 'hotel.room'
    room_type_id = fields.Char('Type ID', related='categ_id.room_type_id')

