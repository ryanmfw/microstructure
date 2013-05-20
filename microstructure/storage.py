from pandas import DataFrame, Series

class BaseStorage(object):
    def __init__(self):
        self._columns = []

    def get_columns(self):
        return self._columns

    def set_columns(self, columns):
        self._columns = columns

    def add_entry(self, time, results):
        pass

    def get_entries(self, start = None, end = None):
        pass

class PrintStorage(BaseStorage):
    def add_entry(self, time, results):
        print str(time), str(results)

class ListStorage(BaseStorage):
    def __init__(self):
        super(ListStorage, self).__init__()
        self._list = []
        self._index = []

    def add_entry(self, time, results):
        self._list.append(results)
        self._index.append(time)

    def get_entries(self, start = None, end = None):
        series = {}
        for column in self._columns:
            series[column] = []
        for res in self._list:
            for key in res.keys():
                series[key].append(res[key])
            
        return DataFrame(series, index = self._index)

class DataFrameStorage(BaseStorage):
    def __init__(self):
        super(DataFrameStorage, self).__init__()
        self._dataframe = DataFrame()

    # def set_columns(self, columns):
    #     super(BaseStorage, self).set_columns()
    #     if not self._dataframe:
    #         self._dataframe = DataFrame(columns=columns)

    def add_entry(self, time, results):
        dict = {}
        for col, val in results.iteritems():
            dict[col] = Series([val], index=[time])
        df = DataFrame(dict)
        self._dataframe = self._dataframe.append(df)

    def get_entries(self, start = None, end = None):
        return self._dataframe
