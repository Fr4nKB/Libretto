import sys, datetime

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