from flask import Flask, jsonify, render_template, request, Response, session
from us_treasury_scrap import web_scrap_treasury
import json, datetime, atexit, time
import pandas as pd, pandas.io.sql as psql
import numpy as np
from scraper import Scrape
from mpl_toolkits.mplot3d import Axes3D
# Axes3D import has side effects, it enables using projection='3d' in add_subplot

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

import random
from simulation import SimAccount, AverageCrossover
import matplotlib.ticker as mtick
from pattern_search import optimize_avg_cross

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
#Get stock data API
from alpha_vantage.timeseries import TimeSeries     #If something goes wrong with stock data stuff, it's here


# Database and connection must be established before any functions are used
class SimCon:
    db = None

def get_data(stock_name):
    connection = SimCon.db.engine.connect()
    query = 'SELECT close FROM daily WHERE stock_name=\"' + stock_name + '\";'
    result = connection.execute(query)
    data = []
    for row in result:
        data.append(row['close'])
    connection.close()
    return data

def exec(data, l, s):
    avgco = AverageCrossover(data, l, s)
    account = avgco.run_sim()
    return account.avg_total_val[len(account.avg_total_val)-1]

# Generates 3D surface of the design space for the Average Crossover algorithm.
def generate_surface(stock_name):

    data = get_data(stock_name)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    lavg = np.arange(100, 500, 20)
    savg = np.arange(18, 98, 4)
    X, Y = np.meshgrid(lavg, savg)
    X = X.flatten()
    Y = Y.flatten()
    Z = np.array([0.0] * len(X))
    print(len(X))
    for i in range(len(X)):
        print(i)
        Z[i] = exec(data, X[i], Y[i])

    ax.plot_trisurf(X, Y, Z)

    ax.set_xlabel('Length Long Average')
    ax.set_ylabel('Length Short Average')
    ax.set_zlabel('Average Total Value Convergence')

    plt.show()


def avgco_simopt(stock_name, lavg_in, savg_in):

    data = get_data(stock_name)

    avgco = AverageCrossover(data, lavg_in, savg_in)
    account1 = avgco.run_sim()

    lavg_opt, savg_opt = optimize_avg_cross(data)
    avgco_opt = AverageCrossover(data, lavg_opt, savg_opt)
    account2 = avgco_opt.run_sim()

    fig, ax = plt.subplots(2, 2, sharex='col', sharey='row', figsize=(8,6))

    ax[0,0].plot(data, 'k-')
    ax[0,0].plot(account1.buy_idxs, account1.buy_prices, 'r.')
    ax[0,0].plot(account1.sell_idxs, account1.sell_prices, 'g.')
    ax[0,0].grid(True, linestyle='-',linewidth=1,alpha=.3)
    ax[0,0].set_title('Input Results')

    ax[1,0].plot(account1.val_idxs, account1.total_val, '#62EF00')
    ax[1,0].plot(account1.val_idxs, account1.avg_total_val, 'g')
    ax[1,0].grid(True, linestyle='-',linewidth=1,alpha=.3)
    ax[1,0].tick_params(axis='y', labelsize=6)

    ax[0,1].plot(data, 'k-')
    ax[0,1].plot(account2.buy_idxs, account2.buy_prices, 'r.')
    ax[0,1].plot(account2.sell_idxs, account2.sell_prices, 'g.')
    ax[0,1].tick_params(reset=True)
    ax[0,1].grid(True, linestyle='-',linewidth=1,alpha=.3)
    ax[0,1].set_title('Optimum Results')

    ax[1,1].plot(account2.val_idxs, account2.total_val, '#62EF00', label='Account Total Value')
    ax[1,1].plot(account2.val_idxs, account2.avg_total_val, 'g', label='Account Average Total Value')
    ax[1,1].tick_params(reset=True, axis='y', labelsize=6)
    ax[1,1].grid(True, linestyle='-',linewidth=1,alpha=.3)
    fmt = '${x:,.0f}'
    tick = mtick.StrMethodFormatter(fmt)
    ax[1,1].yaxis.set_major_formatter(tick)
    ax[1,1].legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), shadow=True, ncol=2, prop={'size': 6})

    plt.savefig('static/simulation.png')
    plt.close()