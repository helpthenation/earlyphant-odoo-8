from openerp.osv import osv
from openerp.report import report_sxw
import datetime

class payment_details(report_sxw.rml_parse):

    def _get_details(self,form):
        order_line_obj = self.pool.get('kr.purchase.order.line')
        ids = order_line_obj.search(self.cr,self.uid,['&',('date_order','>=',form['date_start'] + \
                                                           ' 00:00:00'),('date_order','<=',form['date_end'] + \
                                                                         ' 23:59:59')])
        data = dict()
        for id in ids:
            line = order_line_obj.browse(self.cr,self.uid,[id])
            if line.date_order not in data:
                subtotal = line.sub_total
                data.update({line.date_order:{'amount':{line.supplier_id.name:subtotal},
                                              'analytic_acc':{line.analytic_acc.name:subtotal}}})
            else:
                subtotal = line.sub_total
                if line.supplier_id.name not in data[line.date_order]['amount']:
                    data[line.date_order]['amount'].update({line.supplier_id.name:subtotal})
                else:
                    data[line.date_order]['amount'][line.supplier_id.name]+=subtotal
                if line.analytic_acc.name not in data[line.date_order]['analytic_acc']:
                    data[line.date_order]['analytic_acc'].update({line.analytic_acc.name:subtotal})
                else:
                    data[line.date_order]['analytic_acc'][line.analytic_acc.name]+=subtotal
        return data

    def _get_supplier_payment_details(self,form):

        order_line_obj = self.pool.get('kr.purchase.order.line')
        ids = order_line_obj.search(self.cr, self.uid, ['&', ('date_order', '>=', form['date_start'] +' 00:00:00'),
                                                        ('date_order', '<=', form['date_end'] +' 23:59:59'),
                                                        ('supplier_id','=',form['supplier_id'][0])
                                                        ])
        data = dict()
        for id in ids:
            line = order_line_obj.browse(self.cr, self.uid, [id])
            if line.date_order not in data:
                data.update({line.date_order:
                    {line.invoice_number:[line.sub_total,line.order_id.name]}
                })
            else:
                if line.invoice_number in data[line.date_order]:
                    data[line.date_order][line.invoice_number][0] += line.sub_total
                else:
                    data[line.date_order].update({line.invoice_number:[line.sub_total,line.order_id.name]})

        for date in data:
            data[date].update({'num_invoice':len(data[date])})

        new_data =dict()
        for date in data:
            sub=0
            for invoice in data[date]:
                if invoice != 'num_invoice':
                    sub += data[date][invoice][0]
            new_data.update({date:[data[date],data[date]['num_invoice'],sub]})
        total = 0
        for date in new_data:
            total += new_data[date][2]
            del new_data[date][0]['num_invoice']
        

        arr=[]
        for key in new_data:
            arr.append(key)

        return new_data,sorted(arr),total


    def _get_supplier_details(self,form):

        supplier=self.pool.get('kirirom.supplier').browse(self.cr,self.uid,[form['supplier_id'][0]])
        return {'name':supplier.name,'tel':supplier.tel}

    def __init__(self, cr, uid, name, context):
        super(payment_details, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_details': self._get_details,
            'get_supplier_payment_details': self._get_supplier_payment_details,
            'get_supplier_details':self._get_supplier_details,
        })
class report_purchase_payment(osv.AbstractModel):
    _name = 'report.market_list.report_purchase_payment'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_purchase_payment'
    _wrapped_report_class = payment_details

class purchase_payment_report(osv.AbstractModel):
    _name = 'report.market_list.report_entry_payment_vuocher_pdf'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_entry_payment_vuocher_pdf'
    _wrapped_report_class = payment_details

class supplier_payment_report(osv.AbstractModel):
    _name = 'report.market_list.supplier_payment_voucher_template'
    _inherit = 'report.abstract_report'
    _template = 'market_list.supplier_payment_voucher_template'
    _wrapped_report_class = payment_details

