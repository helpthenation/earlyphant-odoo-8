from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected')
]


# --------------- Market List Line - Day 1 ---------------

class MarketListRequestBreakfastDay1Line(models.Model):
    _name = 'marketlist.request.breakfast.day1.line'
    _description = 'Market List Request Line '

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)


    date_required = fields.Date(string='Request Date', required=True,
                                track_visibility='onchange',
                                default=fields.Date.context_today)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestLunchDay1Line(models.Model):
    _name = 'marketlist.request.lunch.day1.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est


    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)

    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestDinnerDay1Line(models.Model):
    _name = 'marketlist.request.dinner.day1.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestDrystoreDay1Line(models.Model):
    _name = 'marketlist.request.drystore.day1.line'
    _description = 'Market List Request Line '

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')])

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Exp. Price')
    total_price_est = fields.Float('Exp. Total Price',readonly=True,compute='_compute_total_price_est',
        required=True
        )
    product_uom_id = fields.Many2one('product.uom', 'Unit',
                                     track_visibility='onchange',
                                     required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id



# --------------- Market List Line - Day 2 ---------------
class MarketListRequestBreakfastDay2Line(models.Model):
    _name = 'marketlist.request.breakfast.day2.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


class MarketListRequestLunchDay2Line(models.Model):
    _name = 'marketlist.request.lunch.day2.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestDinnerDay2Line(models.Model):
    _name = 'marketlist.request.dinner.day2.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


class MarketListRequestDrystoreDay2Line(models.Model):
    _name = 'marketlist.request.drystore.day2.line'
    _description = 'Market List Request Line '

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True,
        domain=[('categ_id.parent_id.name','=','Market List')]
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


# --------------- Market List General ---------------
class MarketListRequestA2AGeneralLine(models.Model):
    _name = 'marketlist.request.general.a2a.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    @api.constrains('product_id')
    def _set_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit', readonly=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.general.a2a.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)


    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est


# --------------- Market List General ---------------
class MarketListRequestGeneralLine(models.Model):
    _name = 'marketlist.request.general.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    @api.constrains('product_id')
    def _set_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit', readonly=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.general.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)


    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est


# --------------- Market List Pine View Kitchen ---------------
class MarketListRequestVegetableAndHerbLine(models.Model):
    _name = 'marketlist.request.vegetableandherb.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


class MarketListRequestFruitLine(models.Model):
    _name = 'marketlist.request.fruit.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


class MarketListRequestPoultryLine(models.Model):
    _name = 'marketlist.request.poultry.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestSeafoodAndFishLine(models.Model):
    _name = 'marketlist.request.seafoodandfish.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id

class MarketListRequestBeefAndPorkLine(models.Model):
    _name = 'marketlist.request.beefandpork.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)


    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id


class MarketListRequestOtherLine(models.Model):
    _name = 'marketlist.request.other.line'
    _description = 'Market List Request Line'

    @api.multi
    def _compute_total_price_est(self):
        for line in self:
            line.total_price_est = line.product_qty * line.price_per_unit_est

    product_id = fields.Many2one(
        'product.product', 'Product',
        track_visibility='onchange',
        required=True
        )

    name = fields.Char('Description', size=256,
                       track_visibility='onchange')

    price_per_unit_est = fields.Float('Estimated Price',required=True)

    total_price_est = fields.Float('Estimated Total Price',readonly=True,
                                   compute='_compute_total_price_est')

    product_uom_id = fields.Many2one('product.uom', 'Unit',required=True)
    product_qty = fields.Float('Quantity', track_visibility='onchange',
                               digits_compute=dp.get_precision(
                                   'Product Unit of Measure'),required=True)
    request_id = fields.Many2one('marketlist.pvk.request',
                                 'Market List Request',
                                 ondelete='cascade', readonly=True)

    @api.onchange('price_per_unit_est')
    def onchange_price_per_unit_est(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_qty')
    def onchange_product_qty(self):
        self.total_price_est = self.product_qty * self.price_per_unit_est

    @api.onchange('product_id')
    def onchange_product_uom(self):
        self.product_uom_id = self.product_id.uom_id.id
