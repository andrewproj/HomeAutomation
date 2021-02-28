import requests
import re
import html
import bs4
import time
from prometheus_client import start_http_server, Gauge


def getimagebytes(url):
    return requests.request("GET", url).content


def pushfoundnotification(title, message, resulturl, imageurl):
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": "XXXXXXX",
        "user": "XXXXXXX",
        "title": title,
        "message": message,
        "url": resulturl,
	"priority": 1,
        "url_title": "Direct Link"
    }
    files = {
        "attachment": ("product.jpg", getimagebytes(imageurl), "image/jpeg")
    }

    headers = {'user-agent': 'Mozilla/5.0'}
    requests.request("POST", url, headers=headers, data=payload, files=files)


def saksfifthavenue(searchstring, title, foundlasttime):

    isfound = False
    url = "https://www.saksfifthavenue.com/search?q=" + searchstring + "&search-button=&lang=en_US"
    payload = {}
    headers = {'user-agent': 'Mozilla/5.0'}
    notfoundstring = "Sorry, we couldn’t find any results"
    producttitleregex = "data-product-name=\"(.*?)\""

    response = requests.request("GET", url, headers=headers, data=payload)
    if not(notfoundstring in response.text):
        if not foundlasttime:
            itemmatch = re.search(producttitleregex, response.text)
            rawitemtitle = itemmatch[1]
            imagematch = re.search("<img.*?src=\"(.*?)\".*?title=\"" + rawitemtitle + "\"", response.text)
            imageurl = imagematch[1]
            message = bs4.BeautifulSoup(html.unescape(rawitemtitle), "html.parser").text
            pushfoundnotification(title="Saks Fifth Avenue:\n" + title, message=message, resulturl=url, imageurl=imageurl)
        isfound = True

    return isfound


def poshpeanut(searchstring, title, foundlasttime):

    isfound = False
    url = "https://poshpeanut.com/search?q=" + searchstring + "&type=product"
    payload = {}
    headers = {'user-agent': 'Mozilla/5.0'}
    notfoundstring = "No results could be found"
    regex = "class=\"ProductItem__Image\".*?src=\"(.*?)\".*?alt=\"(.*?)\""

    response = requests.request("GET", url, headers=headers, data=payload)
    if not(notfoundstring in response.text):
        if not foundlasttime:
            groups = re.search(regex, response.text, flags=re.DOTALL).groups()
            imageurl = "https:" + groups[0]
            message = bs4.BeautifulSoup(html.unescape(groups[1]), "html.parser").text
            pushfoundnotification(title="Posh Peanut:\n" + title, message=message, resulturl=url, imageurl=imageurl)
        isfound = True

    return isfound


start_http_server(8000)
instock = Gauge('instock', 'In Stock', ['tracker'])
foundstatus = [False, False, False, False, False, False, False]

while True:
    try:
        print("Checking @", time.strftime("%H:%M:%S",time.localtime()))

        foundstatus[0] = saksfifthavenue(searchstring="posh+peanut+sophia", title="Saks Sophia", foundlasttime=foundstatus[0])
        instock.labels('SaksSophia').set(int(foundstatus[0]))

        foundstatus[1] = saksfifthavenue(searchstring="posh+peanut+limoncello", title="Saks Limoncello", foundlasttime=foundstatus[1])
        instock.labels('SaksLimoncello').set(int(foundstatus[1]))

        foundstatus[2] = poshpeanut(searchstring="buddy+patoo", title="Posh Peanut Buddy Patoo", foundlasttime=foundstatus[2])
        instock.labels('PoshPeanutBuddyPatoo').set(int(foundstatus[2]))

        foundstatus[3] = poshpeanut(searchstring="olive+patoo", title="Posh Peanut Olive Patoo", foundlasttime=foundstatus[3])
        instock.labels('PoshPeanutOlivePatoo').set(int(foundstatus[3]))

        foundstatus[4] = poshpeanut(searchstring="sophia", title="Posh Peanut Sophia", foundlasttime=foundstatus[4])
        instock.labels('PoshPeanutSophia').set(int(foundstatus[4]))

        foundstatus[5] = poshpeanut(searchstring="buddy+plush", title="Posh Peanut Buddy Plush", foundlasttime=foundstatus[5])
        instock.labels('PoshPeanutBuddyPlush').set(int(foundstatus[5]))

        foundstatus[6] = poshpeanut(searchstring="olive+plush", title="Posh Peanut Olive Plush", foundlasttime=foundstatus[6])
        instock.labels('PoshPeanutOlivePlush').set(int(foundstatus[6]))

        time.sleep(300)
    except:
        print('Error While Processing')
        time.sleep(5)
