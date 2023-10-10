import datetime

#checks if "date" is valid and not bigger than actual date
def checkDateValidity(date):
    try:
        analysedDate = datetime.datetime.strptime(date,'%d/%m/%Y')
        currentDate = datetime.datetime.today()
        if(analysedDate > currentDate):
            return False
        return True
    except:
        return False
    