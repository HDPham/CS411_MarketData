#! /usr/bin/python
from alpha_vantage.timeseries import TimeSeries
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import requests


# input from user will be symbol
def scrape():
    ts = TimeSeries(key='IK798ICZ6BMU2EZM', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
    print(data)



    page = requests.get("http://dataquestio.github.io/web-scraping-pages/simple.html")
    # print(page.content)
    soup = BeautifulSoup(page.content, 'html.parser')
    print(soup.prettify())





if __name__ == '__main__' :
    print("reached")
    scrape()
