===========
MicroStructure
===========

MicroStructure is a module that, through the use of pandas, allows for the easy analysis of market microstructure.
It imports and steps through order data, reconstructs the order book, and then runs package and user supplied algorithms on the data,
producing pandas DataFrames containing the results at tick-resolution.

This is primarily a vessel for implementing the algorithms discussed in the literature on market microstructure. I hope to add algorithms as time goes on.

Typical usage::
    import microstructure as ms

    class Spread(ms.BaseAlgorithm):
        def step(self, order, book):
            return {"spread":min(book._asks.keys())-max(book._bids.keys())}

    book_data = import_data()

    manager = ms.Manager()
    manager.add_algo(Spread())

    store = ms.DataFrameStorage()
    manager.add_storage(store)

    for data in book_data:
        book.set_book(data['asks'], data['bids'])

        manager.step(data['timestamp'], book)

    import matplotlib.pyplot as plt
    store.get_entries().plot()
    plt.show()

TODO
=========
*Documentation, docstrings
*Add tests
*Add algorithms

License
=========
Copyright (c) 2013 Ryan Wendt <ryan@ryanwendt.com>

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

   1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.

   2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.

   3. This notice may not be removed or altered from any source
   distribution.