from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__, template_folder='templates')

# get mySQL into flask app
from flask_mysqldb import MySQL
mysql = MySQL(app)


@app.route('/')
@app.route('/home')
def home ():
    return render_template('/home.html')

from flask import request
@app.route('/get_stock', methods=['GET', 'POST'])
def get_stock():
    from alpha_vantage.timeseries import TimeSeries
    from bs4 import BeautifulSoup
    from html.parser import HTMLParser


    stock = request.args.get('stock')
    ts = TimeSeries(key='IK798ICZ6BMU2EZM', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=stock,interval='1min', outputsize='full')
    json_data= data.to_json(orient='split')
    return json_data

@app.route('/scraper', methods=['GET'])
def scraper():
    # cursor object executes mySQL stuff
    cursor = mysql.connection.cursor()
    #cursor.execute is python's way of saying "hey, SQL query ahoy!"
    cursor.execute('CREATE DATABASE Stocks')
    cursor.execute('USE Stocks')

    rv = cursor.fetchall())
