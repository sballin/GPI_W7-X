from __future__ import print_function # for print to work inside lambda
from Tkinter import *
from PIL import Image, ImageTk
from matplotlib import pyplot as plt
import sys
import time
import numpy as np
import os
import csv

from GPI_2 import GPI_2

from koheron import connect

GPI_host = os.getenv('HOST', 'w7xrp1')
GPI_client = connect(GPI_host, name='GPI_2')
GPI_driver = GPI_2(GPI_client)

root = Tk()
root.title("GPI Valve Control")

win_width = 1450
win_height = 880
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (win_width / 2)
y = (screen_height / 2) - (win_height / 2)
root.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
root.columnconfigure(4, weight=1)
root.columnconfigure(5, weight=1)
root.rowconfigure(10, weight=1)
root.rowconfigure(11, weight=1)
root.rowconfigure(12, weight=1)

image = Image.open("background.png")
photo = ImageTk.PhotoImage(image)
background = Label(image=photo)
background.image = photo
background.grid(rowspan=10, columnspan=4)

fast_valve_indicator = Canvas(root,width=29, height=43)
fast_valve_indicator.place(x=68, y=210)
fast_valve_status = fast_valve_indicator.create_rectangle(0, 0, 29, 43)
fast_valve_indicator.itemconfig(fast_valve_status, fill="red")
# def get_fast_status():
#     if (GPI_driver.get_fast_1_trigger() == 0 or GPI_driver.get_fast_1_permission_1() == 0 or GPI_driver.get_fast_1_duration_1() == 0 or 
#         GPI_driver.get_fast_1_permission_2() == 0 or GPI_driver.get_fast_1_duration_2() == 0):
#         fast_valve_indicator.itemconfig(fast_valve_status, fill="red")
#     else:
#         fast_valve_indicator.itemconfig(fast_valve_status, fill="green")
# get_fast_valve_status()
fast_valve_label_back = Label(text="FV2", width=13)
fast_valve_label_back.place(x=125, y=125)
def fast_valve_open():
    fast_win = Toplevel()
    fast_win_width = 250
    fast_win_height = 75
    fast_x = (screen_width / 2) - (fast_win_width / 2)
    fast_y = (screen_height / 2) - (fast_win_height / 2)
    fast_win.geometry("%dx%d+%d+%d" % (fast_win_width, fast_win_height, fast_x, fast_y))
    fast_win.title("FV2")
    fast_win.rowconfigure(0, weight=1)
    fast_win.rowconfigure(1, weight=1)
    fast_win.columnconfigure(0, weight=1)
    fast_win.columnconfigure(1, weight=1)
    msg = Message(fast_win, text="Please confirm the OPENING of the FV2.", width=200)
    msg.grid(columnspan=2)
    def fast_confirm():
        GPI_driver.set_fast_1_trigger(1)
#        get_fast_status()
        fast_valve_indicator.itemconfig(fast_valve_status, fill="green")
        fast_win.destroy()
    confirm = Button(fast_win, text="Confirm", width=10, command=fast_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(fast_win, text="Cancel", width=10, command=fast_win.destroy)
    cancel.grid(row=1, column=1)
def fast_valve_close():
    fast_win = Toplevel()
    fast_win_width = 250
    fast_win_height = 75
    fast_x = (screen_width / 2) - (fast_win_width / 2)
    fast_y = (screen_height / 2) - (fast_win_height / 2)
    fast_win.geometry("%dx%d+%d+%d" % (fast_win_width, fast_win_height, fast_x, fast_y))
    fast_win.title("FV2")
    fast_win.rowconfigure(0, weight=1)
    fast_win.rowconfigure(1, weight=1)
    fast_win.columnconfigure(0, weight=1)
    fast_win.columnconfigure(1, weight=1)
    msg = Message(fast_win, text="Please confirm the CLOSING of the FV2.", width=200)
    msg.grid(columnspan=2)
    def fast_confirm():
        GPI_driver.set_fast_1_trigger(0)
#        get_fast_status()
        fast_valve_indicator.itemconfig(fast_valve_status, fill="red")
        fast_win.destroy()
    confirm = Button(fast_win, text="Confirm", width=10, command=fast_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(fast_win, text="Cancel", width=10, command=fast_win.destroy)
    cancel.grid(row=1, column=1)
fast_valve_open_button = Button(root, text="OPEN", fg="green", width=10, command=fast_valve_open)
fast_valve_open_button.place(x=125, y=150)
fast_valve_close_button = Button(root, text="CLOSE", fg="red", width=10, command=fast_valve_close)
fast_valve_close_button.place(x=125, y=180)

slow_valve_1_indicator = Canvas(root,width=29, height=43)
slow_valve_1_indicator.place(x=417, y=464)
slow_valve_1_status = slow_valve_1_indicator.create_rectangle(0, 0, 29, 43)
slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill="red")
# def get_slow_1_status():
#     if GPI_driver.get_slow_1_trigger() == 0:
#         slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill="red")
#     else:
#         slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill="green")
# get_slow_1_status()
slow_valve_1_label_back = Label(text="V5", width=13)
slow_valve_1_label_back.place(x=475, y=380)
def slow_valve_1_open():
    slow_1_win = Toplevel()
    slow_1_win_width = 250
    slow_1_win_height = 75
    slow_1_x = (screen_width / 2) - (slow_1_win_width / 2)
    slow_1_y = (screen_height / 2) - (slow_1_win_height / 2)
    slow_1_win.geometry("%dx%d+%d+%d" % (slow_1_win_width, slow_1_win_height, slow_1_x, slow_1_y))
    slow_1_win.title("V5")
    slow_1_win.rowconfigure(0, weight=1)
    slow_1_win.rowconfigure(1, weight=1)
    slow_1_win.columnconfigure(0, weight=1)
    slow_1_win.columnconfigure(1, weight=1)
    msg = Message(slow_1_win, text="Please confirm the OPENING of V5.", width=200)
    msg.grid(columnspan=2)
    def slow_1_confirm():
        GPI_driver.set_slow_1_trigger(1)
#        get_slow_1_status()
        slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill="green")
        slow_1_win.destroy()
    confirm = Button(slow_1_win, text="Confirm", width=10, command=slow_1_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_1_win, text="Cancel", width=10, command=slow_1_win.destroy)
    cancel.grid(row=1, column=1)
def slow_valve_1_close():
    slow_1_win = Toplevel()
    slow_1_win_width = 250
    slow_1_win_height = 75
    slow_1_x = (screen_width / 2) - (slow_1_win_width / 2)
    slow_1_y = (screen_height / 2) - (slow_1_win_height / 2)
    slow_1_win.geometry("%dx%d+%d+%d" % (slow_1_win_width, slow_1_win_height, slow_1_x, slow_1_y))
    slow_1_win.title("V5")
    slow_1_win.rowconfigure(0, weight=1)
    slow_1_win.rowconfigure(1, weight=1)
    slow_1_win.columnconfigure(0, weight=1)
    slow_1_win.columnconfigure(1, weight=1)
    msg = Message(slow_1_win, text="Please confirm the CLOSING of V5.", width=200)
    msg.grid(columnspan=2)
    def slow_1_confirm():
        GPI_driver.set_slow_1_trigger(0)
#        get_slow_1_status()
        slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill="red")
        slow_1_win.destroy()
    confirm = Button(slow_1_win, text="Confirm", width=10, command=slow_1_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_1_win, text="Cancel", width=10, command=slow_1_win.destroy)
    cancel.grid(row=1, column=1)
slow_valve_1_open_button = Button(root, text="OPEN", fg="green", width=10, command=slow_valve_1_open)
slow_valve_1_open_button.place(x=475, y=405)
slow_valve_1_close_button = Button(root, text="CLOSE", fg="red", width=10, command=slow_valve_1_close)
slow_valve_1_close_button.place(x=475, y=435)

slow_valve_2_indicator = Canvas(root,width=43, height=29)
slow_valve_2_indicator.place(x=509, y=571)
slow_valve_2_status = slow_valve_2_indicator.create_rectangle(0, 0, 43, 29)
slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill="red")
# def get_slow_2_status():
#     if GPI_driver.get_slow_2_trigger() == 0:
#         slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill="red")
#     else:
#         slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill="green")
# get_slow_2_status()
slow_valve_2_label_back = Label(text="V4", width=13)
slow_valve_2_label_back.place(x=310, y=545)
def slow_valve_2_open():
    slow_2_win = Toplevel()
    slow_2_win_width = 250
    slow_2_win_height = 75
    slow_2_x = (screen_width / 2) - (slow_2_win_width / 2)
    slow_2_y = (screen_height / 2) - (slow_2_win_height / 2)
    slow_2_win.geometry("%dx%d+%d+%d" % (slow_2_win_width, slow_2_win_height, slow_2_x, slow_2_y))
    slow_2_win.title("V4")
    slow_2_win.rowconfigure(0, weight=1)
    slow_2_win.rowconfigure(1, weight=1)
    slow_2_win.columnconfigure(0, weight=1)
    slow_2_win.columnconfigure(1, weight=1)
    msg = Message(slow_2_win, text="Please confirm the OPENING of V4.", width=200)
    msg.grid(columnspan=2)
    def slow_2_confirm():
        GPI_driver.set_slow_2_trigger(1)
        #get_slow_2_status()
        slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill="green")
        slow_2_win.destroy()
    confirm = Button(slow_2_win, text="Confirm", width=10, command=slow_2_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_2_win, text="Cancel", width=10, command=slow_2_win.destroy)
    cancel.grid(row=1, column=1)
def slow_valve_2_close():
    slow_2_win = Toplevel()
    slow_2_win_width = 250
    slow_2_win_height = 75
    slow_2_x = (screen_width / 2) - (slow_2_win_width / 2)
    slow_2_y = (screen_height / 2) - (slow_2_win_height / 2)
    slow_2_win.geometry("%dx%d+%d+%d" % (slow_2_win_width, slow_2_win_height, slow_2_x, slow_2_y))
    slow_2_win.title("V4")
    slow_2_win.rowconfigure(0, weight=1)
    slow_2_win.rowconfigure(1, weight=1)
    slow_2_win.columnconfigure(0, weight=1)
    slow_2_win.columnconfigure(1, weight=1)
    msg = Message(slow_2_win, text="Please confirm the CLOSING of V4.", width=200)
    msg.grid(columnspan=2)
    def slow_2_confirm():
        GPI_driver.set_slow_2_trigger(0)
#        get_slow_2_status()
        slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill="red")
        slow_2_win.destroy()
    confirm = Button(slow_2_win, text="Confirm", width=10, command=slow_2_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_2_win, text="Cancel", width=10, command=slow_2_win.destroy)
    cancel.grid(row=1, column=1)
slow_valve_2_open_button = Button(root, text="OPEN", fg="green", width=10, command=slow_valve_2_open)
slow_valve_2_open_button.place(x=310, y=570)
slow_valve_2_close_button = Button(root, text="CLOSE", fg="red", width=10, command=slow_valve_2_close)
slow_valve_2_close_button.place(x=310, y=600)

slow_valve_3_indicator = Canvas(root,width=43, height=29)
slow_valve_3_indicator.place(x=661, y=374)
slow_valve_3_status = slow_valve_3_indicator.create_rectangle(0, 0, 43, 29)
slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill="green")
# def get_slow_3_status():
#     if GPI_driver.get_slow_3_trigger() == 0:
#         slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill="green")
#     else:
#         slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill="red")
# get_slow_3_status()
slow_valve_3_label_back = Label(text="V3", width=13)
slow_valve_3_label_back.place(x=795, y=345)
def slow_valve_3_open():
    slow_3_win = Toplevel()
    slow_3_win_width = 250
    slow_3_win_height = 75
    slow_3_x = (screen_width / 2) - (slow_3_win_width / 2)
    slow_3_y = (screen_height / 2) - (slow_3_win_height / 2)
    slow_3_win.geometry("%dx%d+%d+%d" % (slow_3_win_width, slow_3_win_height, slow_3_x, slow_3_y))
    slow_3_win.title("V3")
    slow_3_win.rowconfigure(0, weight=1)
    slow_3_win.rowconfigure(1, weight=1)
    slow_3_win.columnconfigure(0, weight=1)
    slow_3_win.columnconfigure(1, weight=1)
    msg = Message(slow_3_win, text="Please confirm the OPENING of V3.", width=200)
    msg.grid(columnspan=2)
    def slow_3_confirm():
        GPI_driver.set_slow_3_trigger(1)
#        get_slow_3_status()
        slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill="green")
        slow_3_win.destroy()
    confirm = Button(slow_3_win, text="Confirm", width=10, command=slow_3_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_3_win, text="Cancel", width=10, command=slow_3_win.destroy)
    cancel.grid(row=1, column=1)
def slow_valve_3_close():
    slow_3_win = Toplevel()
    slow_3_win_width = 250
    slow_3_win_height = 75
    slow_3_x = (screen_width / 2) - (slow_3_win_width / 2)
    slow_3_y = (screen_height / 2) - (slow_3_win_height / 2)
    slow_3_win.geometry("%dx%d+%d+%d" % (slow_3_win_width, slow_3_win_height, slow_3_x, slow_3_y))
    slow_3_win.title("V3")
    slow_3_win.rowconfigure(0, weight=1)
    slow_3_win.rowconfigure(1, weight=1)
    slow_3_win.columnconfigure(0, weight=1)
    slow_3_win.columnconfigure(1, weight=1)
    msg = Message(slow_3_win, text="Please confirm the CLOSING of V3.", width=200)
    msg.grid(columnspan=2)
    def slow_3_confirm():
        GPI_driver.set_slow_3_trigger(0)
#        get_slow_3_status()
        slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill="red")
        slow_3_win.destroy()
    confirm = Button(slow_3_win, text="Confirm", width=10, command=slow_3_confirm)
    confirm.grid(row=1, column=0)
    cancel = Button(slow_3_win, text="Cancel", width=10, command=slow_3_win.destroy)
    cancel.grid(row=1, column=1)
slow_valve_3_open_button = Button(root, text="OPEN", fg="green", width=10, command=slow_valve_3_open)
slow_valve_3_open_button.place(x=795, y=370)
slow_valve_3_close_button = Button(root, text="CLOSE", fg="red", width=10, command=slow_valve_3_close)
slow_valve_3_close_button.place(x=795, y=400)


abs_gauge_label_back = Label(text="Absolute Pressure Gauge")
abs_gauge_label_back.place(x=605, y=5)
diff_gauge_label_back = Label(text="Differential Pressure Gauge")
diff_gauge_label_back.place(x=855, y=170)

abs_gauge_label = Label(text="Absolute Pressure Gauge Reading:")
abs_gauge_label.grid(row=0, column=4, columnspan=2)
abs_gauge_graph = Canvas(root, width=200, height=200, background="grey")
abs_gauge_graph.grid(row=1, column=4, columnspan=2)

diff_gauge_label = Label(text="Differential Pressure Gauge Reading:")
diff_gauge_label.grid(row=3, column=4, columnspan=2)
diff_gauge_graph = Canvas(root, width=200, height=200, background="grey")
diff_gauge_graph.grid(row=4, column=4, columnspan=2)

desired_pressure_label = Label(text="Desired Pressure:")
desired_pressure_label.grid(row=6, column=4)
desired_pressure_entry = Entry(root, width=10)
desired_pressure_entry.grid(row=6, column=5)

fill_button = Button(root, text="Fill", width=10)
fill_button.grid(row=7, column=4)

pump_refill_button = Button(root, text="Pump & Refill", width=10)
pump_refill_button.grid(row=7, column=5)

local_permission_1_label = Label(text="Local Permission #1")
local_permission_1_label.grid(row=10, column=0)
timing_1_label = Label(text="FV2 Opening Timing #1")
timing_1_label.grid(row=11, column=0)
duration_1_label = Label(text="Opening Duration #1")
duration_1_label.grid(row=12, column=0)

local_permission_1_var = IntVar()
def print_1_check():
    if local_permission_1_var.get():
        GPI_driver.set_fast_1_permission_1(1)
    else:
        GPI_driver.set_fast_1_permission_1(0)
local_permission_1_check = Checkbutton(root, variable=local_permission_1_var, command=print_1_check)
local_permission_1_check.grid(row=10, column=1)
timing_1_entry = Entry(root, width=10)
def calc_clock_cycles(event):
    cycles_in_entry = int(int(timing_1_entry.get())/8e-9)
    cycles_in_duration = int(int(duration_1_entry.get())/8e-9)
    print(cycles_in_entry)
    print(cycles_in_duration)
timing_1_entry.bind("<Return>", calc_clock_cycles)
timing_1_entry.grid(row=11, column=1)
duration_1_entry = Entry(root, width=10)
duration_1_entry.grid(row=12, column=1)
duration_1_entry.bind("<Return>", calc_clock_cycles)

local_permission_2_label = Label(text="Local Permission #2")
local_permission_2_label.grid(row=10, column=2)
timing_2_label = Label(text="FV2 Opening Timing #2")
timing_2_label.grid(row=11, column=2)
duration_2_label = Label(text="Opening Duration #2")
duration_2_label.grid(row=12, column=2)

local_permission_2_var = IntVar()
def print_2_check():
    if local_permission_2_var.get():
        GPI_driver.set_fast_1_permission_2(1)
    else:
        GPI_driver.set_fast_1_permission_2(0)
local_permission_2_check = Checkbutton(root, variable=local_permission_2_var, command=print_2_check)
local_permission_2_check.grid(row=10, column=3)
timing_2_entry = Entry(root, width=10)
timing_2_entry.grid(row=11, column=3)
duration_2_entry = Entry(root, width=10)
duration_2_entry.grid(row=12, column=3)

W7X_permission_label = Label(text="W7-X Permission:")
W7X_permission_label.grid(row=10, column=4)
W7X_permission_status = Label(text="Granted/Forbidden")
W7X_permission_status.grid(row=10, column=5)

GPI_safe_state_label = Label(text="GPI Safe State:")
GPI_safe_state_label.grid(row=12, column=4)
GPI_safe_state_button = Button(root, text="ENABLE", width=10)
GPI_safe_state_button.grid(row=12, column=5)


root.mainloop()

