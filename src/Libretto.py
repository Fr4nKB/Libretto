import sys
import tkinter as tk
import multiprocessing as mp

#modules to realiza graphs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

#custom modules
import gradesModule as gm
import jsonHandler as jl
import constants as const

configJSON,res = jl.loadJSON("config")
if(res == False):
    sys.exit(1)

plt.rcParams.update({"figure.facecolor" : configJSON["consoleBGcolor"],
                    "axes.facecolor" : configJSON["textBGcolor"],
                    "xtick.color" : "white",
                    "ytick.color" : "white",
                    "text.color" : "white",
                    "axes.edgecolor": "gray"})

def print_grades(grades):

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

def plot_stats(graph, name, x, y, ylim, dpi):

    fig = Figure(figsize=(3.9, 3), dpi = dpi)
    subplot = fig.add_subplot(111)
    subplot.plot(x, y, marker='o', color=configJSON["graphLine"])
    subplot.set_title(name)
    fig.gca().set_ylim(ylim)
    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    if(len(x) > 1):
        fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=30))
    fig.autofmt_xdate(rotation=30, ha="center")
    
    canvas = FigureCanvasTkAgg(fig, master = graph)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    return

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
        elif(index in [1,2]):
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
        ent = tk.Entry(row, bg=configJSON["formInput"], highlightthickness=0, relief=tk.FLAT, fg=configJSON["formText"])
        ent.insert(0, field)
        
        row.pack(padx=15, pady=15)
        ent.pack(side=tk.LEFT)
        entries.append((field, ent))
    return entries

def updateGUI():
    global graph1, graph2

    gm.loadLocalGrades()
    print_grades(gm.grades)

    #remove graphs to replace them
    if(len(graph1.winfo_children()) != 0):
        graph1.winfo_children()[0].destroy()
    if(len(graph2.winfo_children()) != 0):
        graph2.winfo_children()[0].destroy()

    window.update()
    dim = int(textConsole.winfo_width()*4/(6*3.9))
    arr = gm.gradesToStats()
    plot_stats(graph1, "Andamento media", arr[0], arr[1], [18,30], dim)
    plot_stats(graph2, "Andamento carriera (CFU)", arr[0], arr[2], [0, const.TOTCFU], dim)

child = mp.Process(target=gm.loadUNIPIgrades)
child.start()

window = tk.Tk()
window.resizable(False, False)
window.title('Libretto')
window.configure(bg=configJSON["consoleBGcolor"])

#containers to handle disposition of frames
    #container for textconsole and first graph
container1 = tk.Frame(master=window, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
container1.pack(side=tk.TOP, pady=(0,0))
    #container for textconsole
container2 = tk.Frame(master=container1, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
container2.pack(side=tk.LEFT)
    #container for panel and second graph
container3 = tk.Frame(master=window, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
container3.pack(side=tk.BOTTOM, fill=tk.X)

#setup console
console = tk.PanedWindow(orient='vertical', master=container2)
vertScrollbar = tk.Scrollbar(console, orient='vertical')
vertScrollbar.pack(side = tk.RIGHT, fill = tk.Y)

textConsole = tk.Text(container2, height = 12, width = 75, wrap = tk.NONE,
                    yscrollcommand = vertScrollbar.set, bg=configJSON["consoleBGcolor"],
                    fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0)
vertScrollbar.config(command=textConsole.yview)
textConsoleSummary = tk.Text(container2, height = 3, width = 75, wrap = tk.NONE, bg=configJSON["textBGcolor"],
                    fg="white", state=tk.DISABLED, highlightthickness=0, borderwidth=0)

graph1 = tk.Frame(master=container1, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
graph1.pack(side=tk.RIGHT)

#setup control panel
panelContainer = tk.Frame(master=container3, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
panelContainer.pack(expand=True, side=tk.LEFT)
panel = tk.Frame(master=panelContainer, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
panel.pack(pady=25)

ents = _makeform(panel, const.fields)
btnPanel = tk.Frame(master=panel, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
btnPanel.pack(anchor=tk.CENTER)
addBtn = tk.Button(btnPanel, bg=configJSON["addBtnColor"], text='AGGIUNGI', command=(lambda e = ents: [gm.add_grade(_fetch("A", e)), print_grades(gm.grades)]))
addBtn.pack(side=tk.LEFT, padx=5, pady=(15,25))
rmvBtn = tk.Button(btnPanel, bg=configJSON["rmvBtnColor"], text='RIMUOVI', command=(lambda e = ents: [gm.remove_grade(_fetch("R", e)), print_grades(gm.grades)]))
rmvBtn.pack(side=tk.RIGHT, padx=5, pady=(15,25))

graph2 = tk.Frame(master=container3, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
graph2.pack(side=tk.RIGHT)

#display data
updateGUI()

#adjust gui to fit window size
window.update()
padding = int((container1.winfo_height() - (textConsole.winfo_height()+textConsoleSummary.winfo_height()))/4)
textConsole.configure(pady=padding)
textConsoleSummary.configure(pady=padding)

window.after(10000, updateGUI)

#display window
window.mainloop()
