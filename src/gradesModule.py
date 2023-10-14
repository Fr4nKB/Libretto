import sys, time, datetime, re
from multiprocessing import Queue

#modules for HTTP requests
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

#custom modules
import jsonHandler as jl
import constants as const
import utils

class Grades:

    def __init__(this):
        this.__grades = []

    def __checkInput(this, array):
        if(len(array) != 4):
            return False
        
        name, gradeStr, cfuStr, date = array
        
        #check types
        if(type(name) != str or type(gradeStr) != str
           or type(cfuStr) != str or type(date) != str):
            return False
        
        if(gradeStr.isnumeric()):
            grade = int(gradeStr)
        else:
            return False
        
        if(cfuStr.isnumeric()):
            cfu = int(cfuStr)
        else:
            return False
        
        #check length of name
        if(len(name) not in [i for i in range(1, const.MAXNAMELEN)]):
            return False
        
        #check validity of date
        timestamp = utils.checkDateValidity(date)
        if(timestamp == False):
            return False
        
        #check validity of grade and cfu
        if((grade < 18 or (grade > 30 and grade != 33))):
                return False
        if(cfu <= 0):
            return False
        
        return (timestamp, name, grade, cfu, date)

    def addGrade(this, array):
        
        elem = this.__checkInput(array)

        #check for exact repetition
        if(any(elem == s for s in this.__grades)):
            return False
        
        this.__grades.append(elem)
        this.__grades.sort(key = lambda x: x[0], reverse=False)   #sort by date

        this.saveToFile()

        return True

    def removeGrade(this, array):

        elem = this.__checkInput(array)

        if(any(elem == s for s in this.__grades)):
            this.__grades.remove(elem)
            this.saveToFile()
            return True
    
        return False

    def avg(this):
        avg = 0
        cfuSum = 0

        for elem in this.__grades:
            cfuSum += elem[3]
            
            if(elem[2] == 33):     #30L = 33, counts as 30
                tmp = 30
            else:
                tmp = elem[2]

            avg += tmp*elem[3]

        mingrade = (avg + 18*(const.TOTCFU - cfuSum))/const.TOTCFU
        maxgrade = (avg + 30*(const.TOTCFU - cfuSum))/const.TOTCFU

        if(cfuSum != 0):
            avg /= cfuSum

        return round(avg, 2), round(mingrade, 2), round(maxgrade, 2)

    def loadFromFile(this):

        this.flush()

        try:
            with open("./docs/esami.txt", "r") as file:
                contents = file.readlines()
                file.close()

            for elem in contents:
                tokenizedStr = elem.split(", ")

                if(len(tokenizedStr) != 4):
                    return
                else:
                    date = tokenizedStr[3][:len(tokenizedStr[3])-1]
                    this.addGrade([tokenizedStr[0], tokenizedStr[1], tokenizedStr[2], date])

        except:
            this.__grades = []      

    def saveToFile(this):

        file = open("./docs/esami.txt", "w")
        file.write(this.toString())
        file.close() 

    def toString(this):
        res = ""
        for elem in this.__grades:
            res += f"{elem[1]}, {elem[2]}, {elem[3]}, {elem[4]}\n"
        return res
    
    def toStats(this):

        stats = [[], [], []]

        cfuSUM = 0
        avg = 0
        for elem in this.__grades:
            cfuSUM += elem[3]

            if(elem[2] == 33):
                tmp = 30
            else:
                tmp = elem[2]
                
            avg += tmp*elem[3]

            stats[0].append(datetime.datetime.strptime(elem[4],'%d/%m/%Y').date())
            stats[1].append(round(avg/cfuSUM, 2))
            stats[2].append(cfuSUM)

        return stats

    def flush(this):
        this.__grades.clear()

grades = Grades()

configJSON, res = jl.loadJSON("config")
if(res == False):
    sys.exit(1)

def saveCookies(contents):
    if(type(contents) != dict):
        return
    
    jl.saveJSON("session", contents)

def loadCookies(browser):
    cookiesJSON, res = jl.loadJSON("session")

    if(res):
        browser.get(const.urls[0])
        browser.add_cookie({"name": 'shib_idp_session', "value": cookiesJSON['shib_idp_session']})
        browser.add_cookie({"name": 'JSESSIONID', "value": cookiesJSON['JSESSIONID']})
        browser.get(const.urls[0])

        return ((browser.current_url == const.urls[0]) or (browser.current_url == const.urls[1]))
    
    else:
        return False

def loadUNIPIgrades(q = None):
    global grades

    opt = Options()
    opt.add_argument("--headless=new")
    opt.add_argument('--log-level=3')
    browser = webdriver.Chrome(options = opt)

    udataJSON, res = jl.loadJSON("userdata")
    if(res == True):
        payload2 = {
            'j_username': udataJSON['uname'],
            'j_password': udataJSON['pwd'],
            '_eventId_proceed': ''
        }

    print("Trying to connect using previous session: ", end = '', flush = True)
    if(loadCookies(browser) == False):
        print("Trying to establish a new session: ")

        count = 0
        req_cookies = {}
        while True:

            count += 1
            try:
                with requests.Session() as s:
                    print("Connection to unipi servers: ", end = '', flush = True)
                    p1 = s.get(const.urls[0])
                    p2 = s.get(p1.url)
                    p3 = s.post(p2.url, data = const.payload1)
                    p4 = s.get(p3.url)
                    print("DONE")

                    print("Logging in: ", end = '', flush = True)
                    s.post(p4.url, data = payload2)
                    print("DONE")

                    print("Loading 'Alice' portal: ", end = '', flush = True)
                    req_cookies = s.cookies.get_dict()
                    saveCookies(req_cookies)
                    break

            except:
                if(count == 5):
                    print("Final attempt n."+str(count)+" failed, quitting...")
                    return False
                print("Attempt n."+str(count)+" failed, trying again...")

        browser.get(const.urls[0])

        #adding cookies to enter 'Libretto'
        browser.add_cookie({"name": 'shib_idp_session', "value": req_cookies['shib_idp_session']})
        browser.add_cookie({"name": 'JSESSIONID', "value": req_cookies['JSESSIONID']})
        browser.get(const.urls[0])

    #select career
    if(browser.current_url == const.urls[0]):

        time.sleep(1)   #wait for the page to fully load

        try:    #fetch career
            choice = int(udataJSON["career"])
        except: #otherwise make user chose
            arr = browser.find_elements(By.CLASS_NAME, 'table-1-body')
            if(len(arr) >= 0):
                for elem in arr:
                    choices = re.findall(r"(\b(?:[A-Z]+[a-z]?[A-Z]*|[A-Z]*[a-z]?[A-Z]+)\b(?:\s+(?:[A-Z]+[a-z]?[A-Z]*|[A-Z]*[a-z]?[A-Z]+)\b)*)", elem.text)
                choice = utils.optionMenu("SELEZIONA CARRIERA", choices)

                udataJSON["career"] = str(choice)
                jl.saveJSON("userdata", udataJSON)

        url = browser.find_elements(By.ID, 'gu_toolbar_sceltacarriera')[choice].find_element(By.CLASS_NAME, 'toolbar-button-blu').get_attribute('href')
        browser.get(url)

    elif(browser.current_url != const.urls[0]):
        print("Error connecting to UNIPI servers")
        sys.exit(1)

    #navigate to 'Libretto' page
    browser.get(const.urls[2])
    print("DONE")

    time.sleep(1)   #wait for the page to fully load
    rawData = ((browser.find_element(By.ID, 'tableLibretto')).find_element(By.CLASS_NAME, 'table-1-body')).text.split('\n')

    index = 0
    toSave = ""
    while(index < len(rawData)):
        
        tmp = rawData[index+1].split('-')
        tmp2 = (tmp[0].split(' '))[1:]

        if(len(tmp2) <= 2): #no grade yet, skip
            index += 2
            continue

        elem = rawData[index] + ", "

        if(tmp2[len(tmp2)-2] == "30L"):   #grade
                elem += "33, "
        elif(tmp2[len(tmp2)-2].isnumeric() == True):
            elem += tmp2[len(tmp2)-2] + ", "
        else:
            index += 2
            continue

        elem += tmp2[0] + ","

        if(len(tmp) > 1):   #date
            elem += tmp[1]
        else:
            elem += " NaN"
        
        elem += '\n'
        toSave += elem
        index += 2

    browser.quit()

    #save grades locally
    with open("./docs/esami.txt", "w") as file:
        file.write(toSave)
        file.close()

    #used to communicate to parent when finished processing
    if(q != None):
        q.put("")
