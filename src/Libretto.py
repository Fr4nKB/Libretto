import sys, os
import tkinter as tk
import multiprocessing as mp
import queue

#modules to realiza graphs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)

#custom modules
import gradesModule as gm
import networking as net
import jsonHandler as jl
import utils
import constants as const

configJSON,res = jl.loadJSON("config")
if(res == False):
    sys.exit(1)

#set theme for graphs
plt.rcParams.update({"figure.facecolor" : configJSON["consoleBGcolor"],
                    "axes.facecolor" : configJSON["textBGcolor"],
                    "xtick.color" : "white",
                    "ytick.color" : "white",
                    "text.color" : "white",
                    "axes.edgecolor": "gray"})

def print_grades(grades):

    #output grades
    textConsole.config(state=tk.NORMAL)     #make console writable
    textConsole.delete('1.0', tk.END)   #flush old content

    textConsole.insert(tk.END, grades)
	
    textConsole.pack(side=tk.TOP, fill=tk.X)
    textConsole.config(state=tk.DISABLED)   #make console read only

    #output summary grades
    textConsoleSummary.config(state=tk.NORMAL)     #make console writable
    textConsoleSummary.delete('1.0', tk.END)   #flush content

    ret = gm.grades.avg()
    for i, elem in enumerate(ret):
        textConsoleSummary.insert(tk.END, const.phrase[i]+str(elem)+"\n")

    textConsoleSummary.pack(side=tk.TOP, fill=tk.X)
    textConsoleSummary.config(state=tk.DISABLED)   #make console read only

def plot_stats(graph, name, x, y, ylim, dpi):

    #create plot
    fig = Figure(figsize=(3.9, 3), dpi = dpi)
    subplot = fig.add_subplot(111)
    subplot.plot(x, y, marker='o', color=configJSON["graphLine"])
    subplot.set_title(name)

    fig.gca().set_ylim(ylim)    #set max y range

    #setup x axis to display dates
    fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
    
    #take furthest dates and compute the number of days in between, set graph interval
    if(len(x) > 1):
        duration = (x[len(x) - 1] - x[0])
        dur_secs = duration.total_seconds()
        days  = duration.days
        days  = int(divmod(dur_secs, 86400)[0])
        intrvl = int(days/7)
        if(intrvl < 15):    #avoid too much dates when grades are close to each other
            intrvl = 15
        fig.gca().xaxis.set_major_locator(mdates.DayLocator(interval=intrvl))

    fig.autofmt_xdate(rotation=30, ha="center")

    #display on last point of the graph the y amount
    dim = len(x)
    if(dim > 0):
        fig.gca().annotate(y[dim-1], (x[dim-1], y[dim-1]), ha="right")
    
    #draw
    canvas = FigureCanvasTkAgg(fig, master = graph)
    canvas.draw()
    canvas.get_tk_widget().pack()

def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        ent = tk.Entry(row, bg=configJSON["formInput"], highlightthickness=0, relief=tk.FLAT, fg=configJSON["formText"])
        if(field == "PASSWORD"):
            ent.configure(show='*')
        ent.insert(0, field)
        
        row.pack(padx=15, pady=15)
        ent.pack(side=tk.LEFT)
        entries.append((field, ent))
    return entries

def updateGUI():
    global window, textConsole, textConsoleSummary, graph1, graph2
    
    gm.grades.loadFromFile()
    print_grades(gm.grades.toString())

    #remove graphs to replace them
    if(len(graph1.winfo_children()) != 0):
        graph1.winfo_children()[0].destroy()
    if(len(graph2.winfo_children()) != 0):
        graph2.winfo_children()[0].destroy()

    window.update()
    dim = int(textConsole.winfo_width()*4/(6*3.9))
    arr = gm.grades.toStats()
    plot_stats(graph1, "Andamento media", arr[0], arr[1], [18,31], dim)
    plot_stats(graph2, "Andamento carriera (CFU)", arr[0], arr[2], [0, const.TOTCFU+1], dim)

#refresh GUI when child has finished
def pollChild():
    global window, q

    #read from non blocking queue then refresh GUI
    try:
        q.get(False)
        updateGUI()
    #if queue is empty reschedule check in 500ms
    except queue.Empty:
        window.after(500, pollChild)

def addUdata(array, win):

    if(array != []):

        contents = {'uname': array[0], 'pwd': array[1]}
        jl.saveJSON("userdata", contents)

        try:
            if(net.loadUnipiGrades() == False):
                utils.signalErrorWindow("Dati non validi")
                return
        except:
            utils.signalErrorWindow("Dati non validi")
            return
    else:
        if os.path.exists("./docs/userdata.json"):
            os.remove("./docs/userdata.json")
        if os.path.exists("./docs/session.json"):
            os.remove("./docs/session.json")

    configJSON["init"] = "T"
    jl.saveJSON("config", configJSON)
    win.destroy()

def init():
    win = tk.Tk()
    win.resizable(False, False)
    win.configure(bg=configJSON["consoleBGcolor"])
    win.protocol("WM_DELETE_WINDOW", lambda: None)

    ents = makeform(win, const.init)
    btnPanel = tk.Frame(master=win, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
    btnPanel.pack(anchor=tk.CENTER)
    okBtn = tk.Button(btnPanel, bg=configJSON["posBtnColor"], text='OK', command=(lambda e = ents: addUdata(utils.fetch("I", e), win)))
    okBtn.pack(side=tk.LEFT, padx=5, pady=(15,25))
    manBtn = tk.Button(btnPanel, bg=configJSON["negBtnColor"], text='MANUAL', command=(lambda e = ents: addUdata([], win)))
    manBtn.pack(side=tk.LEFT, padx=5, pady=(15,25))

    win.mainloop()

if __name__ == "__main__":
    mp.freeze_support()

    if(configJSON["init"] == "F"):
        init()

    unipi = jl.loadJSON("userdata")[1]
    #if user is UNIPI then load grades from db
    if(unipi):
        q = mp.Queue()
        child = mp.Process(target=net.loadUnipiGrades, args={q})
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

    #setup first graph
    graph1 = tk.Frame(master=container1, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
    graph1.pack(side=tk.RIGHT)

    #setup control panel
    panelContainer = tk.Frame(master=container3, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
    panelContainer.pack(expand=True, side=tk.LEFT)
    panel = tk.Frame(master=panelContainer, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
    panel.pack(pady=25)

    #setup form to insert/delete grades
    ents = makeform(panel, const.fields)
    btnPanel = tk.Frame(master=panel, borderwidth=0, bg=configJSON["panelBGcolor"], highlightthickness=0)
    btnPanel.pack(anchor=tk.CENTER)
    addBtn = tk.Button(btnPanel, bg=configJSON["posBtnColor"], text='AGGIUNGI', command=(lambda e = ents: [gm.grades.addGrade(utils.fetch("A", e)), updateGUI()]))
    addBtn.pack(side=tk.LEFT, padx=5, pady=(15,25))
    rmvBtn = tk.Button(btnPanel, bg=configJSON["negBtnColor"], text='RIMUOVI', command=(lambda e = ents: [gm.grades.removeGrade(utils.fetch("R", e)), updateGUI()]))
    rmvBtn.pack(side=tk.RIGHT, padx=5, pady=(15,25))

    #setup second graph
    graph2 = tk.Frame(master=container3, borderwidth=0, bg=configJSON["consoleBGcolor"], highlightthickness=0)
    graph2.pack(side=tk.RIGHT)

    #display data
    updateGUI()
    if(unipi):
        window.after(1000, pollChild)

    #display window
    window.mainloop()
