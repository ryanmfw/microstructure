from microstructure.orderbook import OrderBook
from microstructure.algorithm import BaseAlgorithm
from microstructure.manager import Manager
from microstructure.storage import PrintStorage, DataFrameStorage
import json
import matplotlib.pyplot as plt

manager = Manager()

class Spread(BaseAlgorithm):
    def step(self, book, fills):
        return {"spread":min(book._asks.keys())-max(book._bids.keys())}


book = OrderBook()
manager.add_algo(Spread())

manager.add_storage(PrintStorage())

store = DataFrameStorage()
manager.add_storage(store)

f = open("data.json")

for line in f.readlines():
    time, value = json.loads(line)
    try:
        bid_list = value["Bids"]
        bids = {}
        for entry in bid_list:
            bids[entry[0]] = entry[1]
        ask_list = value["Asks"]
        asks = {}
        for entry in ask_list:
            asks[entry[0]] = entry[1]

        book.set_book(asks, bids)
        manager.step(time, book)
    except:
        print time


plt.figure()
store.get_entries().plot()
plt.legend(loc='best')
plt.show()
