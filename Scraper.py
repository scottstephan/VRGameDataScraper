from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
from decimal import *
import datetime 
import metacriticscraper as metacritic_scraper
import psnscraper as psn_scraper
import scraperHelpers as sh
import combinedata as combiner

#######STUFF TO DEFINE ###############
now = datetime.datetime.now()
runintestmode = False #If we run the scrapers in test mode they'll use the HTML located in the root directory

metacritic_maxpage = 2 #the number of pages of results to grab. right now there are only 2, but build to scale! Any
# additional results beyond the max # wont return relevant data for BSoup
psn_maxpage = 15 #if you go over the page limit then psn returns just the last available page. will need to check for dupes. also, psn urls start at 1, so 14 pages is 15, not 14.

###END DEFINEABLES###

###################################### CALL THE SCRAPERS ##################################
sh.overrideSleeptime(1,5)
metacritic_data = metacritic_scraper.scrape("psvr",metacritic_maxpage,True,now,runintestmode)
psn_data = psn_scraper.scrape("psvr",psn_maxpage,True,now,runintestmode)
###################################### END SCRAPE ##################################

###Combine the data###
combiner.combinedata(metacritic_data,psn_data,now)
###End combine###

print("all done");
