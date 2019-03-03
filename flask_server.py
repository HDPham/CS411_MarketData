from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__, template_folder='templates')

@app.route('/')
@app.route('/home')
def home ():
    return render_template('/home.html')

@app.route('/scraper', methods=['GET', 'POST'])
def get_stock():
    from alpha_vantage.timeseries import TimeSeries
    from bs4 import BeautifulSoup
    from html.parser import HTMLParser
    import requests

    ts = TimeSeries(key='IK798ICZ6BMU2EZM', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    json_data= data.to_json(orient='split')
    return json_data
