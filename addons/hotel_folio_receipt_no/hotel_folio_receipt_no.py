import datetime
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HotelReceiptNo(models.Model):
    _inherit = 'hotel.folio'

    receipt_no = fields.Char("Receipt No",readonly=True,states={'draft': [('readonly', False)]})
    ref_booking = fields.Char('Ref Booking')

    @api.multi
    def action_wait(self):
        '''
        @param self: object pointer
        '''
        sale_order_obj = self.env['sale.order']
        for o in self:
            sale_obj = sale_order_obj.browse([o.order_id.id])
            sale_obj.write({'receipt_no': o.receipt_no,'fol_no_so': o.name,
                            'checkin': o.checkin_date,
                            'checkout': o.checkout_date})
        res=super(HotelReceiptNo,self).action_wait()
        return res


class HotelReceiptNoInInvoice(models.Model):
    _inherit = 'account.invoice'
    receipt_no = fields.Char("Receipt No")
    fol_no_inv = fields.Char("Folio No")
    checkin = fields.Datetime('Checkin Date')
    checkout = fields.Datetime('Checkout Date')


class HotelReceiptNoInSale(models.Model):
    _inherit = 'sale.order'
    receipt_no = fields.Char("Receipt No")
    fol_no_so = fields.Char("Folio No")
    checkin = fields.Datetime('Checkin Date')
    checkout = fields.Datetime('Checkout Date')

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice=False, context=None):

        sale_order_obj = self.browse(cr, uid, ids, context=context)
        invoice = self.pool.get('account.invoice')
        res = super(HotelReceiptNoInSale,self).action_invoice_create(cr, uid, ids,context=context)
        invoice.write(cr, uid, [res], {'receipt_no': sale_order_obj.receipt_no,'fol_no_inv': sale_order_obj.fol_no_so,
                                       'checkin': sale_order_obj.checkin,
                                       'checkout': sale_order_obj.checkout})
        return res
#Hotel Reservation Summary
class RoomReservationSummary(models.Model):
    _inherit = 'room.reservation.summary'

    room_type_summary = fields.Many2one('product.category', string="Room type", domain=[('parent_id', '=', 'vK Services / Accommodation')])

class ReferenceBooking(models.Model):
    _inherit = 'hotel.reservation'

    ref_booking = fields.Char('Ref Booking')
    booking_by = fields.Many2one('res.users','Reference Booking By',required=False, readonly=True,states={'draft': [('readonly', False)]})

    _defaults = {
        'booking_by': lambda obj, cr, uid, context: uid,
    }

    @api.multi
    def _create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        hotel_folio_obj = self.env['hotel.folio']
        res = super(ReferenceBooking, self)._create_folio()
        folio_ids=hotel_folio_obj.search([('reservation_id','=',self.reservation_no)])
        folio_ids.write({'ref_booking':self.ref_booking})

        return res


class HotelWizard(models.TransientModel):
    _inherit = 'folio.report.wizard'
    report_date = fields.Datetime('Report Date')


class ServiceLine(models.Model):
    _inherit = 'hotel.service.line'
    line_payment = fields.Selection([('cash', 'Cash'),
                                     ('credit_card', 'Credit Card'),
                                     ('cityledger', 'City Ledger'),
                                     ('foc','FOC')],
                                    'Payment Method', default='cityledger')


class FolioLine(models.Model):
    _inherit = 'hotel.folio.line'
    line_payment = fields.Selection([('cash', 'Cash'),
                                     ('credit_card', 'Credit Card'),
                                     ('cityledger', 'City Ledger'),
                                     ('foc','FOC')],
                                    'Payment Method', default='cityledger')