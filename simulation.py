import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd, pandas.io.sql as psql
import json, datetime, atexit, time
import statistics as stats

""" Simulation accounts that keep track of money and shares during investment algorithm simulations """
class SimAccount:

    def __init__(self, price_data, money0, shares0):
        self.commission_fee = 0
        self.price_data = price_data
        self.money = money0
        self.shares = shares0
        # buy and sell trackers
        self.buy_prices = []
        self.buy_sizes = []
        self.buy_idxs = []
        self.sell_prices = []
        self.sell_sizes = []
        self.sell_idxs = []
        # total value trackers
        self.total_val = []
        self.avg_total_val = []
        self.val_idxs = []

    # execute buy
    def exec_buy(self, price, num_shares, idx):
        trade_money = price * num_shares
        # prevents account money from going negative
        if (self.money >= trade_money):
            # update money and shares
            self.money = self.money - trade_money - self.commission_fee
            self.shares = self.shares + num_shares
            # track trade
            self.buy_prices.append(price)
            self.buy_idxs.append(idx)
            self.buy_sizes.append(num_shares)

    # execute sell
    def exec_sell(self, price, num_shares, idx):
        # prevents account shares from going negative
        if (self.shares >= num_shares):
            # update money and shares
            trade_money = price * num_shares
            self.money = self.money + trade_money - self.commission_fee
            self.shares = self.shares - num_shares
            # track trade
            self.sell_prices.append(price)
            self.sell_idxs.append(idx)
            self.sell_sizes.append(num_shares)

    def track_value(self, price, idx):
        self.total_val.append(self.money + self.shares * price)
        self.avg_total_val.append(sum(self.total_val) / len(self.total_val))
        self.val_idxs.append(idx)


""" Average Crossover Investment Algorithm """
class AverageCrossover:

    def __init__(self, price_data, length_long_avg, length_short_avg):
        # initialize simulation account
        self.account = SimAccount(price_data, price_data[0]*1000, 0)
        # start point index of long average
        self.lavg_idx0 = 0
        # start point index of short average
        self.savg_idx0 = length_long_avg - length_short_avg
        # starting point of iterations
        self.start_idx = length_long_avg
        # long and short moving averages
        self.long_avg = stats.mean(price_data[self.lavg_idx0:length_long_avg])
        self.short_avg = stats.mean(price_data[self.savg_idx0:length_long_avg])
        # crossover boolean
        if (self.short_avg > self.long_avg):
            self.short_above_long = True
        else:
            self.short_above_long = False

    def run_sim(self):

        for curr_idx in range(self.start_idx, len(self.account.price_data)):
            # update start point indices
            self.lavg_idx0 = self.lavg_idx0 + 1
            self.savg_idx0 = self.savg_idx0 + 1
            # update moving averages
            long_avg = stats.mean(self.account.price_data[self.lavg_idx0:curr_idx+1])
            short_avg = stats.mean(self.account.price_data[self.savg_idx0:curr_idx+1])

            # short m.avg has crossed below long m.avg, execute buy
            if (self.short_above_long and short_avg < long_avg):
                self.short_above_long = False
                self.account.exec_buy(self.account.price_data[curr_idx], 100, curr_idx)
            # short m.avg has crossed above long m.avg, execute sell
            elif (not self.short_above_long and short_avg > long_avg):
                self.short_above_long = True
                self.account.exec_sell(self.account.price_data[curr_idx], 100, curr_idx)

            # track total value of self.account
            self.account.track_value(self.account.price_data[curr_idx], curr_idx)

        return self.account
