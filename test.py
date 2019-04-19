from flask import Flask, jsonify, render_template, request, Response, session
from us_treasury_scrap import web_scrap_treasury
import json, datetime, atexit, time
import pandas as pd, pandas.io.sql as psql
import numpy as np
import matplotlib.pyplot as plt
app = Flask(__name__, template_folder='templates')
app.secret_key = '99qVu2YPjy5ss0Z66Igj'

# get mySQL into flask app
from flask_sqlalchemy import SQLAlchemy
#Get stock data API
from alpha_vantage.timeseries import TimeSeries     #If something goes wrong with stock data stuff, it's here


#Note: On the actual webserver, will need to CREATE USER with full privileges
# After creating the user, then create database
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://cs411proj:Password_123@localhost/stock_data" #change to mySQL later
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


connection = db.engine.connect()
query = 'SELECT day, open_, high, low, close FROM Daily WHERE stock_name=\"CY\";'
data = connection.execute(query)

df = pd.DataFrame(data.fetchall())
df.columns = data.keys()


# subsets pandas series rows[0:4]
print(df['low'][0:5])
print(df['low'])

print(df['low'][0:5].mean())
