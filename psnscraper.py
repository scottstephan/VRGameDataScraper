from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
import numpy as np
import pandas as pd
from decimal import *
import datetime
import scraperHelpers as sh

class psn_gamedata:
    name = ""
    releasedate = ""
    price = ""
    developer = ""
    starrating = ""
    starrating_num = 0
    numratings = ""
    psnurl=""
    requirements = ""
    
    def displayData(self):
        print("-----------")
        print("Title:" + self.name)
        print("Developer: " + self.developer)
        print("release: " + self.releasedate)
        print("price: " + self.price)
        print("starrating: " + str(self.starrating_num))
        print("number of ratings :" + str(self.numratings))
        print("requirements: " + str(self.requirements))
        
        return
    
    def computeStarRating(self):
        wholestars = []
        wholestars = self.starrating.find_all('i', class_="fa-star")
        
        halfstars = []
        halfstars = self.starrating.find_all('i', class_="fa-star-half-o")
        
        self.starrating_num = len(wholestars) + (len(halfstars))* 0.5
        return
        
    
def scrape(platform,maxpages,outputto_csv,now):
    print("!!!!--- STARTING PSN SCRAPE OF:" + str(maxpages) + " PAGES ---!!!!")

    cpage = 1 #psn pages start with 1, not 0
    psngameurls = []
    psn_url_prefix = "https://store.playstation.com"
    psn_gallerypagedata = [] #the data for the main gallery pages. we scrape the urls from here and then ping each url.
    psn_gamepagedata =[] #the data for each pages inidividual game data

    for i in range(cpage,maxpages):
        
        URL = "https://store.playstation.com/en-us/grid/STORE-MSF77008-VIRTUALREALITYG/"+str(cpage)
    
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        request=urllib.request.Request(URL,None,headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        
        psn_gallerypagedata.append(data)
        sh.randomsleep()
        
        print("done getting page# " + str(cpage))
        cpage+=1       

    #Use BeautifulSoup to parse the PSN data. In this case comb the catalog and get the URLs for the games
    for data in psn_gallerypagedata:
        psn_gallerypage = BeautifulSoup(data,'html.parser')
        
        for games in psn_gallerypage.find_all('div', class_='grid-cell grid-cell--game'): #get all of the game cells from the main product page
            gameURL = games.find('a', class_='internal-app-link ember-view').get('href')
            gameURL = psn_url_prefix + gameURL;
            psngameurls.append(gameURL)

    #Then visit each game URL individually and grab the page data for each game
    count = 0

    for g in psngameurls: 
        URL = g
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        request=urllib.request.Request(URL,None,headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        
        psn_gamepagedata.append(data)
        count+=1
        print(URL)
        sh.randomsleep()
        
        print("done getting psn game data: " + str(count) + "::" + str(len(psngameurls)))
        
    #Then iterate over that psn_gamepagedata and grab the game info
    allpsndata =[]
    c = 0
    for g in psn_gamepagedata:
        psn_gamepage = BeautifulSoup(g,'html.parser')
        tp = psn_gamedata()

        tp.name = psn_gamepage.find('h2', class_='pdp__title').text
        sh.removeExcessCharacters(tp.name)
        
#This is the dumbest. There are several h5 classes that contain the info. The first is the title, the second has several spans whic h contain the release date and number of ratings        
        providerInfoWhole = psn_gamepage.find('div', class_='provider-info')
        
        providerInfoRelevant = []
        providerInfoRelevant = providerInfoWhole.find_all('h5',class_='provider-info__text')
        
        tp.developer = providerInfoRelevant[0].text #the first result is always the developer.
        
        pvIRSpans = []
        pvIRSpans = providerInfoRelevant[1].find_all('span',class_='provider-info__list-item') #then we have to get all the spans inside of the SECOND h5 element
            #the 1st result is the prod type, the 2nd is the release date and the 3rd is the star ratings
        tp.releasedate = pvIRSpans[1].text
        tp.releasedate = sh.remove_prefix(tp.releasedate, "Released ")
        sh.removeExcessCharacters(tp.releasedate)
#End of that insanity
        
        tp.price = psn_gamepage.find('h3', class_='price-display__price').text
        sh.removeExcessCharacters(tp.price)

        tp.starrating = psn_gamepage.find('div', class_='star-rating')
#There's some ludicrous white space node in front of the price that somehow eludes all of pythons whitespace detection. I finally added the return numeral function.       
        tp.numratings = psn_gamepage.find('div', class_='provider-info__rating-count').text
        sh.removeExcessCharacters(tp.numratings)
        sh.removeWhiteSpace(tp.numratings)
        tp.numratings = sh.returnOnlyNumerals(tp.numratings)
#End. Phew.
        
        tp.psnurl=psngameurls[c] #i hate doing stuff like this but I also dont wanna create a new data class and rewrite all of this. 
        
        techspecs = []
        techspecs = psn_gamepage.find_all('div', class_='tech-specs__menu-header')
        tp.requirements = techspecs[len(techSpecs)-1].text #It's always the last entry....in a collection of headers.....stored as divs. Oh, the humanity!

        sh.removeExcessCharacters(tp.requirements)
        
        tp.computeStarRating()
        allpsndata.append(tp)
        c+=1
        

    for g in allpsndata:
        g.displayData()
    
    dt = now.strftime("%Y-%m-%d")
    filename = dt + "_PSN_PSVR"
    with open(filename + '.csv', mode='w') as csvfile:
        
        g_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        g_writer.writerow(["Game Name","Release Date","User Score","NUMBER OF RATINGS","VR Required?"]) #header row
        
        for g in allpsndata:
            g_writer.writerow([g.name,g.releasedate, g.starrating_num,g.numratings,g.requirements])
    
        
    print("PSN SCRAPE COMPLETE; CSV LOCATED AT" + filename)
##
