import datetime

#custom modules
import constants as const
import utils

class Grades:

    def __init__(self, thesis_value: int = 3, value30L: int = 30):
        self.__grades = []
        self.__thesis = thesis_value
        self.value30L = value30L
        self.TOTCFU = const.TOTCFU[0]

    def __checkInput(self, array):
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
        if(cfu <= 0 or cfu > 30):
            return False
        
        return (timestamp, name, grade, cfu, date)

    def addGrade(self, array):
        
        elem = self.__checkInput(array)

        #check for exact repetition
        if(any(elem == s for s in self.__grades)):
            return False
        
        self.__grades.append(elem)
        self.__grades.sort(key = lambda x: x[0], reverse=False)   #sort by date

        self.saveToFile()

        return True

    def removeGrade(self, array):

        elem = self.__checkInput(array)

        if(any(elem == s for s in self.__grades)):
            self.__grades.remove(elem)
            self.saveToFile()
            return True
    
        return False

    def avg(self):
        avg = 0
        cfuSum = 0

        for elem in self.__grades:
            cfuSum += elem[3]
            
            if(elem[2] == 33):
                tmp = self.value30L
            else:
                tmp = elem[2]

            avg += tmp*elem[3]

        for elem in const.TOTCFU:
            if(elem >= cfuSum):
                self.TOTCFU = elem
                break

        rem_cfu = self.TOTCFU - self.__thesis - cfuSum
        mingrade = (avg + 18 * rem_cfu) / (self.TOTCFU - self.__thesis)
        maxgrade = (avg + self.value30L * rem_cfu) / (self.TOTCFU - self.__thesis)

        if(cfuSum != 0):
            avg /= cfuSum

        return round(avg, 2), round(mingrade, 2), round(maxgrade, 2)

    def loadFromFile(self):

        self.flush()

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
                    try:
                        self.addGrade([tokenizedStr[0], tokenizedStr[1], tokenizedStr[2], date])
                    except:
                        continue

        except:
            self.__grades = []    

    def saveToFile(self):

        file = open("./docs/esami.txt", "w")
        file.write(self.toString())
        file.close() 

    def toString(self):
        res = ""
        for elem in self.__grades:
            res += f"{elem[1]}, {elem[2]}, {elem[3]}, {elem[4]}\n"
        return res
    
    def toStats(self):

        stats = [[], [], []]

        cfuSUM = 0
        avg = 0
        for elem in self.__grades:
            cfuSUM += elem[3]

            if(elem[2] == 33):
                tmp = self.value30L
            else:
                tmp = elem[2]
                
            avg += tmp * elem[3]

            stats[0].append(datetime.datetime.strptime(elem[4],'%d/%m/%Y').date())
            stats[1].append(round(avg / cfuSUM, 2))
            stats[2].append(cfuSUM)

        return stats

    def flush(self):
        self.__grades.clear()

grades = Grades()