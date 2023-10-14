import sys, datetime, time
import tkinter as tk

import jsonHandler as jl
import utils

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
    
def signalErrorWindow(error):
    
    tk.messagebox.showerror('Libretto', 'Errore: '+error)

def __answerMenu(win, options, choice):
    if(choice not in options):
        pass        
    else:
        win.destroy()

def optionMenu(name, options):

    configJSON,res = jl.loadJSON("config")
    if(res == False):
        sys.exit(1)

    win = tk.Tk()
    win.title(name)
    win.resizable(False, False)
    win.configure(bg=configJSON["consoleBGcolor"])
    win.protocol("WM_DELETE_WINDOW", lambda: None)
    
    label = tk.Label(win,  text='Seleziona una carriera:')
    label.grid(column=0, row=0, sticky=tk.W)

    #keep track of the option selected in OptionMenu
    choice = tk.StringVar(win)
    choice.set("-----")

    # option menu
    option_menu = tk.OptionMenu(win, choice, *options)
    option_menu.grid(column=1, row=0, sticky=tk.W)

    okBtn = tk.Button(win, bg=configJSON["posBtnColor"], text='OK', command=lambda: __answerMenu(win, options, choice.get()))
    okBtn.grid(column=0, row=1, sticky=tk.W)
    
    win.mainloop()

    return options.index(choice.get())
