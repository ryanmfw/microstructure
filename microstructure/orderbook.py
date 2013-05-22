class Order(object):
    """


    """

    BUY = 0
    SELL = 1
    LIMIT = 0
    MARKET = 1

    def __init__(self, order_type, side, price, amount, time=None, order_id=None):
        """Creates an Order object.

        :param order_type:
        :type order_type: Order.LIMIT, Order.MARKET
        :param side:
        :type side: Order.BUY, Order.SELL
        :param price:
        :type price: float
        :param amount:
        :type amount: int
        :param time:
        :type time: datetime
        :param order_id:
        """

        self.order_type = order_type
        self.side = side
        self.price = price
        self.amount = amount
        self.time = time
        self.order_id = order_id
        self.active = True


class Fill(object):
    """


    """

    def __init__(self, side, price, amount, order_id=None):
        """Creates a Fill object.

        :param side:
        :type side:
        :param price:
        :type price:
        :param amount:
        :type amount:
        :param order_id:
        """

        self.side = side
        self.price = price
        self.amount = amount
        self.order_id = order_id


class OrderManager(object):
    """


    """

    def __init__(self, order_id_start=10000000):
        """Creates an OrderManager object.

        :param order_id_start:
        :type order_id_start:
        """
        self._orders = {}
        self._order_id_start = order_id_start

    def add_order(self, order):
        """Adds an order to the order manager.

        :param order:
        :type order:
        """

        if not order.order_id:
            order.order_id = self._order_id_start
            self._order_id_start += 1
        self._orders[order.order_id] = order

    def find_order(self, order_type, side, price, amount):
        """Finds an order in the order manager.

        :param order_type:
        :type order_type:
        :param side:
        :type side:
        :param price:
        :type price:
        :param amount:
        :type amount:
        """

        for order in self._orders:
            if order.order_type == order_type and order.side == side\
                    and order.price == price and order.amount == amount:
                return order
                #TODO: What if the order doesn't exist?

    def get_order(self, order_id):
        """Returns an order from the order manager.

        :param order_id:
        """

        return self._orders[order_id]

    def remove_order(self, order_id):
        """Removes an order from the order manager

        :param order_id:
        """

        self._orders[order_id].active = False
        del self._orders[order_id]

    def _clear(self):
        """Resets order manager."""

        self._orders = {}


class OrderBook(object):
    """


    """

    class Entry(object):
        """


        """

        def __init__(self, price, side):
            """Creates an Entry object.

            :param price:
            :type price:
            :param side:
            :type side:
            """

            self.price = price
            self.side = side
            self._orders = []


        def add_order(self, order):
            """Adds order to entry.

            :param order:
            :type order:
            """

            self._orders.append(order)
            self._orders.sort(key=lambda order: order.time)


        def add_fill(self, fill):
            """Adds fill to entry

            Description

            :param fill:
            :type fill:
            """

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
            """Fills order using orders in the entry.

            :param order:
            :type order:
            """

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
            """Cancels order in entry.

            For now, it just deletes the order. In the future it may do more.

            :param order_id:
            """

            self._delete_order(order_id)

        def _delete_order(self, order_id):
            """Deletes order from entry.

            :param order_id:
            """

            idx = None
            for x in range(len(self._orders)):
                if self._orders[x].order_id == order_id:
                    idx = x
                    break
            self._orders.pop(x)

        def available(self):
            """Determines the order depth for this entry.

            :returns int:
            """

            return sum(order.amount for order in self._orders if order.active)

        def value(self):
            """Determines the total value of the order depth for this entry.

            :returns float:
            """

            return self.available() * self.price

        def __cmp__(self, other):
            if self.side == Order.BUY:
                return cmp(self.price, other.price)
            else:
                return cmp(other.price, self.price)

    def __init__(self, asks={}, bids={}):
        """Creates an OrderBook object.

        :param asks:
        :type asks:
        :param bids:
        :type bids:
        """

        self._order_list = []
        self._order_manager = OrderManager()
        self.set_book(asks, bids)


    def set_book(self, asks, bids):
        """Sets the book to match market depth data.

        Creates entries with one order at an early time, with the amount of the order equal to the given market depth
        data at that price.

        :param asks:
        :type asks:
        :param bids:
        :type bids:
        """

        self._order_manager._clear()
        self._asks = {}
        self._bids = {}
        for key in asks.keys():
            order = Order(Order.LIMIT, Order.SELL, key, asks[key])
            self.add_order(order)
        for key in bids.keys():
            order = Order(Order.LIMIT, Order.BUY, key, bids[key])
            self.add_order(order)

    def add_order(self, order):
        """Adds an order to the order book.

        Description

        :param order:
        :type order:
        """

        if order.order_type == Order.LIMIT:
            if (order.side == Order.BUY and order.price > min([1000000000]+self._asks.keys())) \
                    or (order.side == Order.SELL and order.price < max([0]+self._bids.keys())):
                return self._add_market(order)
            else:
                return self._add_limit(order)
        elif order.order_type == Order.MARKET:
            return self._add_market(order)

    def _add_limit(self, order):
        """Adds an order to an entry.

        :param order:
        :type order:
        """

        self._order_manager.add_order(order)
        side = self._get_side(order.side)

        if not order.price in side:
            side[order.price] = OrderBook.Entry(order.price, order.side)
        side[order.price].add_order(order)

        return 0, order, []

    def _add_market(self, order):
        """Executes an order against the order book and returns the fills.

        Description

        :param order:
        :type order:
        """

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
        """Removes the order from the order book.

        :param order:
        :type order:
        """

        if not isinstance(order, Order):
            order = self._order_manager.get_order(order)
        if order.active:
            side = self._get_side(order.side)
            side[order.price].cancel_order(order.order_id)
            self._order_manager.remove_order(order.order_id)
            self._clean_entries()

    def add_fill(self, fill):
        """Adds a fill to the order book

        (Useful if the order flow contains fills instead of market orders)

        :param fill:
        :type fill:
        """

        side = self._get_side(fill.side)
        side[fill.price].add_fill(fill)
        return fill

    def find_order(self, order_type, side, price, amount):
        """Finds an order in the book's order manager.

        :param order_type:
        :type order_type:
        :param side:
        :type side:
        :param price:
        :type price:
        :param amount:
        :type amount:
        """

        return self._order_manager.find_order(order_type, side, price, amount)

    def get_level(self, order_side, idx):
        """Returns the market depth entry on the respective side, "idx" positions away from the top of the book.

        :param order_side:
        :type order_side:
        :param idx: 1-indexed
        :type idx:
        :returns: Entry
        """

        if idx == 0:
            return None
        side = self._get_side(order_side)
        keys = sorted(side.keys(),reverse = self._get_side_sort_reverse(order_side))
        return side[keys[idx-1]]


    def _clean_entries(self):
        """Removes empty entries."""

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

    def _get_side_op(self, side, reverse=False):
        if side == Order.BUY ^ reverse:
            return max
        elif side == Order.SELL ^ reverse:
            return min

    def _get_side_sort_reverse(self, side):
        if side == Order.BUY:
            return True
        elif side == Order.SELL:
            return False