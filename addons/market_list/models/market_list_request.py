from openerp import models, fields, api, _
import datetime

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('done','Done')
]

class MarketListRequest(models.Model):
    _name = 'marketlist.request'
    _description = 'Market List Request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'market_list.ml_request_to_approve':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'to_approve',
            'market_list.ml_request_approved':
                lambda self, cr, uid, obj,
                ctx=None: obj.state == 'approved',
            'market_list.ml_request_rejected':
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
        return super(MarketListRequest, self).copy(default)

    @api.model
    def _get_default_create_date(self):
        return datetime.datetime.today()

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ml.request.sequence')
        if vals.get('approve_by'):
            assigned_to = self.env['res.users'].browse(vals.get('approve_by'))
            vals['message_follower_ids'] = [(4, assigned_to.partner_id.id)]
        return super(MarketListRequest, self).create(vals)


    @api.multi
    def write(self, vals):
        if vals.get('approve_by'):
            assigned_to = self.env['res.users'].browse(vals.get('approve_by'))
            vals['message_follower_ids'] = [(6, 0, [assigned_to.partner_id.id, self.requested_by.partner_id.id])]
        if 'state' in vals:
            if vals['state'] == 'approved':
                if self.purchaser:
                    vals['message_follower_ids'] = [(4, self.purchaser.partner_id.id)]
        return super(MarketListRequest, self).write(vals)

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
        date_order = datetime.datetime.today()
        analytic_account_id = self.analytic_account_id.id
        order_line = []
        for line in self.line_ids_day1_breakfast:
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
        for line in self.line_ids_day1_lunch:
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
        for line in self.line_ids_day1_dinner:
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
        for line in self.dry_store_line_day1:
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
        for line in self.line_ids_day2_breakfast:
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
        for line in self.line_ids_day2_lunch:
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
        for line in self.line_ids_day2_dinner:
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
        for line in self.dry_store_line_day2:
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

        new_array = []
        for i in order_line:
            if len(new_array) == 0:
                new_array.append(i)
            else:
                is_append = 1
                for j in new_array:
                    if i[2]['product_id'] == j[2]['product_id']:
                        is_append = 0
                        j[2]['product_qty'] += i[2]['product_qty']

                if is_append == 0:
                    continue
                else:
                    new_array.append(i)
        purchase_obj = self.env['kr.purchase.order']

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

    @api.onchange('line_ids_day1_breakfast')
    def onchange_total_day1_breakfast(self):
        subtotal = 0
        for line in self.line_ids_day1_breakfast:
            subtotal += line.total_price_est
        self.amount_total_est_breakfast_day1 = subtotal

    @api.onchange('line_ids_day1_lunch')
    def onchange_total_day1_lunch(self):
        subtotal = 0
        for line in self.line_ids_day1_lunch:
            subtotal += line.total_price_est
        self.amount_total_est_lunch_day1 = subtotal

    @api.onchange('line_ids_day1_dinner')
    def onchange_total_day1_dinner(self):
        subtotal = 0
        for line in self.line_ids_day1_dinner:
            subtotal += line.total_price_est
        self.amount_total_est_dinner_day1 = subtotal

    @api.onchange('dry_store_line_day1')
    def onchange_total_drystore_day1(self):
        subtotal = 0
        for line in self.dry_store_line_day1:
            subtotal += line.total_price_est
        self.amount_total_est_dry_store_day1 = subtotal

    @api.onchange('line_ids_day2_breakfast')
    def onchange_total_day2_breakfast(self):
        subtotal = 0
        for line in self.line_ids_day2_breakfast:
            subtotal += line.total_price_est
        self.amount_total_est_breakfast_day2 = subtotal

    @api.onchange('line_ids_day2_lunch')
    def onchange_total_day2_lunch(self):
        subtotal = 0
        for line in self.line_ids_day2_lunch:
            subtotal += line.total_price_est
        self.amount_total_est_lunch_day2 = subtotal

    @api.onchange('line_ids_day2_dinner')
    def onchange_total_day2_dinner(self):
        subtotal = 0
        for line in self.line_ids_day2_dinner:
            subtotal += line.total_price_est
        self.amount_total_est_dinner_day2 = subtotal

    @api.onchange('dry_store_line_day2')
    def onchange_total_drystore_day2(self):
        subtotal = 0
        for line in self.dry_store_line_day2:
            subtotal += line.total_price_est
        self.amount_total_est_dry_store_day2 = subtotal

    @api.onchange('breakfast_est_day1', 'lunch_est_day1', 'dinner_est_day1')
    def onchange_person_day1(self):
        self.total_est_day1 = self.breakfast_est_day1 + self.lunch_est_day1 + self.dinner_est_day1

    @api.onchange('breakfast_est_day2', 'lunch_est_day2', 'dinner_est_day2')
    def onchange_person_day2(self):
        self.total_est_day2 = self.breakfast_est_day2 + self.lunch_est_day2 + self.dinner_est_day2

    @api.onchange('amount_total_est_breakfast_day1', 'amount_total_est_lunch_day1',
                  'amount_total_est_dinner_day1', 'amount_total_est_dry_store_day1')
    def onchange_total_day1(self):
        self.grand_total_est_day1 = \
            self.amount_total_est_breakfast_day1 + \
            self.amount_total_est_lunch_day1 + \
            self.amount_total_est_dinner_day1 + \
            self.amount_total_est_dry_store_day1

    @api.onchange('amount_total_est_breakfast_day2', 'amount_total_est_lunch_day2',
                  'amount_total_est_dinner_day2', 'amount_total_est_dry_store_day2')
    def onchange_total_day2(self):
        self.grand_total_est_day2 = \
            self.amount_total_est_breakfast_day2 + \
            self.amount_total_est_lunch_day2 + \
            self.amount_total_est_dinner_day2 + \
            self.amount_total_est_dry_store_day2


    @api.onchange('grand_total_est_day1', 'total_est_day1')
    def onchange_budget_per_pax_day1(self):
        if self.total_est_day1 != 0:
            self.budget_per_pax_day1 = self.grand_total_est_day1 * 3 / self.total_est_day1

    @api.onchange('grand_total_est_day2', 'total_est_day2')
    def onchange_budget_per_pax_day2(self):
        if self.total_est_day2 !=0:
            self.budget_per_pax_day2 = self.grand_total_est_day2 * 3 / self.total_est_day2



    ########### compute function #######################
    @api.multi
    def _compute_amount_total_est_breakfast_day1(self):
        subtotal = 0
        for line in self.line_ids_day1_breakfast:
            subtotal += line.total_price_est

        self.amount_total_est_breakfast_day1 = subtotal

    @api.multi
    def _compute_amount_total_est_lunch_day1(self):
        subtotal = 0
        for line in self.line_ids_day1_lunch:
            subtotal += line.total_price_est

        self.amount_total_est_lunch_day1 = subtotal

    @api.multi
    def _compute_amount_total_est_dinner_day1(self):
        subtotal = 0
        for line in self.line_ids_day1_dinner:
            subtotal += line.total_price_est

        self.amount_total_est_dinner_day1 = subtotal

    @api.multi
    def _compute_amount_total_est_dry_store_day1(self):
        subtotal = 0
        for line in self.dry_store_line_day1:
            subtotal += line.total_price_est

        self.amount_total_est_dry_store_day1 = subtotal

    @api.multi
    def _compute_amount_total_est_breakfast_day2(self):
        subtotal = 0
        for line in self.line_ids_day2_breakfast:
            subtotal += line.total_price_est

        self.amount_total_est_breakfast_day2 = subtotal

    @api.multi
    def _compute_amount_total_est_lunch_day2(self):
        subtotal = 0
        for line in self.line_ids_day2_lunch:
            subtotal += line.total_price_est

        self.amount_total_est_lunch_day2 = subtotal

    @api.multi
    def _compute_amount_total_est_dinner_day2(self):
        subtotal = 0
        for line in self.line_ids_day2_dinner:
            subtotal += line.total_price_est

        self.amount_total_est_dinner_day2 = subtotal

    @api.multi
    def _compute_amount_total_est_dry_store_day2(self):
        subtotal = 0
        for line in self.dry_store_line_day2:
            subtotal += line.total_price_est
        self.amount_total_est_dry_store_day2 = subtotal


    @api.multi
    def _compute_grand_total_est_day1(self):
        self.grand_total_est_day1 = \
            self.amount_total_est_breakfast_day1+self.amount_total_est_lunch_day1 + self.amount_total_est_dinner_day1 \
            + self.amount_total_est_dry_store_day1
    @api.multi
    def _compute_grand_total_est_day2(self):
        self.grand_total_est_day2 = \
            self.amount_total_est_breakfast_day2+self.amount_total_est_lunch_day2 + self.amount_total_est_dinner_day2 \
            + self.amount_total_est_dry_store_day2
    @api.multi
    def _compute_total_est_day1(self):
        self.total_est_day1=self.breakfast_est_day1 + self.lunch_est_day1 + self.dinner_est_day1

    @api.multi
    def _compute_total_est_day2(self):
        self.total_est_day2 = self.breakfast_est_day2 + self.lunch_est_day2 + self.dinner_est_day2

    @api.multi
    def _compute_budget_per_pax_day1(self):
    	if self.total_est_day1 != 0:
        	self.budget_per_pax_day1=self.grand_total_est_day1 *3 / self.total_est_day1
        else:
        	return 0
    @api.multi
    def _compute_budget_per_pax_day2(self):
    	if self.total_est_day2 !=0:
        	self.budget_per_pax_day2 = self.grand_total_est_day2 * 3 / self.total_est_day2
        else:
        	return 0

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


    name = fields.Char('Request Reference',
                       size=32,
                       track_visibility='onchange',
                       readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          track_visibility='onchange',
                                          required=True,
                                          readonly=False,
                                          states = {'approved':[('readonly',True)],
                                                    'done':[('readonly',True)]}
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
                             readonly=True)
    requested_by = fields.Many2one('res.users',
                                   'Requester',
                                   required=True,
                                   track_visibility='onchange',
                                   readonly=True)
    purchaser = fields.Many2one('res.users', 'Purchaser', domain=[('groups_id.name', '=', 'Purchaser')],required=True)
    description = fields.Text('Description')
    # --------------- Person - Day 1 ---------------
    breakfast_est_day1 = fields.Integer('Breakfast Estimation (pax)',
                                        readonly=False,
                                        states={'approved': [('readonly', True)],
                                                'done': [('readonly', True)]})
    lunch_est_day1 = fields.Integer('Lunch Estimation (pax)',
                                    readonly=False,
                                    states={'approved': [('readonly', True)],
                                            'done': [('readonly', True)]}
                                    )
    dinner_est_day1 = fields.Integer('Dinner Estimation (pax)',
                                     readonly=False,
                                     states={'approved': [('readonly', True)],
                                             'done': [('readonly', True)]}
                                     )
    total_est_day1 = fields.Integer('Total Estimation (pax)',
                                    readonly=False,
                                    states={'approved': [('readonly', True)],
                                            'done': [('readonly', True)]},
                                    compute='_compute_total_est_day1',
                                    )

    # --------------- Person - Day 2 ---------------
    breakfast_est_day2 = fields.Integer('Breakfast Estimation (pax)',
                                        readonly=False,
                                        states={'approved': [('readonly', True)],
                                                'done': [('readonly', True)]},

                                        )
    lunch_est_day2 = fields.Integer('Lunch Estimation (pax)',
                                    readonly=False,
                                    states={'approved': [('readonly', True)],
                                            'done': [('readonly', True)]},
                                    )
    dinner_est_day2 = fields.Integer('Dinner Estimation (pax)',
                                     readonly=False,
                                     states={'approved': [('readonly', True)],
                                             'done': [('readonly', True)]}
                                     )
    total_est_day2 = fields.Integer('Total Estimation (pax)',
                                    readonly=False,
                                    states={'approved': [('readonly', True)],
                                            'done': [('readonly', True)]},
                                    compute='_compute_total_est_day2'
                                    )

    # --------------- Purchase For Date ---------------
    purchase_for_date_day1 = fields.Date('Purchase for date',required=True,
                                         readonly=False,
                                         states={'approved': [('readonly', True)],
                                                 'done': [('readonly', True)]}
                                         )
    purchase_for_date_day2 = fields.Date('Purchase for date',required=True,
                                         readonly=False,
                                         states={'approved': [('readonly', True)],
                                                 'done': [('readonly', True)]}
                                         )


    # --------------- Product - Day 1 ---------------
    line_ids_day1_breakfast = fields.One2many('marketlist.request.breakfast.day1.line', 'request_id',
                               'Breakfast - Day1',readonly=False,states={'approved': [('readonly', True)],
                                                                         'done':[('readonly',True)]},copy=True)
    line_ids_day1_lunch = fields.One2many('marketlist.request.lunch.day1.line', 'request_id',
                                    'Lunch - Day1',readonly=False,
                                          states={'approved': [('readonly', True)],
                                                  'done': [('readonly', True)]},copy=True)
    line_ids_day1_dinner = fields.One2many('marketlist.request.dinner.day1.line', 'request_id',
                                    'Dinner - Day1',readonly=False,
                                           states={'approved': [('readonly', True)],
                                                   'done': [('readonly', True)]},copy=True)
    dry_store_line_day1 = fields.One2many('marketlist.request.drystore.day1.line', 'request_id',
                                          'Dry Store - Day1',readonly=False,
                                          states={'approved': [('readonly', True)],
                                                  'done': [('readonly', True)]},copy=True)

    # --------------- Product - Day 2 ---------------
    line_ids_day2_breakfast = fields.One2many('marketlist.request.breakfast.day2.line', 'request_id',
                               'Breakfast - Day2',readonly=False,
                                              states={'approved': [('readonly', True)],
                                                      'done': [('readonly', True)]},copy=True)
    line_ids_day2_lunch = fields.One2many('marketlist.request.lunch.day2.line', 'request_id',
                                    'Lunch - Day2',readonly=False,
                                          states={'approved': [('readonly', True)],
                                                  'done': [('readonly', True)]},copy=True)
    line_ids_day2_dinner = fields.One2many('marketlist.request.dinner.day2.line', 'request_id',
                                    'Dinner - Day2',readonly=False,
                                           states={'approved': [('readonly', True)],
                                                   'done': [('readonly', True)]},copy=True)
    dry_store_line_day2 = fields.One2many('marketlist.request.drystore.day2.line', 'request_id',
                                     'Dry Store - Day2',readonly=False,
                                          states={'approved': [('readonly', True)],
                                                  'done': [('readonly', True)]},copy=True)


    # --------------- Amount Calculation Day 1 Est & Act ---------------
    amount_total_est_breakfast_day1 = fields.Float(string='Exp. Subtotal',
                                    readonly=True,compute='_compute_amount_total_est_breakfast_day1')
    amount_total_est_lunch_day1 = fields.Float(string='Exp. Subtotal',
                                    readonly=True,compute='_compute_amount_total_est_lunch_day1')
    amount_total_est_dinner_day1 = fields.Float(string='Exp. Subtotal',
                                    readonly=True,compute='_compute_amount_total_est_dinner_day1')
    amount_total_est_dry_store_day1 = fields.Float(string='Exp. Subtotal',
                                                   readonly=True,
                                                   compute='_compute_amount_total_est_dry_store_day1')
    # --------------- Amount Calculation Day 2 Est & Act ---------------
    amount_total_est_breakfast_day2 = fields.Float(string='Exp. Subtotal',
                                              readonly=True,
                                                   compute='_compute_amount_total_est_breakfast_day2')
    amount_total_est_lunch_day2 = fields.Float(string='Exp. Subtotal',
                                          readonly=True,
                                               compute='_compute_amount_total_est_lunch_day2')
    amount_total_est_dinner_day2 = fields.Float(string='Exp. Subtotal',
                                           readonly=True,
                                                compute='_compute_amount_total_est_dinner_day2')
    amount_total_est_dry_store_day2 = fields.Float(string='Exp. Subtotal',
                                                readonly=True,
                                                   compute='_compute_amount_total_est_dry_store_day2')

    grand_total_est_day2 = fields.Float(string='Exp. Grand Total',
                                        readonly=True,
                                        compute='_compute_grand_total_est_day2')
    grand_total_est_day1 = fields.Float(string='Exp. Grand Total',
                                        readonly=True,
                                        compute='_compute_grand_total_est_day1')
    budget_per_pax_day1 = fields.Float(string='Budget/Pax',
                                    readonly=True,
                                    compute='_compute_budget_per_pax_day1')
    budget_per_pax_day2 = fields.Float(string='Budget/Pax',
                                       readonly=True,
                                       compute='_compute_budget_per_pax_day2')


    # --------------- Menu Day 1  ---------------
    breakfast_day1 = fields.Text('Breakfast Menu',readonly=False,
                                 states={'approved': [('readonly', True)],
                                         'done': [('readonly', True)]})
    lunch_day1 = fields.Text('Lunch Menu',readonly=False,
                             states={'approved': [('readonly', True)],
                                     'done': [('readonly', True)]})
    dinner_day1 = fields.Text('Dinner Menu',readonly=False,
                              states={'approved': [('readonly', True)],
                                      'done': [('readonly', True)]})

    # --------------- Menu Day 1 ---------------
    breakfast_day2 = fields.Text('Breakfast Menu',readonly=False,
                                 states={'approved': [('readonly', True)],
                                         'done': [('readonly', True)]})
    lunch_day2 = fields.Text('Lunch Menu',readonly=False,
                             states={'approved': [('readonly', True)],
                                     'done': [('readonly', True)]})
    dinner_day2 = fields.Text('Dinner Menu',readonly=False,
                              states={'approved': [('readonly', True)],
                                      'done': [('readonly', True)]})
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

