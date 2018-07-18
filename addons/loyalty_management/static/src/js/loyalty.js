openerp.loyalty_management = function (instance) {
    console.log('loyalty.js');

    var pos_base = instance.point_of_sale;
    var round_pr = instance.web.round_precision;
    var QWeb = instance.web.qweb;

    pos_base.PopUpWidget = pos_base.PosBaseWidget.extend({
        events: {
            'click .selection-item': 'click_item'
        },
        show: function () {
            if (this.$el) {
                this.$el.removeClass('oe_hidden');
            }
        },
        /* called before hide, when a popup is closed */
        close: function () {
        },
        /* hides the popup. keep in mind that this is called in the initialization pass of the
         * pos instantiation, so you don't want to do anything fancy in here */
        hide: function () {
            if (this.$el) {
                this.$el.addClass('oe_hidden');
            }
        }
    });

    pos_base.SelectionPopupWidget = pos_base.PopUpWidget.extend({
        template: 'SelectionPopupWidget',
        show: function (options) {
            options = options || {};
            var self = this;
            this._super(options);

            this.title = options.title;
            this.list = options.list || [];
            this.options = options;
            this.renderElement();

            this.$('.footer .button').click(function () {
                self.pos_widget.screen_selector.close_popup();
            });
        },
        click_item: function (event) {
            var self = this;
            self.pos_widget.screen_selector.close_popup();
            if (this.options.confirm) {
                var item = this.list[parseInt($(event.target).data('item-index'))];
                item = item ? item.item : item;
                this.options.confirm.call(self, item);
            }
        }
    });

    pos_base.load_fields = function (model_name, fields) {
        if (!(fields instanceof Array)) {
            fields = [fields];
        }

        var models = pos_base.PosModel.prototype.models;
        for (var i = 0; i < models.length; i++) {
            var model = models[i];
            if (model.model === model_name) {
                // if 'fields' is empty all fields are loaded, so we do not need
                // to modify the array
                if ((model.fields instanceof Array) && model.fields.length > 0) {
                    model.fields = model.fields.concat(fields || []);
                }
            }
        }
    };

    pos_base.load_fields('res.partner', 'loyalty_points');
    pos_base.load_fields('res.partner', 'loyalty_id');
    pos_base.load_fields('product.product', 'categ_id');

    pos_base.PosModel.prototype.models.push(
        {
            model: 'loyalty.program',
            fields: ['name', 'pp_currency', 'pp_product', 'pp_order', 'rounding'],
            domain: null,
            loaded: function (self, loyalties) {
                self.loyalty = loyalties;
            }
        }
        , {
            model: 'loyalty.rule',
            fields: ['name', 'type', 'product_id', 'category_id', 'pp_product', 'pp_currency', 'loyalty_program_id', 'wh_categ'],
            domain: null,
            loaded: function (self, rules) {
                self.loyalty.rules = rules;
                self.loyalty.rules_by_product_id = {};
                self.loyalty.rules_by_category_id = {};

                for (var i = 0; i < rules.length; i++) {
                    var rule = rules[i];

                    if (rule.type === 'product') {
                        if (!self.loyalty.rules_by_product_id[rule.product_id[0]]) {
                            self.loyalty.rules_by_product_id[rule.product_id[0]] = [rule];
                        }
                        else {
                            self.loyalty.rules_by_product_id[rule.product_id[0]].push(rule);
                        }
                    }
                    else if (rule.type === 'category') {
                        var category_id = rule.wh_categ[0];
                        if (!self.loyalty.rules_by_category_id[category_id]) {
                            self.loyalty.rules_by_category_id[category_id] = [rule];
                        }
                        else {
                            self.loyalty.rules_by_category_id[category_id].push(rule);
                        }
                    }
                }
            }
        },
        {
            model: 'loyalty.reward',
            fields: ['name', 'type', 'minimum_points', 'gift_product_id', 'point_cost', 'discount_product_id', 'discount', 'point_product_id', 'loyalty_program_id'],
            domain: null,
            loaded: function (self, rewards) {
                self.loyalty.rewards = rewards;
                self.loyalty.rewards_by_id = {};
                for (var i = 0; i < rewards.length; i++) {
                    self.loyalty.rewards_by_id[rewards[i].id] = rewards[i];
                }
            }
        }
    );

    pos_base.OrderWidget.include({
        update_summary: function () {
            this._super();
            var order = this.pos.get_order();
            var $loypoints = $(this.el).find('.summary .loyalty-points');

            if (this.pos.loyalty && order.get_client()) {
                var points_won = order.get_won_points();
                var points_spent = order.get_spent_points();
                var points_total = order.get_new_total_points();

                $loypoints.replaceWith($(QWeb.render('LoyaltyPoints', {
                    widget: this,
                    rounding: this.pos.loyalty.rounding,
                    points_won: points_won,
                    points_spent: points_spent,
                    points_total: points_total
                })));

                $loypoints = $(this.el).find('.summary .loyalty-points');
                $loypoints.removeClass('oe_hidden');

                if (points_total < 0) {
                    $loypoints.addClass('negative');
                } else {
                    $loypoints.removeClass('negative');
                }
            }
            else {
                $loypoints.empty();
                $loypoints.addClass('oe_hidden');
            }
            // if (this.pos.loyalty &&
            //     this.getParent().action_buttons &&
            //     this.getParent().action_buttons.loyalty) {
            //
            //     var rewards = order.get_available_rewards();
            //     this.getParent().action_buttons.loyalty.highlight(!!rewards.length);
            // }
        }

    });

    var _super_orderline = pos_base.Orderline;
    pos_base.Orderline = pos_base.Orderline.extend({

        get_reward: function () {
            //this here refer line which has been calling to get_reward method
            return this.pos.loyalty.rewards_by_id[this.reward_id];
        },
        export_as_JSON: function () {
            console.log('export_as_JSON');
            var json = _super_orderline.prototype.export_as_JSON.apply(this, arguments);
            json.reward_id = this.reward_id;
            return json;
        },
        init_from_JSON: function (json) {
            console.log('init_from_JSON');
            _super_orderline.prototype.init_from_JSON.apply(this, arguments);
            this.reward_id = json.reward_id;
        }
    });

    var _super = pos_base.Order;
    pos_base.Order = pos_base.Order.extend({
        addProduct: function (product, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get('selectedOrder').addProduct(product, options);
            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new pos_base.Orderline({}, {pos: this.pos, order: this, product: product});

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }
            if (options.price !== undefined) {
                line.set_unit_price(options.price);
            }
            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }
            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            var last_orderline = this.getLastOrderline();
            if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false) {
                last_orderline.merge(line);
            } else {
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
        },

        get_orderlines: function () {
            return this.get('orderLines').models;
        },

        /* The total of points won, excluding the points spent on rewards */
        get_won_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            }
            ////////////////////loop to find loyalty program base client
            var loy_program;
            for (var i = 0; i < this.pos.loyalty.length; i++) {

                if (this.pos.loyalty[i].id === this.get_client().loyalty_id[0])
                    loy_program = i;
            }
            /////////////////////////////////////////////////////////////

            var orderLines = this.get_orderlines();
            var loyalty_program = this.pos.loyalty[loy_program] || false;
            if (loyalty_program) {
                var rounding = this.pos.loyalty[loy_program].rounding || 0;
                var product_sold = 0;
                var total_sold = 0;
                var total_points = 0;

                for (i = 0; i < orderLines.length; i++) {
                    var line = orderLines[i];
                    var product = line.get_product();
                    var overriden = false;

                    if (line.get_reward()) {  // Reward products are ignored
                        continue;
                    }

                    ////////////////// to consider the rule's index of rules_by_product_id object
                    var temp_rule = this.pos.loyalty.rules_by_product_id[product.id] || [];
                    var loy_rule = -1;
                    for (var t = 0; t < temp_rule.length; t++) {
                        if (temp_rule[t].loyalty_program_id[0] === this.pos.loyalty[loy_program].id)
                            loy_rule = t;
                    }
                    ////////////////////////////////////////////////////////////////////////////

                    if (loy_rule !== -1)
                        var rules = this.pos.loyalty.rules_by_product_id[product.id][loy_rule];
                    else
                        rules = false;

                    if (rules) {
                        total_points += round_pr(line.get_quantity() * rules.pp_product, rounding);
                        total_points += round_pr(line.get_price_with_tax() * rules.pp_currency, rounding);
                    }

                    if (product.categ_id) {
                        var category_id = product.categ_id[0];

                        if (category_id) {
                            var loy_categ = -1;
                            var temp_categ = this.pos.loyalty.rules_by_category_id[category_id] || [];
                            for (t = 0; t < temp_categ.length; t++) {
                                if (temp_categ[t].loyalty_program_id[0] === this.pos.loyalty[loy_program].id)
                                    loy_categ = t;
                            }

                            if (loy_categ !== -1)
                                var rules_categ = this.pos.loyalty.rules_by_category_id[category_id][loy_categ];
                            else
                                rules_categ = false;

                            if (rules_categ) {
                                total_points += round_pr(line.get_quantity() * rules_categ.pp_product, rounding);
                                total_points += round_pr(line.get_price_with_tax() * rules_categ.pp_currency, rounding);
                            }
                        }
                    }
                    if (!overriden) {
                        product_sold += line.get_quantity();
                        total_sold += line.get_price_with_tax();

                    }
                }

                total_points += round_pr(total_sold * this.pos.loyalty[loy_program].pp_currency, rounding);
                total_points += round_pr(product_sold * this.pos.loyalty[loy_program].pp_product, rounding);
                total_points += round_pr(this.pos.loyalty[loy_program].pp_order, rounding);
                return total_points;
            }
        },

        /* The total number of points spent on rewards */
        get_spent_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            }
            else {
                var loy_program;
                for (var i = 0; i < this.pos.loyalty.length; i++) {

                    if (this.pos.loyalty[i].id === this.get_client().loyalty_id[0])
                        loy_program = i;
                }
                var lines = this.get_orderlines();
                var loyalty_program = this.pos.loyalty[loy_program] || false;

                if (loyalty_program) {
                    var rounding = this.pos.loyalty[loy_program].rounding;
                    var points = 0;

                    for (i = 0; i < lines.length; i++) {
                        var line = lines[i];
                        var reward = line.get_reward();
                        if (reward) {
                            if (reward.type === 'gift') {
                                points += round_pr(line.get_quantity() * reward.point_cost, rounding);
                            }
                            else if (reward.type === 'discount') {
                                points += round_pr(-line.get_display_price() * reward.point_cost, rounding);
                            }
                        }
                    }
                    return points;
                }
            }
        },

        /* The total number of points lost or won after the order is validated */
        get_new_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_won_points() - this.get_spent_points(), this.pos.loyalty.rounding);
            }
        },

        /* The total number of points that the customer will have after this order is validated */
        get_new_total_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_client().loyalty_points + this.get_new_points(), this.pos.loyalty.rounding);
            }
        },

        /* The number of loyalty points currently owned by the customer */
        get_current_points: function () {
            return this.get_client() ? this.get_client().loyalty_points : 0;
        },

        /* The total number of points spendable on rewards */
        get_spendable_points: function () {
            if (!this.pos.loyalty || !this.get_client()) {
                return 0;
            } else {
                return round_pr(this.get_client().loyalty_points - this.get_spent_points(), this.pos.loyalty.rounding);
            }
        },

        /* The list of rewards that the current customer can get */
        get_available_rewards: function () {
            var client = this.get_client();
            if (!client) {
                return [];
            }

            var rewards = [];
            for (var i = 0; i < this.pos.loyalty.rewards.length; i++) {
                var reward = this.pos.loyalty.rewards[i];
                if (reward.type === 'gift' && reward.point_cost > this.get_spendable_points()) {
                    continue;
                }
                rewards.push(reward);
            }
            if (this.pos.loyalty.rewards.length === 0)
                return 'no reward';
            else
                return rewards;
        },

        apply_reward: function (reward) {
            var product, order_total, spendable;
            var lrounding;
            var crounding;

            if (reward.type === 'gift') {
                product = this.pos.db.get_product_by_id(reward.gift_product_id[0]);
                if (!product) {
                    return;
                }
                // function addProduct defined at models.js
                this.addProduct(product, {
                    price: 0,
                    quantity: 1,
                    merge: false,
                    extras: {reward_id: reward.id}
                });

            }
            else if (reward.type === 'discount') {

                var loy_program;
                for (var i = 0; i < this.pos.loyalty.length; i++) {

                    if (this.pos.loyalty[i].id === this.get_client().loyalty_id[0])
                        loy_program = i;
                }

                lrounding = this.pos.loyalty[loy_program].rounding;
                crounding = this.pos.currency.rounding;
                spendable = this.get_spendable_points();
                order_total = this.getTotalTaxIncluded();

                var discount = round_pr(order_total * reward.discount, crounding);

                if (round_pr(discount * reward.point_cost, lrounding) > spendable) {
                    discount = 0;
                    this.pos.pos_widget.screen_selector.show_popup('error',
                        {
                            'message': 'Error',
                            'comment': 'Customer doese not have enough point for discount'
                        }
                    );
                }

                if (discount !== 0) {
                    product = this.pos.db.get_product_by_id(reward.discount_product_id[0]);

                    if (!product) {
                        return;
                    }

                    this.addProduct(product, {
                        price: -discount,
                        quantity: 1,
                        merge: false,
                        extras: {reward_id: reward.id}
                    });
                }

            }
        },

        // finalize: function(){
        //     var client = this.get_client();
        //     if ( client ) {
        //         client.loyalty_points = this.get_new_total_points();
        //         // The client list screen has a cache to avoid re-rendering
        //         // the client lines, and so the point updates may not be visible ...
        //         // We need a better GUI framework !
        //         this.pos.gui.screen_instances.clientlist.partner_cache.clear_node(client.id);
        //     }
        //     _super.prototype.finalize.apply(this,arguments);
        // },

        export_for_printing: function () {
            console.log('export_for_printing');
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            if (this.pos.loyalty && this.get_client()) {
                json.loyalty = {
                    rounding: this.pos.loyalty.rounding || 1,
                    name: this.pos.loyalty.name,
                    client: this.get_client().name,
                    points_won: this.get_won_points(),
                    points_spent: this.get_spent_points(),
                    points_total: this.get_new_total_points(),
                };
            }
            return json;
        },

        export_as_JSON: function () {
            console.log('export_as_JSON');
            var json = _super.prototype.export_as_JSON.apply(this, arguments);
            json.loyalty_points = this.get_new_points();
            return json;
        }
    });

    pos_base.PosWidget.include({
        build_widgets: function () {
            var self = this;
            this._super();
            this.selection_popup = new pos_base.SelectionPopupWidget(this, {});
            this.selection_popup.appendTo(this.$el);
            this.screen_selector = new pos_base.ScreenSelector({
                pos: this.pos,
                screen_set: {
                    'products': this.product_screen,
                    'payment': this.payment_screen,
                    'scale': this.scale_screen,
                    'receipt': this.receipt_screen,
                    'clientlist': this.clientlist_screen
                },

                popup_set: {
                    'error': this.error_popup,
                    'error-barcode': this.error_barcode_popup,
                    'error-traceback': this.error_traceback_popup,
                    'confirm': this.confirm_popup,
                    'unsent-orders': this.unsent_orders_popup,
                    'selection': this.selection_popup
                },
                default_screen: 'products',
                default_mode: 'cashier'
            });

            var loy_button = $(QWeb.render('LoyaltyButton'));
            this.$('.control-buttons').removeClass('oe_hidden');
            loy_button.appendTo(this.$('.control-buttons'));

            loy_button.click(function () {
                var order = self.pos.get_order();
                var client = order.get_client();
                var rewards = order.get_available_rewards();
                console.log(rewards);

                if (rewards.length === 0) {
                    if (!client) {
                        self.pos_widget.screen_selector.set_current_screen('clientlist');
                    }
                    else {
                        self.pos_widget.screen_selector.show_popup('error',
                            {
                                'message': 'Error',
                                'comment': 'Spendable point is less than required point'
                            }
                        )
                    }
                }
                else if (rewards === 'no reward') {
                    self.pos_widget.screen_selector.show_popup('error',
                        {
                            'message': 'Error',
                            'comment': 'This loyalty type does not contained any rewards'
                        }
                    )
                }
                else {
                    var list = [];
                    for (var i = 0; i < rewards.length; i++) {
                        if (rewards[i].loyalty_program_id[0] === client.loyalty_id[0]) {
                            list.push({
                                label: rewards[i].name,
                                item: rewards[i]
                            });
                        }
                    }
                    self.pos_widget.screen_selector.show_popup('selection',
                        {
                            'title': 'Please select a reward',
                            'list': list,
                            'confirm': function (reward) {
                                order.apply_reward(reward);
                            }
                        });
                }
            });

        }
    });
};
