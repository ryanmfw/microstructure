from microstructure.orderbook import OrderBook, OrderManager, Order, Fill
import unittest

#test set_book
#test add_order
#test cancel_order
#test add_fill
#test find_order

#test order_manager
#test Entry



class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        book = OrderBook()

    def test_shuffle(self):
        pass
if __name__ == "__main__":
    unittest.main()