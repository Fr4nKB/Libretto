import sys
import json
import tkinter as tk
import loadGrades as lg

grades = []
TOTCFU = 120
index = 0
commands = ["Libretto", "Aggiungi un voto", "Rimuovi un voto", "Stampa media"]
phrase = ["La media ponderata è ", "Media con solo 18 d'ora in poi: ", "Media con solo 30 d'ora in poi: "]

try:
    configJSON = open("./docs/config.json", "r")
    config = json.load(configJSON)
    configJSON.close()
except:
    print("Missing config.json")
    sys.exit(1)

def load_grades():
    global grades
    if(len(config["grades"]) == 0):
        lg.loadGrades()
        grades = lg.grades
    else:
        try:
            with open("./docs/"+config["grades"], "r") as file:
                grades = file.readlines()
                file.close()
        except:
            print("Some error occured while reading",config["grades"])
            sys.exit(1)
    
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

    mingrade = (avg + 18*(TOTCFU - cfuSum))/TOTCFU
    maxgrade = (avg + 30*(TOTCFU - cfuSum))/TOTCFU
    if(cfuSum != 0):
        avg /= cfuSum

    return round(avg, 2), round(mingrade, 2), round(maxgrade, 2)

def print_grades():
    global grades
    global textConsole
    global textConsoleSummary

    #output grades
    textConsole.config(state=tk.NORMAL)     #make console writable
    textConsole.delete('1.0', tk.END)   #flush content

    for elem in grades:
        textConsole.insert(tk.END, elem)
	
    textConsole.pack(side=tk.TOP, fill=tk.X)
    textConsole.config(state=tk.DISABLED)   #make console read only

    #output summary grades
    textConsoleSummary.config(state=tk.NORMAL)     #make console writable
    textConsoleSummary.delete('1.0', tk.END)   #flush content

    ret = avg()
    index = 0
    for elem in ret:
        textConsoleSummary.insert(tk.END, phrase[index]+str(elem)+"\n")
        index += 1

    textConsoleSummary.pack(side=tk.TOP, fill=tk.X)
    textConsoleSummary.config(state=tk.DISABLED)   #make console read only

def add_grade(elem):

    if(elem == []):
        return
    
    toAdd = elem[0]+", "+elem[1]+", "+elem[2]+"\n"

    if(any(elem[0] in s for s in grades)):
        return
    
    grades.append(toAdd)

    file = open(config["grades"], "w")
    for elem in grades:
        file.write(elem)
    file.close()

    print_grades()

def remove_grade(subject):
    global grades

    if(len(subject) <= 0):
        return

    toRemove = [x for x in grades if subject in x]
    if(len(toRemove) == 0):
        return
    
    grades.remove(toRemove[0])

    file = open(config["grades"], "w")
    for elem in grades:
        file.write(elem)
    file.close()

    print_grades()
    
fields = ['CORSO', 'VOTO', 'CFU']

def fetch(type, entries):

    if(type not in ["A", "R"]):
        return

    ret = []
    index = 0

    for entry in entries:

        tmp = entry[1].get()
        length = len(tmp)

        if(length not in [i for i in range(1, 31)]):
            return []
        if(type == "R"):
            return tmp
        elif(index > 0):
            if(str.isnumeric(tmp) == False):
                return []
            tmp_int = int(tmp)
            if(index == 1 and (tmp_int < 18 or (tmp_int > 30 and tmp_int != 33))):
                return []
            elif(index == 2 and (tmp_int) <= 0):
                return []
        
        ret.append(tmp)
        index += 1
    
    return ret

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        ent = tk.Entry(row, bg="#313131", highlightthickness=0, relief=tk.FLAT, fg="#9D9D9D")
        ent.insert(0, field)
        
        row.pack(padx=5, pady=10)
        ent.pack(side=tk.LEFT)
        entries.append((field, ent))
    return entries

if __name__ == "__main__":

    #load grades and setup a window
    load_grades()
    window = tk.Tk()
    window.minsize(600, 450)
    window.maxsize(1200, 800)
    window.resizable(False, False)
    window.title('Libretto')
    window.configure(bg=config["panelBGcolor"])

    #setup console
    console = tk.PanedWindow(orient='vertical')
    vertScrollbar = tk.Scrollbar(console, orient='vertical')
    vertScrollbar.pack(side = tk.RIGHT, fill = tk.Y)

    textConsole = tk.Text(window, height = 9, wrap = tk.NONE,
                        yscrollcommand = vertScrollbar.set, bg=config["consoleBGcolor"],
                        fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0)
    vertScrollbar.config(command=textConsole.yview)
    textConsoleSummary = tk.Text(window, height = 3, wrap = tk.NONE, bg=config["textBGcolor"],
                        fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0, pady=25)
    print_grades()

    #setup control panel
    panel = tk.Frame(master=window, borderwidth=1, bg=config["panelBGcolor"], highlightthickness=0)
    panel.pack(fill=tk.X, pady=25)

    ents = makeform(panel, fields)
    btnPanel = tk.Frame(master=panel, borderwidth=1, bg=config["panelBGcolor"], highlightthickness=0)
    btnPanel.pack(side=tk.TOP)
    addBtn = tk.Button(btnPanel, bg=config["addBtnColor"], text='AGGIUNGI', command=(lambda e = ents: print(fetch("A", e))))
    addBtn.pack(side=tk.LEFT, padx=5, pady=5)
    rmvBtn = tk.Button(btnPanel, bg=config["rmvBtnColor"], text='RIMUOVI', command=(lambda e = ents: print(fetch("R", e))))
    rmvBtn.pack(side=tk.RIGHT, padx=5, pady=5)

    #display window
    window.mainloop()