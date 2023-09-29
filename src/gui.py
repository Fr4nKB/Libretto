import tkinter as tk

#custom models
import gradesModule as gm
import jsonLoader as jl
import constants as const

jl.loadJSON("config")

def print_grades(grades, textConsole, textConsoleSummary):

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

    ret = gm.avg()
    index = 0
    for elem in ret:
        textConsoleSummary.insert(tk.END, const.phrase[index]+str(elem)+"\n")
        index += 1

    textConsoleSummary.pack(side=tk.TOP, fill=tk.X)
    textConsoleSummary.config(state=tk.DISABLED)   #make console read only

def _fetch(type, entries):

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

def _makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        ent = tk.Entry(row, bg="#313131", highlightthickness=0, relief=tk.FLAT, fg="#9D9D9D")
        ent.insert(0, field)
        
        row.pack(padx=5, pady=10)
        ent.pack(side=tk.LEFT)
        entries.append((field, ent))
    return entries

def startGUI():
    gm.loadGrades()

    window = tk.Tk()
    window.minsize(600, 450)
    window.maxsize(1200, 900)
    window.resizable(False, False)
    window.title('Libretto')
    window.configure(bg=jl.jsonFile["panelBGcolor"])

    #setup console
    console = tk.PanedWindow(orient='vertical')
    vertScrollbar = tk.Scrollbar(console, orient='vertical')
    vertScrollbar.pack(side = tk.RIGHT, fill = tk.Y)

    textConsole = tk.Text(window, height = 9, wrap = tk.NONE,
                        yscrollcommand = vertScrollbar.set, bg=jl.jsonFile["consoleBGcolor"],
                        fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0)
    vertScrollbar.config(command=textConsole.yview)
    textConsoleSummary = tk.Text(window, height = 3, wrap = tk.NONE, bg=jl.jsonFile["textBGcolor"],
                        fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0, pady=25)
    
    print_grades(gm.grades, textConsole, textConsoleSummary)

    #setup control panel
    panel = tk.Frame(master=window, borderwidth=1, bg=jl.jsonFile["panelBGcolor"], highlightthickness=0)
    panel.pack(fill=tk.X, pady=25)

    if(len(jl.jsonFile['grades']) > 0):
        ents = _makeform(panel, fields)
        btnPanel = tk.Frame(master=panel, borderwidth=1, bg=jl.jsonFile["panelBGcolor"], highlightthickness=0)
        btnPanel.pack(side=tk.TOP)
        addBtn = tk.Button(btnPanel, bg=jl.jsonFile["addBtnColor"], text='AGGIUNGI', command=(lambda e = ents: [gm.add_grade(_fetch("A", e)), print_grades(gm.grades)]))
        addBtn.pack(side=tk.LEFT, padx=5, pady=5)
        rmvBtn = tk.Button(btnPanel, bg=jl.jsonFile["rmvBtnColor"], text='RIMUOVI', command=(lambda e = ents: [gm.remove_grade(_fetch("R", e)), print_grades(gm.grades)]))
        rmvBtn.pack(side=tk.RIGHT, padx=5, pady=5)

    #display window
    window.mainloop()
