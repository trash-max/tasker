from tkinter import *
from tkinter import ttk

import requests
import json


url = 'https://b72fa9de9108.ngrok.io/api2'


def clicked():
    lbl.configure(text="Я же просил...")


def get_projects():
    r_json = {
            "api_key": "super_secret_key",
            "request": "get_projects"
            }
    r = requests.post(url, json=r_json)
    # r_json = r.json()
    return r.json()


def get_tasks():
    r_json = {
            "api_key": "super_secret_key",
            "request": "get_tasks",
            "project": {"slug": "gnustpjw"}
            }
    r = requests.post(url, json=r_json)
    # r_json = r.json()
    return r.json()



window = Tk()
window.title('Tasker')
window.geometry('800x600+300+200')
tab_control = ttk.Notebook(window)

tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='1 st')
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text='2 nd')

for i in range(5):
    for y in range(5):
        lbl = Label(tab1, text=(str(i)+str(y)))
        lbl.grid(column=i, row=y, padx=20, pady=5)

tab_control.pack(expand=1, fill='both')

# frame1 = Frame(window, bd=5)
# frame2 = Frame(window, bd=5)
# frame1.pack()
# frame2.pack()
#
# print(get_projects())
# print(get_tasks())
#
# lbl = Label(frame1, text="Привет")
# lbl.grid(column=0, row=0)
#
#
# for i in range(5):
#     for y in range(5):
#         btn = Button(frame2, text="Не нажимать!", command=clicked)
#         btn.grid(column=i, row=y, padx=5, pady=5,)
#         # btn.pack(side='left')



window.mainloop()
