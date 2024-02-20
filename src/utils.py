import sys, datetime, time
import tkinter as tk
import jsonHandler as jl

#converts input from form to array
def fetch(type, entries):

    if(type not in ["A", "R", "I"]):
        return

    ret = []
    index = 0

    for entry in entries:
        
        tmp = entry[1].get()

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

def __answerMenu(choiceWin, options, choice):
    if(choice not in options):
        pass    
    else:
        choiceWin.destroy()

def optionMenu(options, q):

    configJSON, res = jl.loadJSON("config")
    if(res == False):
        sys.exit(1)

    choiceWin = tk.Tk()
    choiceWin.title("")
    choiceWin.geometry("200x200")
    choiceWin.resizable(False, False)
    choiceWin.configure(bg=configJSON["panelBGcolor"])
    choiceWin.protocol("WM_DELETE_WINDOW", lambda: None)
    
    panel = tk.Frame(master=choiceWin, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
    panel.pack(expand=True)
    
    label = tk.Label(panel, text='Seleziona una carriera:')
    label.grid(column=0, row=0, sticky=tk.W)

    #keep track of the option selected in OptionMenu
    choice = tk.StringVar(panel)
    choice.set("-----")

    # option menu
    option_menu = tk.OptionMenu(panel, choice, *options)
    option_menu.grid(column=1, row=0, sticky=tk.W)

    okBtn = tk.Button(panel, bg=configJSON["posBtnColor"], text='OK', command=lambda: __answerMenu(choiceWin, options, choice.get()))
    okBtn.grid(column=0, row=1, sticky=tk.W)

    choiceWin.mainloop()

    q.put(options.index(choice.get()))
