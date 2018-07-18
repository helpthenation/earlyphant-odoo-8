from openerp import models, fields, api, _
import datetime
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp

_STATES = [
    ('draft', 'Draft'),
    ('progress', 'Progress'),
    ('validate', 'Validated'),
    ('done', 'Done'),
]


class MarketListPurchaseOrder(models.Model):
    _name = 'kr.purchase.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _track = {
        'state': {
            'market_list.po_request_to_validate':
                lambda self, cr, uid, obj,
                       ctx=None: obj.state == 'progress',
            'market_list.po_done':
                lambda self, cr, uid, obj,
                       ctx=None: obj.state == 'done',
        },
    }

    @api.multi
    def button_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def button_to_progress(self):
        self.state = 'progress'
        if self.picking.id == False:
            self.button_receiver_product()
        return True

    @api.multi
    def button_validate(self):
        self.state = 'validate'
        return True

    @api.multi
    def button_to_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def button_receiver_product(self):
        if 'VKGR' in self.origin or 'A2AGR' in self.origin:
            picking_obj = self.env['stock.picking']
            move_lines = []
            for line in self.order_line:
                if line.product_id.type == 'product':
                    product_line = [0] * 3
                    product_line[0] = 0
                    product_line[1] = False
                    product_line[2] = {'product_id': line.product_id.id,
                                       'product_uom_qty': line.product_qty,
                                       'date':self.date_order,
                                       'date_expected':self.date_order,
                                        'state':'assigned',
                                        'name':line.product_id.name,
                                       'product_uom':line.product_id.uom_id.id
                    }
                    move_lines.append(product_line)
            if move_lines != []:
                vals={
                        'origin': self.name,
                        'partner_id': False,
                        'date_done': self.date_order,
                        'move_type': 'direct',
                        'note': "",
                        'source_loc': 8,
                        'state': 'assigned',
                        'move_lines':move_lines
                        }
                if 'VKGR' in self.origin:
                    vals.update({'picking_type_id': 13, 'destination_loc': 25})
                elif 'A2AGR' in self.origin:
                    vals.update({'picking_type_id': 8, 'destination_loc': 19})
                res=picking_obj.create(vals)

                self.picking = res

    @api.model
    def create(self, vals):
        if "A2AGR" in vals['origin']:
            vals['name'] = self.env['ir.sequence'].get('a2apo.sequence')
        else:
            vals['name'] = self.env['ir.sequence'].get('vpo.sequence')

        res = super(MarketListPurchaseOrder, self).create(vals)

        subtotal = 0
        for line in res.order_line:
            line.sub_total = line.product_qty * line.price_per_unit
            subtotal += line.sub_total
        res.amount_total = subtotal
        return res

    @api.multi
    def write(self, vals):
        ############ amendment in PO #####################################
        if self.origin:
            product_obj = self.env['product.product']
            productId_to_delete = []
            lineId_to_delete = []
            description = []

            if 'order_line' in vals:
                for line in vals['order_line']:
                    if line[0] == 2:
                        lineId_to_delete.append(line[1])
                    elif line[0] == 0:
                        description.append(
                            product_obj.browse([line[2]['product_id']]).name +
                            '  Qty:' + str(line[2]['product_qty']) + '  Price:' + str(line[2]['price_per_unit'])
                        )

                for line in self.order_line:
                    if line.id in lineId_to_delete:
                        productId_to_delete.append(line.product_id.id)

            if len(productId_to_delete) or len(description):
                if 'MKLR' in self.origin:
                    market_list_obj = self.env['marketlist.request']
                    ids = market_list_obj.search([('name', '=', self.origin)])
                    if len(productId_to_delete):
                        for line in ids.line_ids_day1_breakfast:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.line_ids_day1_lunch:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.line_ids_day1_dinner:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.dry_store_line_day1:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.line_ids_day2_breakfast:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.line_ids_day2_lunch:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.line_ids_day2_dinner:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.dry_store_line_day2:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                    if len(description):
                        for text in description:
                            ids.description = ids.description + '\n' + text
                if 'PVKR' in self.origin:
                    market_list_obj = self.env['marketlist.pvk.request']
                    ids = market_list_obj.search([('name', '=', self.origin)])

                    if len(productId_to_delete):
                        for line in ids.veg_herb_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.fruit_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.poultry_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.sea_fish_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.beef_pork_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                        for line in ids.other_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'

                    if len(description):
                        for text in description:
                            ids.description = ids.description + '\n' + text
                if 'VKGR' in self.origin:
                    market_list_obj = self.env['marketlist.general.request']
                    ids = market_list_obj.search([('name', '=', self.origin)])
                    if len(productId_to_delete):
                        for line in ids.product_line_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'

                    if len(description):
                        for text in description:
                            ids.description = ids.description + '\n' + text
                if 'A2AGR' in self.origin:
                    market_list_obj = self.env['marketlist.general.a2a.request']
                    ids = market_list_obj.search([('name', '=', self.origin)])
                    if len(productId_to_delete):
                        for line in ids.product_line_a2a_ids:
                            if line.product_id.id in productId_to_delete:
                                line.name = 'Not Available'
                    if len(description):
                        for text in description:
                            ids.description = ids.description + '\n' + text
        ##################################################################
        if 'state' in vals:
            if vals['state'] == 'progress':
                if not self.validate_by:
                    raise except_orm(_('Warning'), _('Please input validate by!'))
                for line in self.order_line:
                    if not line.supplier_id or not line.invoice_number:
                        raise except_orm(_('Warning'), _('Please input all invoice number and supplier'))

            if vals['state'] != 'draft':
                if self.budget_controller:
                    vals['message_follower_ids'] = [(4, self.budget_controller.partner_id.id)]
        if 'validate_by' in vals:
            if 'validate_by' in vals and not self.validate_by:
                validate_by = self.env['res.users'].browse([vals['validate_by']])
                vals['message_follower_ids'] = [(4, validate_by.partner_id.id)]
            else:
                validate_by = self.env['res.users'].browse([vals['validate_by']])
                vals['message_follower_ids'] = [(6, 0, [self.create_uid.partner_id.id, validate_by.partner_id.id])]
        return super(MarketListPurchaseOrder, self).write(vals)

    @api.multi
    def create_move(self):
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        period_ids = period_obj.find(self._cr, self._uid, self.date_order)

        move_vals = {
            'name': '/',
            'date': self.payment_date,
            'ref': self.name,
            'period_id': period_ids[0],
            'journal_id': self.journal_id.id,
        }

        move_id = move_obj.create(self._cr, self._uid, move_vals, context=self._context)

        if 'MKLR' in self.origin:
            vals = {
                'name': self.description,
                'ref': '/',
                'move_id': move_id,
                'account_id': self.debit_acc.id,
                'debit': self.amount_total,
                'credit': 0.0,
                'period_id': period_ids[0],
                'journal_id': self.journal_id.id,
                'analytic_account_id': self.analytic_account_id.id,
                # 'currency_id': company_currency != current_currency and  current_currency or False,
                # 'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': self.payment_date,
            }
            move_line_obj.create(self._cr, self._uid, vals, context=self._context)
        else:
            for line in self.order_line:
                vals = {
                    'name': line.product_id.name,
                    'ref': '/',
                    'move_id': move_id,
                    'account_id': line.debit_acc.id,
                    'debit': line.sub_total,
                    'credit': 0.0,
                    'period_id': period_ids[0],
                    'journal_id': self.journal_id.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    # 'currency_id': company_currency != current_currency and  current_currency or False,
                    # 'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                    'date': self.payment_date,
                }
                move_line_obj.create(self._cr, self._uid, vals, context=self._context)
        move_line_obj.create(self._cr, self._uid, {
            'name': self.description,
            'ref': '/',
            'move_id': move_id,
            'account_id': self.credit_acc.id,
            'credit': self.amount_total,
            'debit': 0.0,
            'period_id': period_ids[0],
            'journal_id': self.journal_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            # 'currency_id': company_currency != current_currency and  current_currency or False,
            # 'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
            # 'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
            'date': self.payment_date,
        }, context=self._context)

        self.write({'state': 'done', 'entry_ref': move_id})
        # res = move_obj.browse(self._cr, self._uid, [move_id]).button_validate()

        return True

    @api.constrains('date_order')
    def _set_date_order_line(self):
        for line in self.order_line:
            line.date_order = self.date_order

    @api.constrains('analytic_account_id')
    def _set_analytic_acc_line(self):
        for line in self.order_line:
            line.analytic_acc = self.analytic_account_id.id

    @api.constrains('debit_acc')
    def _set_debit_acc_line(self):
        for line in self.order_line:
            line.debit_acc = self.debit_acc.id

    @api.onchange('order_line')
    def onchange_total_amount(self):
        subtotal = 0
        for line in self.order_line:
            subtotal += (line.product_qty * line.price_per_unit)
        self.amount_total = subtotal

    @api.multi
    def _compute_amount_total(self):
        subtotal = 0
        for line in self.order_line:
            subtotal += line.sub_total
        self.amount_total = subtotal

    name = fields.Char('Order Reference', readonly=True)
    origin = fields.Char('Origin', readonly=True)

    date_order = fields.Date('Order Date', readonly=False)
    payment_date = fields.Datetime('Payment Date', required=True)
    request_date = fields.Datetime('Requested Date', readonly=True)
    approved_date = fields.Datetime('Approved Date', readonly=True)

    order_line = fields.One2many('kr.purchase.order.line', 'order_id', 'Order Lines', readonly=False,
                                 states={'done':[('readonly', True)]})
    amount_total = fields.Float('Total Amount', readonly='True',
                                compute='_compute_amount_total', digits=dp.get_precision('Account'))
    description = fields.Text('Description')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=False)
    state = fields.Selection(selection=_STATES, default='draft')
    validate_by = fields.Many2one('res.users', 'Validate By', readonly=True,
                                  states={'draft': [('readonly', False)]})
    budget_controller = fields.Many2one('res.users', 'Buget Controller',
                                        states={'done': [('readonly', True)]})

    journal_id = fields.Many2one('account.journal', 'Journal', required=False, states={'progress': [('required', True)],
                                                                                       'validate': [('readonly', True)],
                                                                                       'done': [
                                                                                           ('readonly', True)]},
                                 readonly=False)
    debit_acc = fields.Many2one('account.account', 'Debit Account', required=False,
                                states={'progress': [('required', True)],
                                        'validate':[('required', True)],
                                        'done': [('readonly', True)]},
                                readonly=False)
    credit_acc = fields.Many2one('account.account', 'Credit Account', required=False,
                                 states={'progress': [('required', True)],
                                         'validate': [('required', True)],
                                         'done': [('readonly', True)]},
                                 readonly=False)
    entry_ref = fields.Many2one('account.move', 'Entry Reference', readonly=True)
    is_a2a = fields.Boolean('Is A2AGR?')
    requested_by = fields.Many2one('res.users', 'Requested By', readonly=True)
    approved_by = fields.Many2one('res.users', 'Approved By', readonly=True)

    picking = fields.Many2one('stock.picking', 'Picking', readonly=True)


class MarketListPurchaseOrderLine(models.Model):
    _name = 'kr.purchase.order.line'

    @api.onchange('product_qty', 'price_per_unit')
    def onchange_subtoal(self):
        self.sub_total = self.product_qty * self.price_per_unit

    @api.multi
    def _compute_sub_total(self):
        for line in self:
            line.sub_total = line.product_qty * line.price_per_unit

    @api.onchange('price_per_unit_riel')
    def onchangeRiel(self):
        self.price_per_unit = self.price_per_unit_riel / 4000

    @api.onchange('price_per_unit')
    def _onchageUSD(self):
        self.price_per_unit_riel = self.price_per_unit * 4000

    @api.constrains('product_id')
    def _set_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    name = fields.Char('Order Reference')
    order_id = fields.Many2one('kr.purchase.order')
    product_id = fields.Many2one('product.product', required=True)
    category_id = fields.Many2one('product.category', 'Category')
    product_qty = fields.Float('Quantity', required=True)
    product_uom_id = fields.Many2one('product.uom', 'Unit', readonly=True)
    price_per_unit_riel = fields.Float('Unit Price (Riel)', required=True)
    price_per_unit = fields.Float('Unit Price', digits=dp.get_precision('KRPO'))

    supplier_id = fields.Many2one('kirirom.supplier', 'Supplier')
    invoice_number = fields.Char('Invoice')

    state = fields.Selection(selection=_STATES, default='draft', related='order_id.state')

    date_order = fields.Date('Order Date', readonly=False)
    analytic_acc = fields.Many2one('account.analytic.account', 'Analytic Account',
                                   readonly=False)
    sub_total = fields.Float('Sub Total',
                             readonly=True, digits=dp.get_precision('KRPO'))

    debit_acc = fields.Many2one('account.account', 'Debit Account', required=False,
                                states={'done': [('readonly', True)]})

    @api.constrains('product_id')
    def _fun_contrains(self):
        self.category_id = self.product_id.categ_id.id
        self.date_order = self.order_id.date_order
        self.analytic_acc = self.order_id.analytic_account_id.id

    @api.constrains('product_qty', 'price_per_unit')
    def _compute_subtotal(self):
        self.sub_total = self.price_per_unit * self.product_qty








