

openerp.hotel_card_pos = function (instance, module) {

	_t = instance.web._t;
    var pos_base = instance.point_of_sale;
    var QWeb = instance.web.qweb;



    // load 'hotel.folio' model into point of sale //
    pos_base.PosModel.prototype.models.push(
        {
            
                model: 'hotel.folio',
                fields: ['name', 'state', 'partner_id', 'write_date'],
                domain: [['state','=','draft']],
                loaded: function (self, hotel_folio) {

                    self.folios = hotel_folio;
                    self.db.add_folios(hotel_folio);
                }
            
        });

    //confirm popup widget//
    pos_base.confirm_popup_me = pos_base.PopUpWidget.extend({
        template: 'ConfirmPopupWidgetMe',
        show: function(options){
            var self = this;
            this._super();

            this.message = options.message || '';
            this.comment = options.comment || '';
            this.comment1 = options.comment1 || '';
            this.renderElement();
            
            this.$('.button.cancel').click(function(){

            	self.pos_widget.screen_selector.set_current_screen('products');
            	self.pos_widget.screen_selector.set_current_screen('hotelcard');
                // self.pos_widget.screen_selector.close_popup();
                if( options.cancel ){
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function(){
                self.pos_widget.screen_selector.close_popup();
                if( options.confirm ){
                    options.confirm.call(self);
                }
            });
        },
    });
    // extend Selection PopUpWidget class from POS to override some functions//
    pos_base.SelectionPopupWidget = pos_base.PopUpWidget.extend({
        template: 'SelectionPopupWidget',

        show: function (options)
            {
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
        click_item: function (event)
            {
                var self = this;
                self.pos_widget.screen_selector.close_popup();
                if (this.options.confirm) {
                    var item = this.list[parseInt($(event.target).data('item-index'))];
                    item = item ? item.item : item;
                    this.options.confirm.call(self, item);
                }
            },

    });

    // include functions into the parent class //
    pos_base.PosWidget.include({
        build_widgets: function () {

            
            var self = this;
            this._super();
            //create object for confirm popup //
            this.confirm_popup_me = new pos_base.confirm_popup_me(this,{});
            this.confirm_popup_me.appendTo(this.$el);
            // create object for hotelcard screen //
            this.hotelcard_screen = new pos_base.HotelCardScreenWidget(this, {});
            // append hotel card screen to the POS screen //
            this.hotelcard_screen.appendTo(this.$('.screens'));

            // create object for selection popup Screen //
            this.selection_popup = new pos_base.SelectionPopupWidget(this, {});
            this.selection_popup.appendTo(this.$el);

            // create screen selector object //
            this.screen_selector = new pos_base.ScreenSelector({

                    pos: this.pos,
                    screen_set: {
                        'products': this.product_screen,
                        'payment': this.payment_screen,
                        'scale': this.scale_screen,
                        'receipt': this.receipt_screen,
                        'clientlist': this.clientlist_screen,
                        'hotelcard': this.hotelcard_screen
                    },

                    popup_set: {
                        'error': this.error_popup,
                        'error-barcode': this.error_barcode_popup,
                        'error-traceback': this.error_traceback_popup,
                        'confirm': this.confirm_popup_me,
                        'unsent-orders': this.unsent_orders_popup,
                        'selection': this.selection_popup,
                    },
                    default_screen: 'products',
                    default_mode: 'cashier'
                });

            // create object for hotelcard button //
            var Hcard_button = $(QWeb.render('HotelCardButton'));
            this.$('.control-buttons').removeClass('oe_hidden');

            // append button to the '.control-buttons' class //
            Hcard_button.appendTo(this.$('.paypad'));

            // create eventhandler for the button //
            Hcard_button.click(function ()
                {
                    
                     var currentOrder = self.pos.get('selectedOrder');

                    // to check if there's order is selected or not //
                    if (currentOrder.get('orderLines').models.length !== 0){


                        //screen to load all the draft folio //
                        self.pos_widget.screen_selector.set_current_screen('hotelcard');
                    }
                    else {
                        
                        // this is error popup screen //
                        self.pos_widget.screen_selector.show_popup('error',
                            {
                                 'message': _t('Empty Order'),
                                 'comment': _t('There must be at least one product in your order before Hotel Card can be proceeded'),
                            });
                    }
                });

        },

        // function to push the 'order' in the form of JSON to python
         _push_: function(order)
        {
            var self = this;
            if(order)
            {
                // this.proxy.log('push_order',order.export_as_JSON()); //
                this.add_data(self.export_to_JSON(order));
            }

            var pushed = new $.Deferred();
            var flushed = self._flush_(self.pos.db.get_orders());

                flushed.always(function(ids)
                {
                    pushed.resolve();
                });

            return pushed;
        },
        // my code

        // function to add data 'order' in to database (db) //
        add_data: function(order){
            var order_id = order.uid;
            var orders  = this.pos.db.load('orders',[]);

            // if the order was already stored, we overwrite its data
            for(var i = 0, len = orders.length; i < len; i++){
                if(orders[i].id === order_id){
                    orders[i].data = order;
                    this.pos.db.save('orders',orders);
                    return order_id;
                }
            }
            orders.push({id: order_id, data: order});
            this.pos.db.save('orders',orders);
            return order_id;
        },
         /////////////////////////////////

        // funtion to convert 'order' into JOSON form for Python //
        export_to_JSON: function(order) {
            var orderLines, paymentLines;
            orderLines = [];
            (order.get('orderLines')).each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            (order.get('paymentLines')).each(_.bind( function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            console.log(order,"---------");
            return {
                name: order.getName(),
                // number_of_customer: order.get_number_customer(),
                table_num: order.get_table_number(),
                amount_paid: order.getPaidTotal(),
                amount_total: order.getTotalTaxIncluded(),
                amount_tax: order.getTax(),
                amount_return: order.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: order.pos.pos_session.id,
                partner_id: order.get_client() ? order.get_client().id : false,
                user_id: order.pos.cashier ? order.pos.cashier.id : order.pos.user.id,
                uid: order.uid,
                sequence_number: order.sequence_number,
                folio_id: order['folios'],
            };
        },

        // function to check if it connectio to db //
        _flush_: function(orders)
         {
            var self = this;

            this.set('synch',{ state: 'connecting', pending: orders.length});

            return self.hotel_card_pos_connector(orders).done(function (server_ids){
                var pending = self.pos.db.get_orders().length;

                self.set('synch', {
                    state: pending ? 'connecting' : 'connected',
                    pending: pending
                });

                return server_ids;
            });
         },

        // function that establish connection between JS and Python //
        hotel_card_pos_connector: function(orders, options)
        {
        	// options = options || {};
        	self = this;
        	// create object for 'hotel.restaurant.order' model to establish connection with it //
            var hotelRestaurantModel = new instance.web.Model('hotel.restaurant.order');
            //                                                                                 //
            // invoke the method inside 'hotel.restaurant.order' model  name 'create_table_order' in hotel_card.py //
            var res = hotelRestaurantModel.call('create_table_order',
                [
                    _.map(orders, function (order) {
                            
                            return order;
                        })
                ],
                undefined,
                {
                    // shadow: !options.to_invoice,
                    // timeout: timeout
                }
            ).then(function(server_ids){
                _.each(orders,function(order){
                        self.pos.get('selectedOrder').destroy();
                    });
                return server_ids;
            }).always(function () {
                _.each(orders, function (order) {
                        self.pos.db.remove_order(order.id);
                });
            }).fail(function (error, event)
                {       
                        
                // prevent an error popup creation by the rpc failure //
                // we want the failure to be silent as we send the orders in the background //
                
                // event.preventDefault();
            });

            
            return res;
        },

        // function to load new folio that just create //
        load_new_folios: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.pos.__proto__.models,function(model){ return model.model === 'hotel.folio'; }).fields;
            new instance.web.Model('hotel.folio')
                .query(fields)
                .filter([['write_date','>', self.pos.db.get_folio_write_date()]])
                .all({'timeout':3000, 'shadow': true})
                .then(function(folios){
                    if (self.pos.db.add_folios(folios)) {
                        // check if the folios we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(err,event){ event.preventDefault(); def.reject(); });
            return def;
        },
    });

    // extend ScreenWidget Class to create a new screen //
    pos_base.HotelCardScreenWidget = pos_base.ScreenWidget.extend({
        template: 'HotelCardScreenWidget',



        init: function(parent, options) {
        this._super(parent, options);
        console.log("This HotelCardScreenWidget");
        },
        show_leftpane: true,
        auto_back: true,


        show: function(){
            var self = this;

            // function to invoke the parent class //
            this._super();

            // function handler for the 'Cancel' button //
            this.$('.back').click(function(){
                self.pos_widget.screen_selector.set_current_screen('products');
            });

            // object to take all orders from POS //
            var order = self.pos.get_order();
            var i = 0;

            // function handler for selecting a particular folio line //
            self.$('.folio-list-contents').delegate('.client-line','click',function(event){
                
                // condition to prevent looping 
                // it takes only one iteration
                var j = 0;
                if (i===j){
                    
                    self.line_select(event,$(folios),parseInt($(this).data('id')),order);
                    i = i+1;
                }
                            
            });

            // function handler for the searchbox 'search folio' //
            var search_timeout = null;
            this.$('.searchbox input').on('keyup',function(event){
                clearTimeout(search_timeout);
                var query = this.value;
                search_timeout = setTimeout(function(){
                    self.perform_search_folio(query,event.which === 13);
                },70);
            });

            // get folio object that already sorted //
            var folios = this.pos.db.get_folios_sorted(1000);

            // call function to render the folio list //
            self.render_list(folios);
            // reload the folio if there is creation of new folio //
            self.reload_folios();
            
        },

        // funtion to search for a particular folio //
        perform_search_folio: function(query, associate_result){
            var self = this;
            if(query){
                var folios = self.pos.db.search_folio(query);
                self.render_list(folios);
            }else{
                var folios = self.pos.db.get_folios_sorted();
                self.render_list(folios);
            }
        },

        // function to ganerate the folio that in draft state //
        render_list: function(folio){
            console.log("render_list")
            var contents = this.$el[0].querySelector('.folio-list-contents');
            contents.innerHTML = "";
            var sorted_folio = [];
            for (var j =0, len = folio.length; j < len; j++) {
                if (folio[j].state === 'draft') {
                    sorted_folio.push(folio[j]);
                }
            };
            for(var i = 0, len = sorted_folio.length; i < len; i++){
                var partner    = sorted_folio[i];
                var clientline_html = QWeb.render('FolioLine',{widget: this, partner:sorted_folio[i]});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];

                if( folio === this.new_client ){
                    clientline.classList.add('highlight');
                }else{
                    clientline.classList.remove('highlight');
                }

                contents.appendChild(clientline);
            }
        },

        // function handler for selecting a particular folio line //
        line_select: function(event,$folio_lines,id,order){
            var self = this;
            var folios = $folio_lines;
            var folio = [];

            // loop to get all folios 
            for(var a = 0, len = folios.length; a<len; a++){
                    // check if it the folio being selected 
                    // then push 'folios' into order 
                    // then assign the correct folio into it
                    if (folios[a].id === id){
                        folio = folios[a];
                        order['folios'] = folio;
                        console.log(JSON.stringify(folio))
                    	self.pos_widget.screen_selector.show_popup('confirm',{
	                        message: _t('Are you sure this folio ?'),
	                        comment: _t("Folio: "+folio.name),
	                        comment1: _t("Customer: "+folio.partner_id[1]),
	                        confirm: function(){
	                        	// call the _push__() function from pos_widget class //
	                        	// after push the order then destroy it from POS
	                            self.pos_widget._push_(order);
	                            this.pos_widget.screen_selector.set_current_screen('products');
	                        },
	                    });  
                    }
            }
            
                
        },

        // function to reload folio //
        reload_folios: function(){
            var self = this;
            return self.pos_widget.load_new_folios().then(function(){
                self.render_list(self.pos.db.get_folios_sorted());

                // update the currently assigned client if it has been changed in db.
                var curr_client = self.pos.get_order().get_client();
                if (curr_client) {
                    self.pos.get_order().set_client(self.pos.db.get_folio_by_id(curr_client.id));
                }
            });
        },

        close: function(){
            this._super();
        },


    });

    pos_base.PosDB.include({

        // override the init() to create some variables //
        init: function(options){
            this._super(options);
            this.folio_sorted = [];
            this.folio_by_id = {};
            this.folio_search_string = "";
            this.folio_write_date = null;
        },

        // funtios to add folio into database //
        add_folios: function(folios){
            console.log("add_folios")
            var updated_count = 0;
            var new_write_date = '';
            for(var i = 0, len = folios.length; i < len; i++){
                var folio = folios[i];

                if (
                        this.folio_write_date &&
                        this.folio_by_id[folio.id] &&
                        new Date(this.folio_write_date).getTime() + 1000 >=
                        new Date(folio.write_date).getTime() ) {
                    // FIXME: The write_date is stored with milisec precision in the database
                    // but the dates we get back are only precise to the second. This means when
                    // you read folios modified strictly after time X, you get back folios that were
                    // modified X - 1 sec ago.
                    continue;
                } else if ( new_write_date < folio.write_date ) {
                    new_write_date  = folio.write_date;
                }
                if (!this.folio_by_id[folio.id]) {

                    this.folio_sorted.push(folio.id);
                }
                this.folio_by_id[folio.id] = folio;

                updated_count += 1;
            }

            this.folio_write_date = new_write_date || this.folio_write_date;
            if (updated_count) {
                // If there were updates, we need to completely
                // rebuild the search string and the ean13 indexing

                this.folio_search_string = "";
                for (var id in this.folio_by_id) {
                    var folio = this.folio_by_id[id];
                    this.folio_search_string += this._folio_search_string(folio);
                }
            }
            return updated_count;
        },

        // function to get the write date of aparticular folio //
        get_folio_write_date: function(){
            console.log("this is get_folio_write_date")
            return this.folio_write_date;
        },

        // function to get folio by id //
        get_folio_by_id: function(id){
            return this.folio_by_id[id];
        },
        
        // function to sort the folio //
        get_folios_sorted: function(max_count){
            console.log("this is get_folio_sorted")
            max_count = max_count ? Math.min(this.folio_sorted.length, max_count) : this.folio_sorted.length;
            var folios = [];
            for (var i = 0; i < max_count; i++) {
                folios.push(this.folio_by_id[this.folio_sorted[i]]);
            }
            return folios;
        },

        // fucntion to search a folio //
        search_folio: function(query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
    
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                r = re.exec(this.folio_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_folio_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
        _folio_search_string: function(partner){
            var str =  partner.partner_id[1];
            var folio_owner = partner.name;
            str = '' + partner.id + ':' + ' ' + folio_owner + '' + str.replace(':','') + '\n';
            return str;
        },
    });

};
