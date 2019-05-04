from lxml import etree
from io import BytesIO
import requests, datetime

def web_scrap_treasury():
    #Get value of today
    now = datetime.datetime.now()
    #Convert today into acceptable datetime string
    date = datetime.date(now.year, now.month, now.day-1).strftime("%Y-%m-%d")
    try:
        page = requests.get('https://data.treasury.gov/feed.svc/DailyTreasuryBillRateData?$filter=month(INDEX_DATE)%20eq%204%20and%20year(INDEX_DATE)%20eq%202019')
    except:
        return 2.38
    tree = etree.parse(BytesIO(page.content))

    root = tree.getroot()
    date_tags = root.findall('.//{http://schemas.microsoft.com/ado/2007/08/dataservices}INDEX_DATE')
    parent_tag = None
    for date_tag in date_tags:
        if date in date_tag.text:
            parent_tag = date_tag.getparent()
    if(parent_tag == None):
        return 2.38
    discount_tag = parent_tag.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}ROUND_B1_CLOSE_4WK_2')
    if(discount_tag == None):
        return 2.38
    return discount_tag.text

if (__name__ == "__main__"):
    web_scrap_treasury()
