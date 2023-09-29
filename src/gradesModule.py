import sys
import time

#modules to realiza graphs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

#modules for HTTP requests
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

#custom modules
import jsonLoader as jl
import constants as const

plt.style.use('dark_background')
grades = [] #all the grades will be loaded here
jl.loadJSON("userdata")
payload2 = {
    'j_username': jl.jsonFile['uname'],
    'j_password': jl.jsonFile['pwd'],
    '_eventId_proceed': ''
}

def loadGrades():
    global grades

    if(len(jl.jsonFile["grades"]) != 0):
        try:
            with open("./docs/"+jl.jsonFile["grades"], "r") as file:
                grades = file.readlines()
                file.close()
        except:
            print("Some error occured while reading",jl.jsonFile["grades"])
            sys.exit(1)

    else:
        opt = Options()
        opt.add_argument("--headless=new")
        browser = webdriver.Chrome(options = opt)

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
            browser.get(const.urls[0])

            #adding cookies to enter 'Libretto'
            browser.add_cookie({"name": 'shib_idp_session', "value": req_cookies['shib_idp_session']})
            browser.add_cookie({"name": 'JSESSIONID', "value": req_cookies['JSESSIONID']})

            #navigate to 'Libretto' page
            browser.get(const.urls[0])
            if(browser.current_url != const.urls[1]):
                time.sleep(1)   #wait for the page to fully load
                url = browser.find_elements(By.ID, 'gu_toolbar_sceltacarriera')[0].find_element(By.CLASS_NAME, 'toolbar-button-blu').get_attribute('href')
                browser.get(url)

            browser.get(const.urls[2])
            print("DONE")

            time.sleep(1)   #wait for the page to fully load
            rawData = ((browser.find_element(By.ID, 'tableLibretto')).find_element(By.CLASS_NAME, 'table-1-body')).text.split('\n')
            
            index = 0
            while(index < len(rawData)):
                
                tmp = rawData[index+1].split('-')
                tmp2 = tmp[0].split(' ')

                if(len(tmp2) <= 2): #no grade, skip
                    index += 2
                    continue

                elem = rawData[index] + ", "

                if(tmp2[2] == "30L"):   #grade
                        elem += "33, "
                else:
                    elem += tmp2[2] + ", "

                elem += tmp2[1] + ","

                if(len(tmp) > 1):   #date
                    elem += tmp[1]
                else:
                    elem += " NaN"
                
                elem += '\n'

                grades.append(elem)
                index += 2

        browser.quit()

def avg():
    global grades

    avg = 0
    cfuSum = 0
    tokenizedGrades = [elem.split(", ") for elem in grades]
    length = len(grades)

    for i in range(length):
        if(len(tokenizedGrades[i]) != 4):
            continue
        grade = int(tokenizedGrades[i][1])
        if(grade > 30):     #30L = 33, counts as 30
            grade = 30
        elif(grade < 18):
            continue
        avg += grade*int(tokenizedGrades[i][2])
        cfuSum += int(tokenizedGrades[i][2])

    mingrade = (avg + 18*(const.TOTCFU - cfuSum))/const.TOTCFU
    maxgrade = (avg + 30*(const.TOTCFU - cfuSum))/const.TOTCFU
    if(cfuSum != 0):
        avg /= cfuSum

    return round(avg, 2), round(mingrade, 2), round(maxgrade, 2)

def add_grade(elem):
    global grades

    if(elem == []):
        return
    
    toAdd = elem[0]+", "+elem[1]+", "+elem[2]+"\n"

    if(any(elem[0] in s for s in grades)):
        return
    
    grades.append(toAdd)

    file = open(jl.jsonFile["grades"], "w")
    for elem in grades:
        file.write(elem)
    file.close()

def remove_grade(subject):
    global grades

    if(len(subject) <= 0):
        return

    toRemove = [x for x in grades if subject in x]
    if(len(toRemove) == 0):
        return
    
    grades.remove(toRemove[0])

    file = open(jl.jsonFile["grades"], "w")
    for elem in grades:
        file.write(elem)
    file.close()
   
def convertToObject():
    global grades
    global toGraph

    objects = []
    toGraph = [[], [], []]

    for elem in grades:
        contents = elem.split(', ')
        date = contents[3][:len(contents[3])-1]
        timestruct = time.strptime(date, "%d/%m/%Y")

        objects.append((int(time.mktime(timestruct)), date, int(contents[1]), int(contents[2])))

    objects.sort(key=lambda x: x[0], reverse=False)

    cfuSUM = 0
    avg = 0
    for elem in objects:
        cfuSUM += elem[3]

        if(elem[2] == 33):
            tmp = 30
        else:
            tmp = elem[2]
            
        avg += tmp*elem[3]

        toGraph[0].append(datetime.datetime.strptime(elem[1],'%d/%m/%Y').date())
        toGraph[1].append(round(avg/cfuSUM, 2))
        toGraph[2].append(cfuSUM)

def plot_stats(name, nameX, nameY, x, y):

    plt.xlabel(nameX)
    plt.ylabel(nameY)
    plt.xticks(x)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=50))
    plt.plot(x, y, marker='o')
    plt.gcf().autofmt_xdate()

    plt.savefig(name+".png", dpi = 300)
    plt.clf()
    return
