import pandas as pd
from microstructure.orderbook import Order, OrderBook

class Manager(object):
    def __init__(self):
        self._algos = []
        self._storage = []

    def _get_columns(self):
        cols = []
        #for algo in self._algos:
        #    cols += algo.columns
        return cols

    def add_algo(self, algo):
        self._algos.append(algo)
        #for store in self._storage:
        #    store.set_columns(self._get_columns())

        #TODO: Add dependency tree

    def add_storage(self, storage):
        #storage.set_columns(self._get_columns())
        self._storage.append(storage)

    def step(self, time, book, fills = []):
        results = {}
        for algo in self._algos:
            result = algo.step(book, fills)
            for key, value in result.iteritems():

                results[key] = value
        for storage in self._storage:
            storage.add_entry(time, results)
        return results
