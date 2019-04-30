from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
from decimal import *
import datetime
import scraperHelpers as sh

class metacritic_gamedata:
    name = ""
    releasedate = ""
    metascore = ""
    userscore = ""
    vrrequired = ""
    metauserdelta = 0
    metacriticurl=""
    num_userreviews = "UNASSIGNED"
    num_criticalreviews = "UNASSIGNED"
    
    def removeNonAscii(self):
        self.name = sh.cleanAscii(self.name)
        self.releasedate = sh.cleanAscii(self.releasedate)
        self.metascore = sh.cleanAscii(self.metascore)
        self.userscore = sh.cleanAscii(self.userscore)
        self.vrrequired = sh.cleanAscii(self.vrrequired)
        
    def encodeStrings(self):
        self.name = self.name.encode('utf-8')
        self.releasedate = self.releasedate.encode('utf-8')
        self.metascore = self.metascore.encode('utf-8')
        self.userscore = self.userscore.encode('utf-8')
        self.vrrequired = self.vrrequired.encode('utf-8')
    
    def crunchNumbers(self):
        if self.metascore != "tbd" and self.userscore != "tbd":
            self.metauserdelta = Decimal(self.metascore)/10 - Decimal(self.userscore) #metascores are on a 100 pt scale, user scales are on a 10 pt scale. thanks mc!
            self.metauserdelta.quantize(Decimal('.02'), rounding=ROUND_UP)
        return;
    
    def displayData(self):
        print(self.name)
        print(self.releasedate)
        print(self.metascore)
        print(str(self.num_criticalreviews))
        print(self.userscore)
        print(str(self.num_userreviews))
        print(self.metauserdelta)
        print(self.vrrequired)
        print(self.metacriticurl)
        return
####
    
#################################################LOGIC###########################################    
def scrape(platform,maxpages,outputto_csv,now,test_mode):

    cpage = 0 #page counter
    metacritic_mainpagedata = [] #all the html data from the mainpages
    metacritic_vrgames = [] #used to store metacritic_gamedata objects

##Scrape the Metacritic main pages for general info- Stores in metacritic_mainpagedata
    
    print("!!!!--- STARTING METACRITIC SCRAPE OF:" + str(maxpages) + " PAGES ---!!!!")
    localDir = "metacritic_main_html/"

    if test_mode is False: #get data via a url request
        print("Starting live request for MetaCritic gallery pages")
        for i in range(cpage,maxpages):
            URL = "https://www.metacritic.com/browse/games/score/metascore/all/ps4/filtered?hardware=psvr&page="+str(cpage)
            localFilename = str(cpage) + ".html"
                
            data = sh.makeURLRequest(URL, True,localDir,localFilename,5,0)
            metacritic_mainpagedata.append(data)
            print("done getting page# " + str(cpage))
               
            cpage+=1
    else:
        print("Starting LOCAL request for MetaCritic gallery pages")
        metacritic_mainpagedata = sh.getLocalHTMLCache(localDir)
    
        
##Take the data in metacritic_mainpagedata and extract all of the relevant info into a metacritic_gamedata object
        
    for data in metacritic_mainpagedata:
        soup = BeautifulSoup(data,'html.parser')

        g = soup.find_all('li', class_='product game_product')
        print(len(g))
        
        for games in g: #get all of the game_product rows that contain the info and iterate over them
            
            title = games.find('div', class_='product_title').find('a').text #find the title
            title = sh.removeExcessCharacters(title)
            
            metascore = games.find('div',class_='metascore_w').text #get the metascore
            metascore = sh.removeExcessCharacters(metascore)
            
            userscore = games.find('span', class_='textscore').text
            userscore = sh.removeExcessCharacters(userscore)
            
            releasedate = games.find('li', class_='release_date').find('span', class_='data').text
            releasedate = sh.removeExcessCharacters(releasedate)
            
            psvrrequired = games.find('li', class_='stat attributes').text
            psvrrequired = sh.removeExcessCharacters(psvrrequired)
            
            murl = games.find('div', class_="basic_stat product_title").find('a').get('href')
            murl = sh.removeExcessCharacters(murl)
            murl = "https://www.metacritic.com" + str(murl);
            
        #Query each product page for the NUMBER of reviews
            if test_mode is False:
                sh.randomsleep()
            URL = murl
     
            localFilename = str(title) + ".html"
            localDir = "metacritic_individualgames_html/"
            localFileLoc = localDir + localFilename
            
            if test_mode is False:
                print("Making request for: " + str(murl))
                prodpage = sh.makeURLRequest(URL, True,localDir,localFilename,5,0)
            else:
                print("Making local request for: " + localFileLoc)
                prodpage = sh.getLocalHTMLFile(localFileLoc)
                
            p_soup = BeautifulSoup(prodpage,'html.parser')
            num_reviews = p_soup.find_all('div', class_='summary')
                
            try:
                num_userreviews = num_reviews[1].find('a').text
                if num_userreviews.endswith(' Ratings'):
                    num_userreviews = num_userreviews[:-8] #Should remove the word ratings.
                num_userreviews = sh.removeExcessCharacters(num_userreviews)
            except:
                num_userreviews = -1
                print("FAILED ON FINDING NUM USER REVIEWS")
                    
            num_criticalreviews = num_reviews[0].find('a').find('span').text #Critics reviews are store din a different heirarchy than users!
            num_criticalreviews = sh.removeExcessCharacters(num_criticalreviews)
            
            
#Stuff the results into a custom data object and feed it into an array            
            tgame = metacritic_gamedata()
            tgame.name = title
            tgame.releasedate = releasedate
            tgame.metascore = metascore
            tgame.userscore = userscore
            tgame.vrrequired = psvrrequired
            tgame.metacriticurl = murl
            tgame.num_userreviews = num_userreviews
            tgame.num_criticalreviews = num_criticalreviews
            tgame.crunchNumbers()
 #           tgame.displayData()
            metacritic_vrgames.append(tgame)
            
    for g in metacritic_vrgames:
        g.removeNonAscii()
        #g.encodeStrings()
##Plop it out the Metacritic_gamedata data into a csv
    dt = now.strftime("%Y-%m-%d")
    filename = dt + "_Metacritic_PSVR"
    with open(filename + '.csv', mode='w') as csvfile:
        
        g_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        g_writer.writerow(["Game Name","Release Date","Metascore","User Score","Meta/User Delta","VR Required?"]) #header row
        
        for g in metacritic_vrgames:
            g_writer.writerow([g.name,g.releasedate, g.metascore,g.userscore,g.metauserdelta,g.vrrequired])
        
    print("METACRITIC SCRAPE COMPLETE; CSV LOCATED AT" + filename)
    
    return metacritic_vrgames
        