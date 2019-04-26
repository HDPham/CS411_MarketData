import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd, pandas.io.sql as psql
import json, datetime, atexit, time

""" Simulation accounts that keep track of money and shares during investment algorithm simulations """
class SimAccount:

    def __init__(self, money0, shares0):
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
            self.money = self.money - trade_money
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
            self.money = self.money + trade_money
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

    """
    INITIALIZE AVERAGE CROSSOVER INVESTMENT SIMULATION
    INPUTS:
        price_data:         price data to run simulation on
        length_long_avg:    number of days for long average
        length_short_avg:   number of days for short average
    """
    def __init__(self, price_data, length_long_avg, length_short_avg):
        # initialize simulation account
        self.account = SimAccount(price_data[0]*1000, 1000)
        self.price_data = price_data
        # start point index of long average
        self.lavg_idx0 = 0
        # start point index of short average
        self.savg_idx0 = length_long_avg - length_short_avg
        # starting point of iterations
        self.start_idx = length_long_avg
        # long and short moving averages
        #self.long_avg = price_data[self.lavg_idx0:length_long_avg].mean()
        #self.short_avg = price_data[self.savg_idx0:length_long_avg].mean()
        self.long_avg = sum(price_data[self.lavg_idx0:length_long_avg]) / len(price_data[self.lavg_idx0:length_long_avg])
        self.short_avg = sum(price_data[self.savg_idx0:length_long_avg]) / len(price_data[self.savg_idx0:length_long_avg])
        # crossover boolean
        if (self.short_avg > self.long_avg):
            self.short_above_long = True
        else:
            self.short_above_long = False

    def run_sim(self):

        for curr_idx in range(self.start_idx, len(self.price_data)):
            # update start point indices
            self.lavg_idx0 = self.lavg_idx0 + 1
            self.savg_idx0 = self.savg_idx0 + 1
            # update moving averages
            long_avg = sum(self.price_data[self.lavg_idx0:curr_idx+1]) / len(self.price_data[self.lavg_idx0:curr_idx+1])
            short_avg = sum(self.price_data[self.savg_idx0:curr_idx+1]) / len(self.price_data[self.savg_idx0:curr_idx+1])

            # short m.avg has crossed below long m.avg, execute buy
            if (self.short_above_long and short_avg < long_avg):
                self.short_above_long = False
                self.account.exec_buy(self.price_data[curr_idx], 10, curr_idx)
            # short m.avg has crossed above long m.avg, execute sell
            elif (not self.short_above_long and short_avg > long_avg):
                self.short_above_long = True
                self.account.exec_sell(self.price_data[curr_idx], 10, curr_idx)

            # track total value of self.account
            self.account.track_value(self.price_data[curr_idx], curr_idx)

        return self.account

""" DUMM Investment Algorithm (discretized) """
class DUMM:

    # number of discrete steps between high_price and 0
    num_incs0 = 100
    """
    INITIALIZE DUMM INVESTMENT SIMULATION
    INPUTS:
        price_data: price data to run simulation on
        bti:        buffer to increment ratio
        gf:         growth function type
                        e: exponential
                        q: quadratic
        qpow:       quadratic power used in quadratic growth functions
        gratio:     growth ratio
    """
    def __init__(self, price_data, bti=2, gf='e', qpow=0, gratio=1):
        # initialize DUMM account
        self.account = SimAccount(price_data[0]*1000, 1000)
        self.price_data = price_data

        self.num_incs0 = DUMM.num_incs0
        self.bti = bti                                      # must be at least 1
        self.inc_size = 0
        self.buf_size = 0
        self.num_incs = self.num_incs0 - self.bti

        self.g_func = GrowthFunction(gf, qpow)
        self.gratio = gratio

        self.high_price = 0
        # cycle reset in the Phase class
        Phase.phase_type = "start"
        Phase.last_price = 0
        Phase.dumm = self

    # computes inc_size, buf_size, sets last_price
    # high_price is the highest price, it determines inc_size of the cycle
    def pre_cycle(self, high_price):
        self.inc_size = high_price / self.num_incs0
        self.buf_size = self.inc_size * self.bti
        Phase.last_price = self.inc_size * self.num_incs

    def run_sim(self):

        for idx in range(0,len(self.price_data)):
            curr_price = self.price_data[idx]
            self.account.track_value(curr_price, idx)

            if (Phase.phase_type == "buy"):
                while (curr_price <= (Phase.last_price - self.inc_size)):
                    Phase.trade(idx)
                if (curr_price >= (Phase.last_price + self.buf_size)):
                    Phase()
                    while ((curr_price >= (Phase.last_price + self.inc_size)) and (Phase.phase_type != "start")):
                        Phase.trade(idx)

            elif (Phase.phase_type == "sell"):
                while ((curr_price >= (Phase.last_price + self.inc_size)) and (Phase.phase_type != "start")):
                    Phase.trade(idx)
                if (curr_price <= (Phase.last_price - self.buf_size)):
                    Phase()
                    while (curr_price <= (Phase.last_price - self.inc_size)):
                        Phase.trade(idx)

            if (Phase.phase_type == "start"):
                # this sets high_price
                if (curr_price > self.high_price):
                    self.high_price = curr_price
                    self.pre_cycle(self.high_price)
                # this is to initialize the first (buy) phase of a cycle
                if (curr_price <= (Phase.last_price - self.buf_size)):
                    Phase()
                    while(curr_price <= (Phase.last_price - self.inc_size)):
                        Phase.trade(idx)

        #print("Money = " + str(self.account.money))
        #print("Shares = " + str(self.account.shares))
        #print("Total Value = " + str(self.account.money + (self.account.shares * self.price_data[len(self.price_data)-1])))

        return self.account


""" DUMM helper class """
class Phase:

    phase_type = "start"
    curr_phase = None

    size_arr = None
    last_price = 0

    dumm = None

    # this function initializes the size_arr for the cycle
    # ASSUMPTIONS:
    #   last_price has already been set
    @classmethod
    def initialize_size_arr(cls):

        length = cls.dumm.num_incs + 1

        cls.size_arr = np.array([0.0] * length)

        x_0 = cls.dumm.g_func.inv(1.0)
        x_n = cls.dumm.g_func.inv(cls.dumm.gratio)
        x_inc_size = (x_n - x_0) / cls.dumm.num_incs

        x_arr = np.array([0.0] * length)
        x_arr[0] = x_0
        cls.size_arr[0] = 1.0
        for i in range(1, length):
            x_arr[i] = x_arr[i-1] + x_inc_size
            cls.size_arr[i] = cls.dumm.g_func.func(x_arr[i])
        cls.size_arr = cls.size_arr[0:(length-1)]

    # ASSUMPTIONS:
    #   money_size_arr has already been computed
    #   phase_type has already been appropriately changed
    #   curr_phase has already been set
    def compute_price_arr(self):
        if (Phase.phase_type == "start"):
            length = Phase.dumm.num_incs
        else:
            length = self.prev_phase.idx
        self.price_arr = np.array([0.0] * length)

        if ((Phase.phase_type == "buy") or (Phase.phase_type == "start")):
            self.price_arr[0] = Phase.last_price - Phase.dumm.buf_size
            for i in range(1, length):
                self.price_arr[i] = self.price_arr[i-1] - Phase.dumm.inc_size

        elif (Phase.phase_type == "sell"):
            self.price_arr[0] = Phase.last_price + Phase.dumm.buf_size
            for i in range(1, length):
                self.price_arr[i] = self.price_arr[i-1] + Phase.dumm.inc_size

    # changes will be made (wrt money vs wrt shares)
    def compute_price_and_size_arrs(self):
        if (Phase.phase_type == "start"):
            self.money_size_arr = Phase.size_arr
        else:
            self.money_size_arr = Phase.size_arr[0:self.prev_phase.idx]
        self.compute_price_arr()
        self.shares_size_arr = self.money_size_arr /  self.price_arr
        return

    # changes will be made (wrt money vs wrt shares)
    def compute_scaling_factor(self):
        if (Phase.phase_type == "start"):
            return Phase.dumm.account.money / np.sum(self.money_size_arr)
        elif (Phase.phase_type == "buy"):
            return self.prev_phase.phase_money / np.sum(self.money_size_arr)
        elif (Phase.phase_type == "sell"):
            return self.prev_phase.phase_shares / np.sum(self.shares_size_arr)

    # ASSUMPTIONS:
    # money_size_arr and shares_size_arr have been computed
    def compute_money_and_shares_arrs(self, s_f):
        self.money_arr = self.money_size_arr * s_f
        self.shares_arr = self.shares_size_arr * s_f
        return

    def __init__(self):

        self.phase_money = 0
        self.phase_shares = 0

        if (Phase.phase_type == "start"):
            self.prev_phase = None
            Phase.curr_phase = self

            Phase.initialize_size_arr()
            self.idx = 0

            self.compute_price_and_size_arrs()
            scaling_factor = self.compute_scaling_factor()
            self.compute_money_and_shares_arrs(scaling_factor)
        else:
            self.prev_phase = Phase.curr_phase
            Phase.curr_phase = self

            if (Phase.phase_type == "buy"):
                Phase.phase_type = "sell"
                self.idx = 0

                self.compute_price_and_size_arrs()
                scaling_factor = self.compute_scaling_factor()
                self.compute_money_and_shares_arrs(scaling_factor)

            elif (Phase.phase_type == "sell"):
                Phase.phase_type = "buy"
                self.idx = 0

                self.compute_price_and_size_arrs()
                scaling_factor = self.compute_scaling_factor()
                self.compute_money_and_shares_arrs(scaling_factor)

    # helper function for the trade() function
    @classmethod
    def end_phase(cls):
        if (cls.curr_phase.prev_phase != None):
            cls.curr_phase.prev_phase.phase_money = cls.curr_phase.prev_phase.phase_money + cls.curr_phase.phase_money
            cls.curr_phase.prev_phase.phase_shares = cls.curr_phase.prev_phase.phase_shares + cls.curr_phase.phase_shares
        cls.curr_phase = cls.curr_phase.prev_phase
        return

    # during a "start" phase, phase_type is not changed to "buy" until the first trade is executed
    @classmethod
    def trade(cls, idx):
        if (cls.phase_type == "start"):
            cls.phase_type = "buy"

        if (cls.phase_type == "buy"):
            trade_money = cls.curr_phase.money_arr[cls.curr_phase.idx]
            cls.curr_phase.phase_money = cls.curr_phase.phase_money - trade_money
            trade_shares = cls.curr_phase.shares_arr[cls.curr_phase.idx]
            cls.curr_phase.phase_shares = cls.curr_phase.phase_shares + trade_shares
            price = cls.curr_phase.price_arr[cls.curr_phase.idx]
            cls.last_price = price
            cls.dumm.account.exec_buy(price, trade_shares, idx)

        elif (Phase.phase_type == "sell"):
            trade_money = cls.curr_phase.money_arr[cls.curr_phase.idx]
            cls.curr_phase.phase_money = cls.curr_phase.phase_money + trade_money
            trade_shares = cls.curr_phase.shares_arr[cls.curr_phase.idx]
            cls.curr_phase.phase_shares = cls.curr_phase.phase_shares - trade_shares
            price = cls.curr_phase.price_arr[cls.curr_phase.idx]
            cls.last_price = price
            cls.dumm.account.exec_sell(price, trade_shares, idx)

        cls.curr_phase.idx = cls.curr_phase.idx + 1

        if (cls.curr_phase.prev_phase != None):
            if (cls.curr_phase.idx == cls.curr_phase.prev_phase.idx):
                cls.end_phase()
                cls.end_phase()
                if (cls.curr_phase == None):
                    cls.phase_type = "start"


""" DUMM helper class """
class GrowthFunction:

# quadratic_function scales wrt growth ratio
#*******************************************************************************
    def quadratic_function(self, x):
        return pow(x, self.quad_power)

    def inverse_quadratic_function(self, y):
        # this is for the constant function
        if (self.quad_power == 0):
            return 1
        return pow(y, (1 / self.quad_power))
#*******************************************************************************

# quadratic_function scales wrt growth ratio and wrt base!!!
#*******************************************************************************
    def exponential_function(self, x):
        return np.exp(x)

    def inverse_exponential_function(self, y):
        return math.log(y)
#*******************************************************************************

    def __init__(self, function_type, quad_power):
        self.quad_power = quad_power
        if (function_type == 'q'):
            if (self.quad_power == 0):
                self.function_name = "constant"
            elif (self.quad_power == 1):
                self.function_name = "linear"
            else:
                self.function_name = "quadratic, power = " + str(self.quad_power)
            self.func = self.quadratic_function
            self.inv = self.inverse_quadratic_function
        elif (function_type == 'e'):
            self.function_name = "exponential"
            self.func = self.exponential_function
            self.inv = self.inverse_exponential_function
