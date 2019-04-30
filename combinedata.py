from bs4 import BeautifulSoup
import urllib
from urllib.request import urlopen
import csv
from decimal import *
import datetime 
import metacriticscraper as metacritic_scraper
import psnscraper as psn_scraper
import scraperHelpers as sh

class combineddata:
    name = "N/A"
    releasedate = "N/A"
    meta_metascore = "N/A"
    meta_userscore = "N/A"
    meta_vrrequired = "N/A"
    meta_metauserdelta = 0
    meta_metacriticurl="N/A"
    meta_num_userreviews = "UNASSIGNED"
    meta_num_criticalreviews = "UNASSIGNED"
    psn_price = "N/A"
    psn_developer = "N/A"
    psn_starrating = "N/A"
    psn_starrating_num = 0
    psn_numratings = "N/A"
    psn_psnurl="N/A"
    psn_requirements = "N/A"
    
    def setPSNDataItems(self,price,developer,starrating,num_starrating,numratings,psnurl,requirements):
        self.psn_price = price
        self.psn_developer = developer
        self.psn_starrating = starrating
        self.psn_starrating_num = num_starrating
        self.psn_numratings = numratings
        self.psn_psnurl= psnurl
        self.psn_requirements = requirements
        return
    
    def setMetacriticItems(self,metascore,userscore,requirements,scoredelta,url,num_userreviews,num_criticalreviews):
        self.meta_metascore = metascore
        self.meta_userscore = userscore
        self.meta_vrrequired = requirements
        self.meta_metauserdelta = 0
        self.meta_metacriticurl= url
        self.meta_num_userreviews = num_userreviews
        self.meta_num_criticalreviews = num_criticalreviews
        return

combined_data = []


def combinedata(metacritic_data,psn_data,now): #Its totally possible to do the following without creating a new data object but I'm not bound by memory here so I'm leaving it for the sake of clairty
#Use the largest data set
    print("Starting PSN: " + str(len(psn_data)))
    print("Starting MC: " + str(len(metacritic_data)))
    
    for p in psn_data:
        for m in metacritic_data:
            p_comp = p.name.replace(' ','')
            m_comp = m.name.replace(' ','')
            p_comp = p_comp.lower()
            m_comp = m_comp.lower()
           # print(repr(p_comp) + "," + repr(m_comp))

            if p_comp == m_comp:
                c = combineddata()
                c.name = p.name
                c.releasedate = p.releasedate
                c.setPSNDataItems(p.price,p.developer,p.starrating,p.starrating_num,p.numratings,p.psnurl,p.requirements)
                c.setMetacriticItems(m.metascore,m.userscore,m.vrrequired,m.metauserdelta,m.metacriticurl,m.num_userreviews,m.num_criticalreviews)
                
 #               print("MATCHED: ")
#                print(p.name + "::" + m.name)

                metacritic_data.remove(m)
                
                combined_data.append(c)
                
            
    print("Remaining PSN: " + str(len(psn_data)))
    print("Remaining MC: " + str(len(metacritic_data)))
        
    for p in psn_data:
        c = combineddata()
        c.name = p.name
        c.setPSNDataItems(p.price,p.developer,p.starrating,p.starrating_num,p.numratings,p.psnurl,p.requirements)
        combined_data.append(c)
        
    for m in metacritic_data:
        c = combineddata()
        c.name = m.name
        c.setMetacriticItems(m.metascore,m.userscore,m.vrrequired,m.metauserdelta,m.metacriticurl,m.num_userreviews,m.num_criticalreviews)
        print("UNMATCHED: " + repr(m.name))
        combined_data.append(c)
        
#    for m in metacritic_data:
#Write it all out. Phew.
    
    dt = now.strftime("%Y-%m-%d")
    filename = dt + "_COMBINED_PSVR"
    with open(filename + '.csv', mode='w') as csvfile:

        g_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        g_writer.writerow(["Game Name","PSN Developer","Release Date","PSN Price","Metascore","MC_NumCriticalRatings","Metacritic User Score","MC_NumUserRatings","PSN User Rating","PSN_NumberUserReviews","PSN_Requirements","MetaCritic Requirements","Metacritic URL","PSN URL"]) #header row
        
        for g in combined_data:
            g_writer.writerow([g.name,g.psn_developer,g.releasedate,g.psn_price,g.meta_metascore,g.meta_num_criticalreviews,g.meta_userscore,g.meta_num_userreviews,g.psn_starrating_num,g.psn_numratings,g.psn_requirements,g.meta_vrrequired,g.meta_metacriticurl,g.psn_psnurl])
        
 
    print("METACRITIC SCRAPE COMPLETE; CSV LOCATED AT" + filename)
    
    
    return
    