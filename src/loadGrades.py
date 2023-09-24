import sys
import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

grades = []
urls = ['https://www.studenti.unipi.it/auth/Logon.do', 'https://www.studenti.unipi.it/auth/studente/HomePageStudente.do', 'https://www.studenti.unipi.it/auth/studente/Libretto/LibrettoHome.do?menu_opened_cod=menu_link-navbox_studenti_Carriera']

try:
    userdataJSON = open("./docs/userdata.json", "r")
    userdata = json.load(userdataJSON)
    userdataJSON.close()
except:
    print("Missing userdata.json")
    sys.exit(1)

payload1 = {
    'shib_idp_ls_exception.shib_idp_session_ss': "",
    'shib_idp_ls_success.shib_idp_session_ss': "true",
    'shib_idp_ls_value.shib_idp_session_ss': "",
    'shib_idp_ls_exception.shib_idp_persistent_ss': "",
    'shib_idp_ls_success.shib_idp_persistent_ss': "true",
    'shib_idp_ls_value.shib_idp_persistent_ss': "",
    'shib_idp_ls_supported': "true",
    '_eventId_proceed': "" 
}

payload2 = {
    'j_username': userdata['uname'],
    'j_password': userdata['pwd'],
    '_eventId_proceed': ''
}

def loadGrades():
    global grades

    opt = Options()
    opt.add_argument("--headless=new")
    browser = webdriver.Chrome(options = opt)

    with requests.Session() as s:

        print("Connection to unipi servers: ", end = '', flush = True)
        p1 = s.get(urls[0])
        p2 = s.get(p1.url)
        p3 = s.post(p2.url, data = payload1)
        p4 = s.get(p3.url)
        print("DONE")

        print("Logging in: ", end = '', flush = True)
        s.post(p4.url, data = payload2)
        print("DONE")

        print("Loading 'Alice' portal: ", end = '', flush = True)
        req_cookies = s.cookies.get_dict()
        browser.get(urls[0])

        #adding cookies to enter 'Libretto'
        browser.add_cookie({"name": 'shib_idp_session', "value": req_cookies['shib_idp_session']})
        browser.add_cookie({"name": 'JSESSIONID', "value": req_cookies['JSESSIONID']})

        #navigate to 'Libretto' page
        browser.get(urls[0])
        if(browser.current_url != urls[1]):
            time.sleep(1)   #wait for the page to fully load
            url = browser.find_elements(By.ID, 'gu_toolbar_sceltacarriera')[0].find_element(By.CLASS_NAME, 'toolbar-button-blu').get_attribute('href')
            browser.get(url)

        browser.get(urls[2])
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

            elem += tmp2[1] + ", "

            if(len(tmp) > 1):   #date
                elem += tmp[1]
            else:
                elem += "NaN"
            
            elem += '\n'

            grades.append(elem)
            index += 2

    browser.quit()
