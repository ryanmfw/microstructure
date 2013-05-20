class Order(object):
    BUY = 0
    SELL = 1
    LIMIT = 0
    MARKET = 1

    def __init__(self, order_type, side, price, amount, time=None, order_id=None):
        self.order_type = order_type
        self.side = side
        self.price = price
        self.amount = amount
        #if time:
        self.time = time
        #else:
        #    self.time = None  #TODO: Set to earliest time
        self.order_id = order_id
        self.active = True


class Fill(object):
    def __init__(self, side, price, amount, order_id=None):
        self.side = side
        self.price = price
        self.amount = amount
        self.order_id = order_id


class OrderManager(object):
    def __init__(self, order_id_start=10000000):
        self._orders = {}
        self._order_id_start = order_id_start

    def add_order(self, order):
        if not order.order_id:
            order.order_id = self._order_id_start
            self._order_id_start += 1
        self._orders[order.order_id] = order

    def find_order(self, order_type, side, price, amount):
        for order in self._orders:
            if order.order_type == order_type and order.side == side\
                    and order.price == price and order.amount == amount:
                return order
                #TODO: How to handle the order not existing

    def get_order(self, order_id):
        return self._orders[order_id]

    def remove_order(self, order_id):
        self._orders[order_id].active = False
        del self._orders[order_id]


class OrderBook(object):
    class Entry(object):
        def __init__(self, price, side):
            self.price = price
            self.side = side
            #self.orders = []
            self._orders = []
            self._orders_dict = {}
            #self.orders_dict.set

        def add_order(self, order):
            self._orders.append(order)
            self._orders.sort(key=lambda order: order.time)
            #self.orders.sort(key = lambda order: order.time)
            #self.orders_dict[order.time] += order
            self._orders_dict[order.order_id] = order

        def add_fill(self, fill):
            if fill.order_id:
                [order for order in self._orders if order.order_id == fill.order_id][0].amount -= fill.amount
            else:
                self._orders[0].amount -= fill.amount
                fill.order_id = self._orders[0].order_id
                if self._orders[0].amount == 0:
                    self._orders[0].active = 0
                    self._orders.pop(0)
            return fill

        def fill(self, order):
            fills = []
            amount_left = order.amount
            while amount_left > 0 and len(self._orders) > 0:
                if self._orders[0].amount > amount_left:
                    fill_amount = amount_left
                    amount_left = 0
                    order.amount = 0
                    self._orders[0].amount -= amount_left
                else:
                    fill_amount = self._orders[0].amount
                    amount_left -= fill_amount
                    order.amount -= fill_amount
                    self._orders[0].active = False
                    self._orders.pop(0)
                fill = Fill(self.side, self.price, fill_amount)
                fills.append(fill)
            return amount_left, order, fills

        def cancel_order(self, order_id):
            self._delete_order(order_id)

        def _delete_order(self, order_id):
            idx = None
            for x in range(len(self._orders)):
                if self._orders[x].order_id == order_id:
                    idx = x
                    break
            self._orders.pop(x)
            #del self._orders_dict[order_id]

        def available(self):
            return sum(order.amount for order in self._orders if order.active)

        def value(self):
            return self.available() * self.price

    def __init__(self, asks_init={}, bids_init={}):

        self._asks = {}
        self._bids = {}
        self._order_list = []
        #self._fills_orders = fill_orders
        self._order_manager = OrderManager()
        if asks_init != {} or bids_init != {}:
            self.set_book(asks_init, bids_init)

    def set_book(self, asks, bids):
        for key in asks.keys():
            order = Order(Order.LIMIT, Order.SELL, key, asks[key])
            self.add_order(order)
        for key in bids.keys():
            order = Order(Order.LIMIT, Order.BUY, key, bids[key])
            self.add_order(order)

    def add_order(self, order):
        if order.order_type == Order.LIMIT:
            if (order.side == Order.BUY and order.price > min([1000000000]+self._asks.keys())) \
                    or (order.side == Order.SELL and order.price < max([0]+self._bids.keys())):
                return self._add_market(order)
            else:
                return self._add_limit(order)
        elif order.order_type == Order.MARKET:
            return self._add_market(order)

    def _add_limit(self, order):
        self._order_manager.add_order(order)
        side = self._get_side(order.side)

        if not order.price in side:
            side[order.price] = OrderBook.Entry(order.price, order.side)
        side[order.price].add_order(order)

        return 0, order, []

    def _add_market(self, order):
        side = self._get_side(order.side, reverse=True)
        op = self._get_side_op(order.side, reverse=True)
        amount_left = order.amount
        fills = []
        while amount_left > 0 and len(side.keys()) > 0:
            amount_left, order, fill = side[op(side.keys())].fill(order)
            fills += fill
            self._clean_entries()
        return amount_left, order, fills

    def cancel_order(self, order):
        if not isinstance(order, Order):
            order = self._order_manager.get_order(order)
        if order.active:
            side = self._get_side(order.side)
            side[order.price].cancel_order(order.order_id)
            self._order_manager.remove_order(order.order_id)
            self._clean_entries()

    def add_fill(self, fill):
        side = self._get_side(fill.side)
        side[fill.price].add_fill(fill)
        return fill

    def find_order(self, order_type, side, price, amount):
        return self._order_manager.find_order(order_type, side, price, amount)

    def _clean_entries(self):
        del_list = []
        for price, entry in self._asks.iteritems():
            if entry.available() == 0:
                del_list.append(price)
        for price in del_list:
            del self._asks[price]
        del_list = []
        for price, entry in self._bids.iteritems():
            if entry.available() == 0:
                del_list.append(price)
        for price in del_list:
            del self._bids[price]

    def _get_side(self, side, reverse=False):
        if side == Order.BUY ^ reverse:
            return self._bids
        elif side == Order.SELL ^ reverse:
            return self._asks
            #TODO: Raise error otherwise

    def _get_side_op(self, side, reverse=False):
        if side == Order.BUY ^ reverse:
            return max
        elif side == Order.SELL ^ reverse:
            return min