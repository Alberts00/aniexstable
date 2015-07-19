__author__ = 'alberts00'
import requests
from bs4 import BeautifulSoup as bs
import time
import numpy as np
import re
import pandas as pd
import os

os.environ['TZ'] = 'Europe/Riga'
time.tzset()

def loadcsv(filename):
    return np.genfromtxt(filename, delimiter=',', dtype=str)

def getcurrentlywatchinganime(soup):
    animetime = 0
    title = ""
    for anime in soup.find_all('anime'):
        if anime.my_status.text == "1" or anime.my_status.text == "2":
            if animetime < int(anime.my_last_updated.text):
                animetime = int(anime.my_last_updated.text)
                title = anime.series_title.text
    print(time.strftime('%Y-%m-%d %H:%M', time.localtime(animetime)), title)
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(animetime)), title


def getcurrentlywatchingmanga(soup):
    mangatime = 0
    title = ""
    for manga in soup.find_all('manga'):
        if manga.my_status.text == "1" or manga.my_status.text == "2":
            if mangatime < int(manga.my_last_updated.text):
                mangatime = int(manga.my_last_updated.text)
                title = manga.series_title.text
    print(time.strftime('%Y-%m-%d %H:%M', time.localtime(mangatime)), title)
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(mangatime)), title



def getpage(username, type):
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0',
    }
    url = "http://myanimelist.net/malappinfo.php?u="+username+"&status=all&type="+type
    page = requests.get(url, headers=headers)
    soup = bs(page.text)
    if "Incapsula_Resource" in page.text:
        print(url)
        time.sleep(5)
        return getpage(username, type)
    return soup

def getdaysspent(soup):
    return (soup.find("user_days_spent_watching").text)

print()
data = loadcsv("data.csv")
for i in range(1, len(data)):
    print(data[i][1])
    username = re.search("(animelist|profile)\/(.*)", data[i][1]).group(2)
    soup = getpage(username, "anime")
    lastanimeupdated, lastanime = getcurrentlywatchinganime(soup)
    data[i][2] = lastanime
    data[i][3] = lastanimeupdated
    data[i][4] = getdaysspent(soup)
    soup = getpage(username, "manga")
    lastmangaupdated, lastmanga  = getcurrentlywatchingmanga(soup)
    if lastmanga is not "":
        data[i][5] = lastmanga
        data[i][6] = lastmangaupdated
        data[i][7] = getdaysspent(soup)
    else:
        data[i][5] = "None"
        data[i][6] = "None"
        data[i][7] = "None"


#print(data)
data = sorted(data, key=lambda x: x[3], reverse=True)


df = pd.DataFrame(data)
html = df.to_html(index=False, header=False)
lastupdated = "<p>Last updated: " + time.strftime("%Y-%m-%d %H:%M") + "</p>"
html += lastupdated
f = open("out.html", "w")
f.write(html)
