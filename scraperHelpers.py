import re
from random import randint
from time import sleep
import urllib
from urllib.request import urlopen
import os

max_sleeptime = 5
min_sleeptime = 2

def removeExcessCharacters(data):
    #print("REMOVING EXCESS CHARACTERS:" + str(data))
    data = data.lstrip(' ')
    #print("AFTER LSTRIP:" + str(data))
    data = data.strip()
    #print("AFTER strip:" + str(data))
    data = str(data).replace("  ","")
    #print("AFTER replace:" + str(data))
    data = data.rstrip(' ')
    #print("AFTER rstrip:" + str(data))
    return data

def cleanAscii(s):
    return s.encode('ascii', 'ignore').decode('ascii')

def removeWhiteSpace(data):
    re.sub(r'\s+', '', str(data))
    return

def returnOnlyNumerals(data):
    nums = [int(s) for s in data.split() if s.isdigit()]
    return nums[0]

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        #print(text + "started with" + prefix)
        return text[len(prefix):]
    return text

def randomsleep():
    sleeptime = randint(min_sleeptime,max_sleeptime)
    print("SLEEPING FOR: " + str(sleeptime))
    sleep(sleeptime)
    return

def overrideSleeptime(min,max):
    min_sleeptime = min
    max_sleeptime = max
    
def removeTrailingPhrase(data,phrase):
    data = data.rstrip(phrase)


def makeURLRequest(URL, savelocal,local_dir,local_filename,timeoutmax,countAttempts):

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,} 
        request = urllib.request.Request(URL,None,headers)
        response = urllib.request.urlopen(request)
        page_data = response.read()
        
#Check to see if the save directory exists and if it doesn't, create it
        if os.path.isdir(local_dir) is False:
            try:
                os.mkdir(local_dir)
            except OSError:
                print("Created: " + str(local_dir))
            else:
                print("Could not create: " + str(local_dir))
#end dir check

#Save the html locally so i can stop harassing metacritic
        if savelocal is True:
            Html_file= open(local_dir + local_filename,"wb")
            Html_file.write(page_data)
            Html_file.close()
        return page_data

def getLocalHTMLCache(file_dir):
    files = os.listdir(file_dir) 
    htmlfiles = []
    
    for fnames in files:
        if fnames == ".DS_Store":
            files.remove(fnames)
    
    for f in files:
        file_loc = file_dir + f
        #print(file_loc)
        
        htmlfile = open(file_loc,'r+', encoding="utf-8") 
        html = htmlfile.read()
        htmlfiles.append(html)
     
    return htmlfiles
