__author__ = 'alberts00'
import requests
from bs4 import BeautifulSoup as bs
import time
import numpy as np
import re
import pandas as pd
import os
import inspect


launchpath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + "/"


os.environ['TZ'] = 'Europe/Riga'
time.tzset()


def loadcsv(filename):
    return np.genfromtxt(launchpath+filename, delimiter=',', dtype=str)

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
    return soup.find("user_days_spent_watching").text

def writetofile(data, filename):
    data = np.array(sorted(data, key=lambda x: x[3], reverse=True))
    data = data[data[:, 3] != "None"]
    df = pd.DataFrame(data)
    html = df.to_html(index=False, header=False)
    lastupdated = "<p>Last updated: " + time.strftime("%Y-%m-%d %H:%M") + "</p><\\br>"
    pievienomani = "<p>Ja vēlies, lai tevi pievieno tabulai raksti iekš: https://exs.lv/anime/forum/2metr</p>"

    html += lastupdated + pievienomani
    soup = bs(html)
    soup.table['class'] = soup.table('class', []) + ['table']
    f = open(launchpath + filename, "w")
    f.write(str(soup.prettify()))



data = loadcsv("data.csv")

for i in range(1, len(data)):
    print(data[i][1])
    username = re.search("(animelist|profile)\/(.*)", data[i][1]).group(2)
    data[i][1] = "http://myanimelist.net/profile/"+username
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

anime = [["" for i in range(5)] for j in range(len(data))]
manga = [["" for i in range(5)] for j in range(len(data))]

for i in range(0, len(data)):
    anime[i][0] = data[i][0]
    anime[i][1] = data[i][1]
    anime[i][2] = data[i][2]
    anime[i][3] = data[i][3]
    anime[i][4] = data[i][4]
    manga[i][0] = data[i][0]
    manga[i][1] = data[i][1]
    manga[i][2] = data[i][5]
    manga[i][3] = data[i][6]
    manga[i][4] = data[i][7]

writetofile(data, "out.html")
writetofile(anime, "anime.html")
writetofile(manga, "manga.html")




