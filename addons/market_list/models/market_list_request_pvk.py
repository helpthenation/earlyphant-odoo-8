from openerp import models, fields, api, _
import datetime

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('done','Done')
]


class MarketListPVKRequest(models.Model):
    _name = 'marketlist.pvk.request'
    _description = 'Market List Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'market_list.pvk_request_to_approve':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'to_approve',
            'market_list.pvk_request_approved':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'approved',
            'market_list.pvk_request_rejected':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'rejected',
        },
    }

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'date_start': datetime.datetime.today(),
            'requested_by':self.env.uid,
        })
        return super(MarketListPVKRequest, self).copy(default)

    @api.model
    def _get_default_create_date(self):
        return datetime.datetime.today()
    @api.model
    def _get_default_requested_by(self):
        print "********"
        print self.env.uid
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('pvk.request.sequence')
        if vals.get('approve_by'):
            assigned_to = self.env['res.users'].browse(vals.get('approve_by'))
            vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        return super(MarketListPVKRequest, self).create(vals)


    @api.multi
    def write(self, vals):
        if vals.get('approve_by'):
            assigned_to = self.env['res.users'].browse(vals.get('approve_by'))
            vals['message_follower_ids'] = [(6, 0, [assigned_to.partner_id.id, self.requested_by.partner_id.id])]
        if 'state' in vals:
            if vals['state'] == 'approved':
                if self.purchaser:
                    vals['message_follower_ids'] = [(4, self.purchaser.partner_id.id)]
        return super(MarketListPVKRequest, self).write(vals)

    @api.multi
    def _compute_amount_total_est(self):
        subtotal = 0
        for line in self.veg_herb_line_ids:
            subtotal += line.total_price_est
        self.amount_total_est = subtotal

    @api.multi
    def button_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def button_to_approve(self):
        self.state = 'to_approve'
        return True

    @api.multi
    def button_approved(self):
        self.state = 'approved'
        self.approve_date = datetime.datetime.today()
        return True
    @api.multi
    def button_generate_po(self):
        self.state = 'done'

        purchase_obj = self.env['kr.purchase.order']
        order_line = []
        analytic_account_id = self.analytic_account_id.id
        date_order = datetime.datetime.today()

        for line in self.veg_herb_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit':line.price_per_unit_est}

            order_line.append(product_line)
        for line in self.fruit_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit': line.price_per_unit_est}

            order_line.append(product_line)
        for line in self.poultry_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit': line.price_per_unit_est}

            order_line.append(product_line)

        for line in self.sea_fish_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit': line.price_per_unit_est}

            order_line.append(product_line)
        for line in self.beef_pork_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit': line.price_per_unit_est}

            order_line.append(product_line)
        for line in self.other_line_ids:
            product_line = [0] * 3
            product_line[0] = 0
            product_line[1] = False
            product_line[2] = {'product_id': line.product_id.id,
                               'product_qty': line.product_qty,
                               'analytic_acc':analytic_account_id,
                               'date_order':date_order,
                               'price_per_unit_riel': 0,
                               'product_uom_id': line.product_uom_id.id,
                               'price_per_unit': line.price_per_unit_est}
            order_line.append(product_line)

        vals = {'order_line': order_line,
                'origin': self.name,
                'analytic_account_id': analytic_account_id,
                'date_order': date_order,
                'request_date': self.date_start,
                'is_a2a':False,
                'requested_by':self.requested_by.id,
                'approved_by':self.approve_by.id,
                'approved_date':self.approve_date}
        purchase_obj.create(vals)

        return True

    @api.multi
    def button_rejected(self):
        self.state = 'rejected'
        return True

    @api.onchange('veg_herb_line_ids', 'fruit_line_ids', 'poultry_line_ids', 'sea_fish_line_ids', 'beef_pork_line_ids', 'other_line_ids')
    def onchange_total(self):
        subtotal = 0
        for line in self.veg_herb_line_ids:
            subtotal += line.total_price_est
        for line in self.fruit_line_ids:
            subtotal += line.total_price_est
        for line in self.poultry_line_ids:
            subtotal += line.total_price_est
        for line in self.sea_fish_line_ids:
            subtotal += line.total_price_est
        for line in self.beef_pork_line_ids:
            subtotal += line.total_price_est
        for line in self.other_line_ids:
            subtotal += line.total_price_est
        self.amount_total_est = subtotal

    @api.multi
    def _compute_amount_total_est(self):
        amount_total=0
        for line in self.veg_herb_line_ids:
            amount_total += line.total_price_est

        for line in self.fruit_line_ids:
            amount_total += line.total_price_est

        for line in self.poultry_line_ids:
            amount_total += line.total_price_est

        for line in self.sea_fish_line_ids:
            amount_total += line.total_price_est

        for line in self.beef_pork_line_ids:
            amount_total += line.total_price_est

        for line in self.other_line_ids:
            amount_total += line.total_price_est

        self.amount_total_est = amount_total

    # def _needaction_domain_get(self, cr, uid, context=None):
    #     emp_obj = self.pool.get('res.users').browse(cr, uid, [uid], context=context)
    #     arr = []
    #     for obj in emp_obj.groups_id:
    #         arr.append(obj.id)
    #     if 93 in arr:
    #         return False
    #     elif 92 in arr:
    #         return [('state', '=', 'approved')]
    #     elif 86 in arr:
    #         return ['&', ('state', '=', 'to_approve'), ('approve_by', '=', emp_obj.id)]
    #     elif 85 in arr:
    #         return ['&', ('state', '=', 'rejected'), ('request_by', '=', emp_obj.id)]
    #     else:
    #         return False


    name = fields.Char('Request Reference', size=32,
                       track_visibility='onchange',readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', track_visibility='onchange',
                                          required=True,
                                          readonly=False,
                                          states={'approved': [('readonly', True)],
                                                  'done': [('readonly', True)]}
                                          )
    approve_date = fields.Datetime('Approved Date', readonly=True)
    approve_by = fields.Many2one('res.users',
                                   'Approver',
                                   track_visibility='onchange',
                                   readonly=False,
                                   required=True,
                                   domain=[('groups_id.name', '=', 'Request Manager')])

    date_start = fields.Datetime('Creation date',
                             help="Date when the user initiated the "
                                  "request.",
                                 readonly=True,
                                 )

    requested_by = fields.Many2one('res.users',
                                   'Requester',
                                   required=True,
                                   track_visibility='onchange',
                                   readonly=True)
    purchaser = fields.Many2one('res.users', 'Purchaser', 
    	domain=[('groups_id.name', '=', 'Purchaser')],required=True)
    description = fields.Text('Description')



    # --------------- Product ---------------
    veg_herb_line_ids = fields.One2many('marketlist.request.vegetableandherb.line', 'request_id',
                               'Vegetable & Herb',
                                        readonly=False,
                                        states={'approved': [('readonly', True)],
                                                'done': [('readonly', True)]},
                                        copy=True
                                        )
    fruit_line_ids = fields.One2many('marketlist.request.fruit.line', 'request_id',
                                    'Fruit',
                                     readonly=False,
                                     states={'approved': [('readonly', True)],
                                             'done': [('readonly', True)]},
                                     copy=True
                                     )
    poultry_line_ids = fields.One2many('marketlist.request.poultry.line', 'request_id',
                                    'Poultry',
                                       readonly=False,
                                       states={'approved': [('readonly', True)],
                                               'done': [('readonly', True)]},
                                               copy=True
                                       )
    sea_fish_line_ids = fields.One2many('marketlist.request.seafoodandfish.line', 'request_id',
                               'Seefood & Fish',
                                        readonly=False,
                                        states={'approved': [('readonly', True)],
                                                'done': [('readonly', True)]},
                                                copy=True
                                        )
    beef_pork_line_ids = fields.One2many('marketlist.request.beefandpork.line', 'request_id',
                                    'Beef & Pork',
                                         readonly=False,
                                         states={'approved': [('readonly', True)],
                                                 'done': [('readonly', True)]},
                                                 copy=True
                                         )
    other_line_ids = fields.One2many('marketlist.request.other.line', 'request_id',
                                    'Other',
                                     readonly=False,
                                     states={'approved': [('readonly', True)],
                                             'done': [('readonly', True)]},
                                             copy=True
                                     )

    # --------------- Total Amount Calculation 1 Est & Act ---------------
    amount_total_est = fields.Float(string='Estimated Total Price',
                                    readonly=True,
                                    compute='_compute_amount_total_est')

    state = fields.Selection(selection=_STATES,
                             string='Status',
                             track_visibility='onchange',
                             required=True,
                             default='draft')
    _defaults = {
        'requested_by':_get_default_requested_by,
        'description':' ',
        'date_start':_get_default_create_date
    }




