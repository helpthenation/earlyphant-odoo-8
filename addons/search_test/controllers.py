from openerp import http
from openerp.http import request


class SearchTest(http.Controller):

    # def _get_search_domain(self,search):
    #     domain= ""
    #     if search:
    #         for srch in search.split(" "):
    #             domain += [('name','ilike',srch)]
    #     return domain


    @http.route([
        '/search'
    ], type='http', auth="public", website=True)
    def testing(self,search=''):
        print "============execute"
        return "Hello world"




        # cr, uid, pool=request.cr, request.uid, request.registry
        # domain = self._get_search_domain(search)
        # emp_obj = pool.get('hr.employee')
        # emp_ids = emp_obj.search(cr, uid, domain)
        # employee = emp_obj.browse(cr, uid, emp_ids)
        # values = {
        #     'search':search,
        #     'employee':employee,
        # }
        # return employee

