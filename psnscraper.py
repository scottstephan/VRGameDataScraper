from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
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
    
    def removeNonAscii(self):
        self.name = sh.cleanAscii(self.name)
        self.developer = sh.cleanAscii(self.developer)
        self.releasedate = sh.cleanAscii(self.releasedate)
        self.price = sh.cleanAscii(self.price)
        self.requirements = sh.cleanAscii(self.requirements)
        
    def encodeStrings(self):
        self.name = self.name.encode('utf-8')
        self.developer = self.developer.encode('utf-8')
        self.releasedate = self.releasedate.encode('utf-8')
        self.price = self.price.encode('utf-8')
        self.requirements = self.requirements.encode('utf-8')
    
def scrape(platform,maxpages,outputto_csv,now,test_mode):
    print("!!!!--- STARTING PSN SCRAPE OF:" + str(maxpages) + " PAGES ---!!!!")

    cpage = 1 #psn pages start with 1, not 0
    psngameurls = []
    psn_url_prefix = "https://store.playstation.com"
    psn_gallerypagedata = [] #the data for the main gallery pages. we scrape the urls from here and then ping each url.
    psn_gamepagedata =[] #the data for each pages inidividual game data
    localDir = "psn_games_html/"

    if test_mode is False:
        for i in range(cpage,maxpages):
            
            URL = "https://store.playstation.com/en-us/grid/STORE-MSF77008-VIRTUALREALITYG/"+str(cpage)

            if test_mode is False:
                localFilename = "psn_gallery_" + str(cpage) + ".html"
                data = sh.makeURLRequest(URL, True,localDir,localFilename,5,0)
                sh.randomsleep()
            
            psn_gallerypagedata.append(data)
            
            print("done getting page# " + str(cpage))
            cpage+=1       
            
#Comb the catalog and get the URLs for the games - Does not run in test_mode
    if test_mode is False:
        for data in psn_gallerypagedata:
            psn_gallerypage = BeautifulSoup(data,'html.parser')
            
            for games in psn_gallerypage.find_all('div', class_='grid-cell grid-cell--game'): #get all of the game cells from the main product page
                gameURL = games.find('a', class_='internal-app-link ember-view').get('href')
                gameURL = psn_url_prefix + gameURL;
                psngameurls.append(gameURL)

#Then visit each game URL individually and grab the page data for each game- In test_mode we just grab the directory contents
    count = 0
    if test_mode is False:
        for g in psngameurls:       
            URL = g
            localFilename ="psn_game_" + str(count) + ".html"
                
            if test_mode is False:
                data = sh.makeURLRequest(URL, True,localDir,localFilename,5,0)
                psn_gamepagedata.append(data)
                sh.randomsleep()
    else:
        psn_gamepagedata = sh.getLocalHTMLCache(localDir)

    count+=1
            
    print("done getting psn game data: " + str(count) + "::" + str(len(psngameurls)))
        
    #Then iterate over that psn_gamepagedata and grab the game info
    allpsndata =[]
    c = 0
    print("Starting scrape of individual game pages. Total game pages: " + str(len(psn_gamepagedata)))
    for g in psn_gamepagedata:
        psn_gamepage = BeautifulSoup(g,'html.parser',from_encoding="utf-8")
        tp = psn_gamedata()

        tp.name = psn_gamepage.find('h2', class_='pdp__title').text
        tp.name = sh.removeExcessCharacters(tp.name)
        print("Scraping " + tp.name + ", " + str(c) + " of " + str(len(psn_gamepagedata)))

        
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
        try:
            tp.numratings = psn_gamepage.find('div', class_='provider-info__rating-count').text
        except:
            tp.numratings = "N/A"
        sh.removeExcessCharacters(tp.numratings)
        sh.removeWhiteSpace(tp.numratings)
        tp.numratings = sh.returnOnlyNumerals(tp.numratings)
        
        if test_mode is False: #psn_gameurls doesnt exist in test mode!
            tp.psnurl=psngameurls[c] #i hate doing stuff like this but I also dont wanna create a new data class and rewrite all of this. 
        else:
            tp.psnurl="TESTMODE"
            
        techspecs = []
        techspecs = psn_gamepage.find_all('div', class_='tech-specs__menu-header')
        try:
            tp.requirements = techspecs[len(techSpecs)-1].text #It's always the last entry....in a collection of headers.....stored as divs. Oh, the humanity!
            sh.removeExcessCharacters(tp.requirements)
        except:
            tp.requirements = "N/A"
        
        tp.computeStarRating()
        allpsndata.append(tp)
        c+=1
        

    for g in allpsndata:
        #g.displayData()
        g.removeNonAscii()
        #g.encodeStrings()
    
    dt = now.strftime("%Y-%m-%d")
    filename = dt + "_PSN_PSVR"
    with open(filename + '.csv', mode='w') as csvfile:
        
        g_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        g_writer.writerow(["Game Name","Release Date","Price","Developer","PSN Stars","NUMBER OF RATINGS","VR Requiredments"]) #header row
        
        for g in allpsndata:
            g_writer.writerow([g.name,g.releasedate,g.price,g.developer, g.starrating_num,g.numratings,g.requirements])
    
        
    print("PSN SCRAPE COMPLETE; CSV LOCATED AT" + filename)
    return allpsndata
##
