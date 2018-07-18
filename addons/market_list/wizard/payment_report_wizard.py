from openerp import models, fields, api
import datetime

class PaymentReport(models.TransientModel):
    _name = 'mk.payment.report.wizard'

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')

    @api.multi
    def print_report(self):
        data = {
            'ids': self.ids,
            'model': 'kr.purchase.order.line',
            'form': self.read(['date_start', 'date_end'])[0]
        }
        return self.env['report'].get_action(self, 'market_list.report_purchase_payment',
                                             data=data)

class SupplierPaymentReport(models.TransientModel):
    _name = 'mk.supplier.payment.report.wizard'

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    supplier_id = fields.Many2one('kirirom.supplier','Supplier')

    @api.multi
    def print_report(self):

        data = {
            'ids': self.ids,
            'model': 'kr.purchase.order.line',
            'form': self.read(['date_start', 'date_end', 'supplier_id'])[0]
        }
        return self.env['report'].get_action(self, 'market_list.supplier_payment_voucher_template',
                                             data=data)


