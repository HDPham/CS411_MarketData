from flask import Flask, jsonify, render_template, request, Response, session
import json, datetime, atexit
import pandas as pd, pandas.io.sql as psql
import numpy as np
from datetime import date, datetime, timedelta
from threading import Timer
import random

app = Flask(__name__, template_folder='templates')
app.secret_key = '99qVu2YPjy5ss0Z66Igj'

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
#Get stock data API
from alpha_vantage.timeseries import TimeSeries

#Note: On the actual webserver, will need to CREATE USER with full privileges
# After creating the user, then create database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://cs411proj:Password_123@localhost/stock_data" #change to mySQL later
##### NOT SURE IF I NEED THIS #####
#####app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##### NOT SURE IF I NEED THESE #####
#####metadata = db.metadata

#####Session = db.create_session(options={'bind':'dest_db_con'})
#####sql_session = Session()

# connection variable provides bridge between Python and SQL
connection = db.engine.connect()


# Keeps track of market holidays (i.e.: days that the markets are closed).
# For use in the trading_day() function.
class Holidays:

    holidays = [date(2019, 1, 1),           # New Year Day
                date(2019, 1, 21),          # MLK Day - 3rd Monday of Jan
                date(2019, 2, 18),          # Presidents Day - 3rd Monday of Feb
                date(2019, 4, 19),          # Good Friday - This one is confusing, may have to be updated manually
                date(2019, 5, 27),          # Memorial Day - Last Monday of May
                date(2019, 7, 4),           # 4th of July
                date(2019, 9, 2),           # Labor Day - 1st Monday of Sept
                date(2019, 10, 28),         # Thanksgiving - 4th Thursday of Nov
                date(2019, 12, 25)]         # Christmas

    # Recompute holidays (at beginning of year)
    @classmethod
    def compute_holidays(cls, year):
        # Reinitialize holidays
        cls.holidays = [date(year, 1, 1)]
        # Calculate date of MLK Day and append
        if (date(year, 1, 1).weekday() == 0):
            cls.holidays.append(date(year, 1, 15))
        else:
            day = 1 + (7 - date(year, 1, 1).weekday()) + 14
            cls.holidays.append(date(year, 1, day))
        # Calculate date of Presidents Day and append
        if (date(year, 2, 1).weekday() == 0):
            cls.holiday.append(date(year, 2, 15))
        else:
            day = 1 + (7 - date(year, 2, 1).weekday()) + 14
            cls.holidays.append(date(year, 2, day))
        # GOOD FRIDAY MISSING
        # Calculate date of Memorial Day and append
        day = 31 - date(year, 5, 31).weekday()
        cls.holidays.append(date(year, 5, day))
        # Append 4th of July
        cls.holidays.append(date(year, 7, 4))
        # Calculate date of Labor Day and append
        if (date(year, 9, 1).weekday() == 0):
            cls.holidays.append(date(year, 9, 1))
        else:
            day = 1 + (7 - date(year, 9, 1).weekday())
            cls.holidays.append(date(year, 9, day))
        # Calculate date of Thanksgiving and append
        if (date(year, 11, 1).weekday() <= 3):
            day = 25 - date(year, 11, 1).weekday()
            cls.holidays.append(date(year, 11, day))
        else:
            day = 32 - date(year, 11, 1).weekday()
            cls.holidays.append(date(year, 11, day))
        # Append Christmas
        cls.holidays.append(date(year, 12, 25))


# Outputs True or False based on whether the markets are open on the current day
def trading_day():
    # Obtain today's date
    today = date.today()
    # If today is the first day of the year, compute all market holidays for the year
    if (today.month == 1 and today.day == 1):
        Holidays.compute_holidays(today.year)
    # Obtain today's weekday
    weekday = today.weekday()
    # Outputs False if today is a Saturday or a Sunday
    if (weekday == 5 or weekday == 6):
        return False
    # Outputs False if today is a market holiday
    elif (today in Holidays.holidays):
        return False
    else:
        return True

# Retrieves data from alpha_vantage and inserts stock data that hasn't already been inserted.
# Assumes that all stocks are updated on the same day (via the last_update class variable).
# Robust function that will work for both daily updates or weekly updates.
def insert_stock_data(stock_name, av_key):
    ts = TimeSeries(key=av_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stock_name, interval='1min', outputsize='full')
    """
    maybe put a try catch at this point in case there's an AV failure?
    """
    # date + time data sorted low to high (oldest to newest)
    time_data = data.index

    row = 0
    insertion_row = False
    while (not insertion_row):
        date, time = time_data[row].split(' ')
        row_year, row_month, row_day = date.split('-')
        # Greater year than the last update implies the row is not in the DB
        if (int(row_year) > last_update.year):
            insertion_row = True
        # Greater month than the last update implies the row is not in the DB
        elif (int(row_month) > last_update.month):
            insertion_row = True
        # Greater day than the last update implies the row is not in the DB
        elif (int(row_day) > last_update.day):
            insertion_row = True
        else:
            row = row + 1
            # in the case that all tuples have already been inserted, prevents infinite loop
            if (row == len(data)):
                break
    # iterate through remaining rows, insert data into DB
    for (i in range(row:len(data))):
        connection.execute("INSERT INTO time(datetime, open, high, low, close, volume, stock_name)" + "VALUES (\"" + time_data[i] + "\", \"" + data['1. open'][i] + "\", \"" + data['2. high'][i] + "\", \"" + data['3. low'][i] + "\", \"" + data['4. close'][i] + "\", \"" + data['5. volume'][i] + "\", \"" + stock_name + "\");")
        ### MIGHT NEED TRY CATCH FOR DUPLICATE INSERTION ERROR


### NEED TO POPULATE WITH FULL LIST OF STOCKS
stock_list = ['cy', 'aapl', 'goog']

def collect_data(list_idx):
    # Update DB with intraday stock data
    insert_stock_data(stock_list[list_idx], 'IK798ICZ6BMU2EZM')

    list_idx = list_idx + 1
    # if there are still stocks to be scraped
    if (list_idx != len(stock_list)):
        # Seconds for timer; must be so that there are 5 or less calls per minute per AV key
        # A little randomized in case AV doesn't like that automated scraping is taking place
        secs = 12 + random.random() * 2
        # Initialize timer
        t = Timer(secs, collect_data, args=[list_idx])
        t.start()


# daily_timer:
"""
* ISSUES:   - Time zones? (just bc it executes at the right time in Urbana, IL, doesn't mean it'll execute at the right time on a server in California)
            X- Account for leap year
            X- Time shifting between function calls? (might be off by a couple seconds between calls, but this will propagate over time, need a way to execute at the same time every day)
            X- Daylight savings?
"""
def daily_timer():
    # set datetime of next daily_timer() execution
    now = datetime.today()
    delta_t = timedelta(days=1)
    next_daily_timer = now + delta_t
    next_daily_timer = next_daily_timer.replace(hour=17, minute=5, second=0, microsecond=0)   # reset next_daily_timer datetime to be exactly at 5:05pm
    # set timer for next daily_timer() execution
    now = datetime.today()
    delta_t = next_daily_timer - now
    secs = delta_t.seconds + 1
    t = Timer(secs, daily_timer)
    t.start()

    if (trading_day()):
        # class variable that keeps track of when the last update was (this is definitely in the wrong spot, it's just pseudocode for now)
        last_update = date.today()
        collect_data(0)
