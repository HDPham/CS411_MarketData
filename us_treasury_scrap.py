from lxml import etree
from io import BytesIO
import requests, datetime

def web_scrap_treasury():
    #Get value of today
    now = datetime.datetime.now()
    #Convert today into acceptable datetime string
    date = datetime.date(now.year, now.month, now.day-1).strftime("%Y-%m-%d")
    page = requests.get('https://data.treasury.gov/feed.svc/DailyTreasuryBillRateData?$filter=month(INDEX_DATE)%20eq%204%20and%20year(INDEX_DATE)%20eq%202019')
    tree = etree.parse(page.content)
    some_file_like = BytesIO(b"<d:ROUND_B1_CLOSE_4WK_2 m:type=\"Edm.Double\">")
    for event, element in tree.iterparse(some_file_like):
        # print("%s, %4s, %s" % (event, element.tag, element.text))
        continue


if (__name__ == "__main__"):
    web_scrap_treasury()
