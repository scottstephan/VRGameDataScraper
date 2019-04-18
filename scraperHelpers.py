import re
from random import randint
from time import sleep

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

def removeWhiteSpace(data):
    re.sub(r'\s+', '', str(data))
    return

def returnOnlyNumerals(data):
    nums = [int(s) for s in data.split() if s.isdigit()]
    return nums[0]

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        print(text + "started with" + prefix)
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
    
    

