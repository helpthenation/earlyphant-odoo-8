import time
from openerp import models
from openerp.report import report_sxw

class PurchaseRequestReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PurchaseRequestReport, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_res_data': self.get_res_data,
        })
        self.context = context

class PurchaseRequestMarketListReportKot(models.AbstractModel):
    _name = 'report.market_list.purchase_request_marketlist_pdf'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_marketlist_purchase_request_pdf'
    _wrapped_report_class = PurchaseRequestReport


class PurchaseRequestGeneralReportKot(models.AbstractModel):
    _name = 'report.market_list.purchase_request_general_pdf'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_general_purchase_request_pdf'
    _wrapped_report_class = PurchaseRequestReport

class PurchaseRequestGeneralA2AReportKot(models.AbstractModel):
    _name = 'report.market_list.purchase_request_general_a2a_pdf'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_general_purchase_request_a2a_pdf'
    _wrapped_report_class = PurchaseRequestReport


class PurchaseRequestPVKReportKot(models.AbstractModel):
    _name = 'report.market_list.purchase_request_pvk_pdf'
    _inherit = 'report.abstract_report'
    _template = 'market_list.report_pvk_purchase_request_pdf'
    _wrapped_report_class = PurchaseRequestReport
