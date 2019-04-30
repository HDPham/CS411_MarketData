import random
import numpy as np
from alpha_vantage.timeseries import TimeSeries

class DataGeneration:

    oneA_data = [13,7,11,5,13]

    rb_data = [10, 9, 8, 9, 6.5, 7, 2, 1, 4, 8, 1, 10]

    @classmethod
    def generate_random(cls, start, rand_size, length):
        rand_data = np.array([1.0] * length)
        rand_data[0] = start
        for i in range(1, length):
            rand_data[i] = rand_data[i-1] + random.uniform(-rand_size, rand_size)
            if (rand_data[i] <= 0):
                rand_data[i] = rand_data[i-1]
        return rand_data

    #***************************************************************************
    # git readme: http://introtopython.org/dictionaries.html
    # Alpha Vantage API Key: 3R1Y1E6PX3LY4BCE

    @classmethod
    def get_daily(cls, stock_name):
        ts = TimeSeries(key='3R1Y1E6PX3LY4BCE')
        ohlc_data, meta_data = ts.get_daily(symbol=stock_name, outputsize='full')

        sorted_price_data = np.array([])
        for dict_val in ohlc_data.values():
            sorted_ohlc = np.array([float(dict_val['1. open'])])
            if (float(dict_val['1. open']) > float(dict_val['4. close'])):
                sorted_ohlc = np.append(sorted_ohlc, float(dict_val['2. high']))
                sorted_ohlc = np.append(sorted_ohlc, float(dict_val['3. low']))
            else:
                sorted_ohlc = np.append(sorted_ohlc, float(dict_val['2. high']))
                sorted_ohlc = np.append(sorted_ohlc, float(dict_val['3. low']))
            sorted_ohlc = np.append(sorted_ohlc, float(dict_val['4. close']))
            sorted_price_data = np.append(sorted_ohlc, sorted_price_data)

        return sorted_price_data
