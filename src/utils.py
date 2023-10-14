import datetime, time
import tkinter as tk

#converts input from form to array
def fetch(type, entries):

    if(type not in ["A", "R", "I"]):
        return

    ret = []
    index = 0

    for entry in entries:
        
        tmp = entry[1].get()

        if(index == 1 and type == "I"):
            ret.append(tmp)
            return ret

        ret.append(tmp)
        index += 1

    return ret

#checks if "date" is valid and not bigger than actual date, returns timestamp
def checkDateValidity(date):
    try:
        analysedDate = datetime.datetime.strptime(date,'%d/%m/%Y')
        currentDate = datetime.datetime.today()
        if(analysedDate > currentDate):
            return 0
        return int(time.mktime(time.strptime(date, "%d/%m/%Y")))
    except:
        return 0
    
def signalErrorWindow(window, error):
    
    tk.messagebox.showerror('Libretto', 'Errore: '+error)
