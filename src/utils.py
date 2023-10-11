import datetime
import tkinter as tk

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
    
def signalErrorWindow(window, error):
    
    tk.messagebox.showerror('Libretto', 'Errore: '+error)

    # Create a button to delete the button
    b = tk.Button(window, text="OK", command=tk.on_click)
    b.pack(pady=20)
