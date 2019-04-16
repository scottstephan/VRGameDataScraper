from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
import numpy as np
import pandas as pd
from decimal import *
import datetime 

################# FUNCTIONS & CLASSES ###########
def removeExcessCharacters(data):
    data = str(data).replace("  ","")
    data = data.strip('\r\n')
    return data

class gamedata:
    name = ""
    releasedate = ""
    metascore = ""
    userscore = ""
    vrrequired = ""
    metauserdelta = 0
    metacriticurl=""
    
    def crunchNumbers(self):
        if self.metascore != "tbd" and self.userscore != "tbd":
            self.metauserdelta = Decimal(self.metascore)/10 - Decimal(self.userscore) #metascores are on a 100 pt scale, user scales are on a 10 pt scale. thanks mc!
            self.metauserdelta.quantize(Decimal('.02'), rounding=ROUND_UP)
        return;
    
    def displayData(self):
        print(self.name)
        print(self.releasedate)
        print(self.metascore)
        print(self.userscore)
        print(self.metauserdelta)
        print(self.vrrequired)
        print(self.metacriticurl)
        return
    
##################################################
now = datetime.datetime.now()

vrgames = [] #used to store gamedata objects
metacritic_maxpage = 2 #the number of pages of results to grab. right now there are only 2, but build to scale! Any additional results beyond the max # wont return relevant data for BSoup

#TO-DO: Refactor a lot of the page data requesting into a class. This gets confusing quick

cpage = 0 #page counter
metacritic_pagedata = [] #its a little sloppy but I'm going to grab the html bytestreams, store them in a list and then iterate over that to more cleanly seperate retrieval from logic

#This stuff below is dumb- I made a data class to avoid this kind of stuff! But I don't know another way to hand off relevant data to PANDAS other than to coallate it by type. useful only for PANDAs stuff, not required for CSV output.
allnames = []
allreleasedates =[]
allmetascores = []
alluserscores = []
allmetauserdeltas = []
allvrrequireds = []
allmetaurls = []

###################################### METACRITIC ##################################
 
#Format the URL with the right header to avoid 403s
for i in range(cpage,metacritic_maxpage):
    URL = "https://www.metacritic.com/browse/games/score/metascore/all/ps4/filtered?hardware=psvr&page="+str(cpage)

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(URL,None,headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    
    metacritic_pagedata.append(data)
    print("done getting page# " + str(cpage))
    cpage+=1
##

#Use BeautifulSoup to parse the Metacritic data
for data in metacritic_pagedata:
    soup = BeautifulSoup(data,'html.parser')

    for games in soup.find_all('li', class_='product game_product'): #get all of the game_product rows that contain the info and iterate over them
 
        title = games.find('div', class_='product_title').find('a').text #find the title
        title = removeExcessCharacters(title)
        allnames.append(title)
        
        metascore = games.find('div',class_='metascore_w').text #get the metascore
        metascore = removeExcessCharacters(metascore)
        allmetascores.append(metascore)
        
        userscore = games.find('span', class_='textscore').text
        userscore = removeExcessCharacters(userscore)
        alluserscores.append(userscore)
        
        releasedate = games.find('li', class_='release_date').find('span', class_='data').text
        releasedate = removeExcessCharacters(releasedate)
        allreleasedates.append(releasedate)
        
        psvrrequired = games.find('li', class_='stat attributes').text
        psvrrequired = removeExcessCharacters(psvrrequired)
        allvrrequireds.append(psvrrequired)
        
        murl = games.find('div', class_="basic_stat product_title").find('a').get('href')
        murl = removeExcessCharacters(murl)
        murl = "https://www.metacritic.com" + murl;
        allmetaurls.append(murl)
        
        #TO-DO: use the murl to query the product page and get the number of critical and user reviews
        
        tgame = gamedata()
        tgame.name = title
        tgame.releasedate = releasedate
        tgame.metascore = metascore
        tgame.userscore = userscore
        tgame.vrrequired = psvrrequired
        tgame.metacriticurl = murl;
        vrgames.append(tgame)
    
##
print("Done parsing data")



#Read back the objects to show we did the right work
for g in vrgames:
    g.crunchNumbers()
    g.displayData()
    allmetauserdeltas.append(g.metauserdelta)
##
    
##Plop it out the Metacritic data into a csv
dt = now.strftime("%Y-%m-%d")
filename = "Metacritic_PSVR_"+dt
with open(filename + '.csv', mode='w') as csvfile:
    
    g_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    g_writer.writerow(["Game Name","Release Date","Metascore","User Score","Meta/User Delta","VR Required?"]) #header row
    
    for g in vrgames:
        g_writer.writerow([g.name,g.releasedate, g.metascore,g.userscore,g.metauserdelta,g.vrrequired])
###################################### END METACRITIC ##################################

        
############################# PSN ##########################################
cpage = 1 #psn pages start with 1, not 0
psngameurls = []
psn_maxpage = 15 #if you go over the page limit then psn returns just the last available page. will need to check for dupes. also, psn urls start at 1, so 14 pages is 15, not 14.
psn_url_prefix = "https://store.playstation.com/en-us/product"
psn_pagedata = [] #i feel like a lot of this common data should be factored into a class and then assigned in a block for readability

for i in range(cpage,psn_maxpage):
    URL = "https://store.playstation.com/en-us/grid/STORE-MSF77008-VIRTUALREALITYG/"+str(cpage)

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(URL,None,headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    
    psn_pagedata.append(data)
    print("done getting page# " + str(cpage))
    cpage+=1       

#Use BeautifulSoup to parse the PSN data
for data in psn_pagedata:
    soup = BeautifulSoup(data,'html.parser')
    
    for games in soup.find_all('div', class_='grid-cell grid-cell--game'): #get all of the game cells from the main product page
        gameURL = games.find('a', class_='internal-app-link ember-view').get('href')
        gameURL = psn_url_prefix + gameURL;
        psngameurls.append(gameURL)
 
for g in psngameurls:
    print(g)
#Then iterate over those URLS and get the data
    
##

###################################### END PSN ##################################

print("all done");
    
    