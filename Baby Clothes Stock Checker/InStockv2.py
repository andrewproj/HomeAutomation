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

collections = {
    'amelia earhard': 1,
    'amethyst': 1,
    'aqua floral': 1,
    'ashley': 1,
    'banana cream': 1,
    'bella': 1,
    'black ribbed': 1,
    'black rose': 1,
    'blue rose': 0,
    'bruno': 1,
    'buddy': 1,
    'cadet': 0,
    'cash': 1,
    'cassie': 1,
    'chelsea': 1,
    'chloe': 0,
    'collyns': 1,
    'cotton candy': 1,
    'country rose': 1,
    'crimson': 0,
    'crissy': 1,
    'dusk rose': 1,
    'dusty rose': 1,
    'elizabeth': 1,
    'eloise': 1,
    'erin': 1,
    'evil eye': 1,
    'french gray': 1,
    'frenchie': 1,
    'frida kahlo': 1,
    'fry': 1,
    'hayley': 1,
    'hazel': 1,
    'hydrangea': 0,
    'jax': 1,
    'katherine': 0,
    'keira': 1,
    'lana': 0,
    'leia': 1,
    'lola': 0,
    'lucia': 1,
    'malala yousafzai': 1,
    'mateo': 0,
    'matryoshka': 1,
    'miles': 1,
    'nicholas': 0,
    'nicolette': 1,
    'paola': 1,
    'pink lemonade': 1,
    'pistachio': 1,
    'pretzel': 1,
    'robins egg': 1,
    'rosa parks': 1,
    'rosalyn': 0,
    'rose': 1,
    'rosie the riveters': 1,
    'rowan': 1,
    'ruth bader ginsburg': 1,
    'sailor blue': 1,
    'samara': 1,
    'sashimi': 0,
    'skip': 1,
    'strawberry': 0,
    'sweet pink': 0,
    'tenni': 0,
    'theresa': 1,
    'tommy': 1,
    'valerie': 0,
    'vintage dino': 1,
    'vintage pink rose': 1
}
excludes = [item.casefold() for item in collections.keys() if collections[item] == 0]
querymodifier = ""
for item in excludes:
    querymodifier += "-\"" + item + "\""


def getimagebytes(url):
    image = requests.request("GET", url).content
    return image


def pushfoundnotification(title, message, resulturl, imageurl):
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": "***",
        "user": "***",  # Notification List
        "title": title.replace("amp;", ""),
        "message": message,
        "url": resulturl,
        "url_title": "Direct Link"
    }
    files = {
        "attachment": ("product.jpg", getimagebytes(imageurl), "image/jpeg")
    }

    headers = {'user-agent': 'Mozilla/5.0'}
    requests.request("POST", url, headers=headers, data=payload, files=files)


def excludeitem(producttitle):
    exclude = False
    casefoldproducttitle = producttitle.casefold()

    for item in excludes:
        if item in casefoldproducttitle:
            exclude = True

    return exclude


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
    return "https://www.saksfifthavenue.com/on/demandware.store/Sites-SaksFifthAvenue-Site/en_US/Search-UpdateGrid?q=" + searchstring + querymodifier + "&start=" + str(start) + "&sz=" + str(size)


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
    return "https://poshpeanut.com/search?page=" + str(page) + "&q=" + searchstring + querymodifier + "&type=product"


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
threading.Thread(target=poshpeanut, args=("",)).start()


#saksfifthavenue("posh%20peanut")
#poshpeanut("")


while True:
    time.sleep(1)

