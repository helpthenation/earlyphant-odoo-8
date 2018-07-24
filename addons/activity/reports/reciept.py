import time
from openerp import models
from openerp.report import report_sxw

class ActivityReceipt(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context):
        super(ActivityReceipt, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_res_data': self.get_res_data,
        })
        self.context = context


class ReportKot(models.AbstractModel):
    _name = 'report.activity.activity_receipt_pdf'
    _inherit = 'report.abstract_report'
    _template = 'activity.activity_receipt_pdf'
    _wrapped_report_class = ActivityReceipt