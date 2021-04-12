import random
import sys
import threading
import requests
import re
import html
import bs4
import time
import json
from datetime import datetime
from prometheus_client import start_http_server, Gauge


stock = Gauge('stockchecker_stock', 'Stock', ['source', 'type'])
timestamps = Gauge('stockchecker_timestamp', 'Timestamp', ['source', 'operation'])

intercheckperiod = 60
errorsleepperiod = 5
interrequestdelay = 5
testchance = 2  #Use anything over 1 for 100% capture


def getimagebytes(url):
    image = requests.request("GET", url).content
    return image


def pushfoundnotification(title, message, resulturl, imageurl):
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": "***",
        "user": "***",  # Notification List
        "title": title,
        "message": message,
        "url": resulturl,
        "url_title": "Direct Link"
    }
    files = {
        "attachment": ("product.jpg", getimagebytes(imageurl), "image/jpeg")
    }

    headers = {'user-agent': 'Mozilla/5.0'}
    requests.request("POST", url, headers=headers, data=payload, files=files)


# region SaksFifthAvenue


def saksfifthavenuepushfoundnotification(productlist):
    for currentproduct in productlist:
        pid = currentproduct[0]
        orignalprice = currentproduct[1]
        price = currentproduct[2]
        atmcode = currentproduct[3]
        brandname = currentproduct[4]
        productname = currentproduct[5]
        title = productname + " $" + price
        imageurl = buildsaksfifthavenueimageurl(pid)
        producturl = buildsaksfifthavenueproducturl(pid)

        pushfoundnotification(title=title, message="SaksFifthAvenue In Stock Alert", resulturl=producturl, imageurl=imageurl)


def buildsaksfifthavenueimageurl(pid):
    return "https://image.s5a.com/is/image/saks/" + pid + "/"


def buildsaksfifthavenueproducturl(pid):
    return "https://www.saksfifthavenue.com/product/" + pid + ".html"


def buildsaksfifthavenueurl(searchstring, start, size):
    print(str(datetime.now()) + " - Building SaksFifthAvenue URL for searchstring=" + searchstring + ", start=" + str(start) + ", size=" + str(size))
    time.sleep(interrequestdelay)
    return "https://www.saksfifthavenue.com/on/demandware.store/Sites-SaksFifthAvenue-Site/en_US/Search-UpdateGrid?q=" + searchstring + "&start=" + str(start) + "&sz=" + str(size)


def saksfifthavenue(searchstring):

    size = 20
    payload = {}
    headers = {'user-agent': 'Mozilla/5.0'}
    regexstring = "<input type=\"hidden\" class=\"tileproduct-detail\" data-pid=\"(?P<pid>.*?)\">\\n<input type=\"hidden\" class=\"tileproduct-orignalprice\" data-orignalprice=\"(?P<originalprice>.*?)\">\\n<input type=\"hidden\" class=\"tileproduct-price\" data-price=\"(?P<price>.*?)\">\\n<input type=\"hidden\" class=\"tileproduct-atm-code\" data-atm-code=\"(?P<atmcode>.*?)\">\\n<input type=\"hidden\" class=\"tileproduct-brandname\" data-brandname=\"(?P<brandname>.*?)\">\\n<input type=\"hidden\" class=\"tileproduct-name\" data-product-name=\"(?P<productname>.*?)\">"
    productcatalog = {}
    previousinstockpidsset = set()
    firstrun = True

    while True:
        try:
            matches = []
            start = 0
            currentinstockpidsset = set()
            currentinstockpidslist = []

            timestamps.labels(source='saksfifthavenue', operation='start').set(time.time())

            while len(matches) > 0 or start == 0:
                url = buildsaksfifthavenueurl(searchstring, start, size)
                response = requests.request("GET", url, headers=headers, data=payload)
                matches = re.findall(regexstring, response.text)
                for currentmatch in matches:
                    if random.random() <= testchance:
                        pid = currentmatch[0]
                        productcatalog[pid] = currentmatch
                        currentinstockpidslist.append(pid)

                start = start + size

            currentinstockpidsset = set(currentinstockpidslist)

            if firstrun:
                firstrun = False
            else:
                newinstockpids = currentinstockpidsset - previousinstockpidsset
                newoutofstockpids = previousinstockpidsset - currentinstockpidsset
                newinstockproducts = [productcatalog.get(pid) for pid in newinstockpids]

                stock.labels(source='saksfifthavenue', type='current').set(len(currentinstockpidsset))
                stock.labels(source='saksfifthavenue', type='added').set(len(newinstockpids))
                stock.labels(source='saksfifthavenue', type='removed').set(len(newoutofstockpids))

                saksfifthavenuepushfoundnotification(newinstockproducts)

            previousinstockpidsset = currentinstockpidsset
            timestamps.labels(source='saksfifthavenue', operation='end').set(time.time())
            time.sleep(intercheckperiod)
        except:
            timestamps.labels(source='saksfifthavenue', operation='error').set(time.time())
            print('Error While Processing')
            print(sys.exc_info())
            time.sleep(errorsleepperiod)


# endregion


# region Posh Peanut


def poshpeanutpushfoundnotification(productlist):
    for currentproduct in productlist:
        pid = currentproduct["id"]
        price = int(currentproduct["price"]) / 100
        title = currentproduct["title"] + " $" + str(int(price))
        imageurl = "https:" + currentproduct["featured_image"]
        resulturl = "https://poshpeanut.com/products/" + currentproduct["handle"] + "/"

        pushfoundnotification(title=title, message="Posh Peanut In Stock Alert", resulturl=resulturl, imageurl=imageurl)


def buildposhpeanuteurl(searchstring, page):
    print(str(datetime.now()) + " - Building Post Peanut URL for searchstring=" + searchstring + ", page=" + str(page))
    time.sleep(interrequestdelay)
    return "https://poshpeanut.com/search?page=" + str(page) + "&q=" + searchstring + "&type=product"


def poshpeanut(searchstring):

    page = 1
    payload = {}
    headers = {'user-agent': 'Mozilla/5.0'}
    regexstring = "<script type=\"application\\/json\" data-product-json>(?P<atmcode>[\\s|\\S]*?)<\\/script>"
    productcatalog = {}
    previousinstockpidsset = set()
    firstrun = True

    while True:
        try:
            matches = []
            page = 1
            currentinstockpidsset = set()
            currentinstockpidslist = []

            timestamps.labels(source='poshpeanut', operation='start').set(time.time())

            while len(matches) > 0 or page == 1:
                url = buildposhpeanuteurl(searchstring, page)
                response = requests.request("GET", url, headers=headers, data=payload)
                matches = re.findall(regexstring, response.text)
                for currentmatch in matches:
                    if random.random() <= testchance:
                        currentproduct = json.loads(currentmatch)["product"]
                        pid = currentproduct["id"]
                        productcatalog[pid] = currentproduct
                        currentinstockpidslist.append(pid)

                page = page + 1

            currentinstockpidsset = set(currentinstockpidslist)

            if firstrun:
                firstrun = False
            else:
                newinstockpids = currentinstockpidsset - previousinstockpidsset
                newoutofstockpids = previousinstockpidsset - currentinstockpidsset
                newinstockproducts = [productcatalog.get(pid) for pid in newinstockpids]

                stock.labels(source='poshpeanut', type='current').set(len(currentinstockpidsset))
                stock.labels(source='poshpeanut', type='added').set(len(newinstockpids))
                stock.labels(source='poshpeanut', type='removed').set(len(newoutofstockpids))

                poshpeanutpushfoundnotification(newinstockproducts)

            previousinstockpidsset = currentinstockpidsset
            timestamps.labels(source='poshpeanut', operation='end').set(time.time())
            time.sleep(intercheckperiod)
        except:
            timestamps.labels(source='poshpeanut', operation='error').set(time.time())
            print('Error While Processing')
            print(sys.exc_info())
            time.sleep(errorsleepperiod)


# endregion


start_http_server(8000)
threading.Thread(target=saksfifthavenue, args=("posh%20peanut",)).start()
threading.Thread(target=poshpeanut, args=("*",)).start()

while True:
    time.sleep(1)

