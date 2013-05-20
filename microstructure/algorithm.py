from orderbook import Order

class BaseAlgorithm(object):
    def __init__(self, *args, **kwargs):
        pass

    def step(self, book, fills):
        return {}

class CaoHanschWangAlgorithm(BaseAlgorithm):
    def mid(self, book):
        return (book.get_level(Order.SELL, 1).price + book.get_level(Order.BUY, 1).price)/2.0

    def height(self, side, book, idx):
        if idx == 1:
            price_1 = self.mid(book)
        else:
            price_1 = book.get_level(side, idx-1).price
        price_2 = book.get_level(side, idx).price
        return (price_2 - price_1)/self._normalize(side, book)

    def length(self, side, book, idx):
        level = book.get_level(side, idx)
        return level.available()

    def weighted_price(self, book, n1, n2):
        numerator = 0
        for side in [Order.BUY, Order.SELL]:
            numerator += sum([self.length(side, book, j)*book.get_level(side, j).price for j in range(n1,n2+1)])
        denominator = 0
        for side in [Order.BUY, Order.SELL]:
            denominator += sum([self.length(side, book, j) for j in range(n1,n2+1)])
        return numerator/denominator

    def length_imbalance(self, book, idx):
        supply = book.get_level(Order.SELL, idx).available()
        demand = book.get_level(Order.BUY, idx).available
        return (supply-demand)/float(supply+demand)

    def height_imbalance(self, book, idx):
        supply_price_diff = book.get_level(Order.SELL, idx).price - book.get_level(Order.SELL, idx-1).price
        demand_price_diff = book.get_level(Order.BUY, idx).price - book.get_level(Order.BUY, idx-1).price
        return (supply_price_diff - demand_price_diff)/float(supply_price_diff+demand_price_diff)

    def _normalize(self, side, book):
        return book.get_level(side, 10).price - self.mid(book)

    def step(self, book, fills):
        results = {}
        results["mid"] = self.mid(book)
        for side, name in zip([Order.BUY, Order.SELL], ["buy","sell"]):
            for i in range(1,4):
                key = "height_"+name+"_"+str(i)
                results[key] = self.height(side, book, i)

                key = "length_"+name+"_"+str(i)
                results[key] = self.length(side, book, i)



        results["WP2-10"] = self.weighted_price(book, 2, 10)
        return results