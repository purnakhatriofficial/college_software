from tkinter import *
from datetime import datetime

root = Tk()
root.title("Calendar")
root.geometry("600x600")
root.resizable(0, 0)
root.config(bg="black")

def calendar():
    date = datetime.now() 
    day = date.strftime("%A")
    month = date.strftime("%B")
    year = date.strftime("%Y")
    date_str = date.strftime("%d")
    time = date.strftime("%H:%M:%S")
    label.config(text=f"{day}\n{date_str}/{month}/{year}\n{time}")
    label.after(1000, calendar)

label = Label(root, font=("Courier", 40), bg="black", fg="white")
label.pack(anchor="center")

calendar()
root.mainloop()
