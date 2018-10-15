'''
GUI for valve control in GPI system at W7-X.

Original code by Kevin Tang.
'''

from __future__ import print_function # for print to work inside lambda
import tkinter as tk
from PIL import Image, ImageTk
import os
import koheron 
from GPI_2 import GPI_2


def get_fast_status():
    if (
            GPI_driver.get_fast_1_trigger()      == 0 or
            GPI_driver.get_fast_1_permission_1() == 0 or
            GPI_driver.get_fast_1_duration_1()   == 0 or 
            GPI_driver.get_fast_1_permission_2() == 0 or
            GPI_driver.get_fast_1_duration_2()   == 0
        ):
        fast_valve_indicator.itemconfig(fast_valve_status, fill='red')
    else:
        fast_valve_indicator.itemconfig(fast_valve_status, fill='green')
        
        
def fast_valve_open():
    fast_win = tk.Toplevel()
    fast_win_width = 250
    fast_win_height = 75
    fast_x = (screen_width / 2) - (fast_win_width / 2)
    fast_y = (screen_height / 2) - (fast_win_height / 2)
    fast_win.geometry('%dx%d+%d+%d' % (fast_win_width, fast_win_height, fast_x, fast_y))
    fast_win.title('FV2')
    fast_win.rowconfigure(0, weight=1)
    fast_win.rowconfigure(1, weight=1)
    fast_win.columnconfigure(0, weight=1)
    fast_win.columnconfigure(1, weight=1)
    msg = tk.Message(fast_win, text='Please confirm the OPENING of the FV2.', width=200)
    msg.grid(columnspan=2)
    
    def fast_confirm():
        GPI_driver.set_fast_1_trigger(1)
        #get_fast_status()
        fast_valve_indicator.itemconfig(fast_valve_status, fill='green')
        fast_win.destroy()
        
    confirm = tk.Button(fast_win, text='Confirm', width=10, command=fast_confirm)
    confirm.grid(row=1, column=0)
    cancel = tk.Button(fast_win, text='Cancel', width=10, command=fast_win.destroy)
    cancel.grid(row=1, column=1)
    
    
def fast_valve_close():
    fast_win = tk.Toplevel()
    fast_win_width = 250
    fast_win_height = 75
    fast_x = (screen_width / 2) - (fast_win_width / 2)
    fast_y = (screen_height / 2) - (fast_win_height / 2)
    fast_win.geometry('%dx%d+%d+%d' % (fast_win_width, fast_win_height, fast_x, fast_y))
    fast_win.title('FV2')
    fast_win.rowconfigure(0, weight=1)
    fast_win.rowconfigure(1, weight=1)
    fast_win.columnconfigure(0, weight=1)
    fast_win.columnconfigure(1, weight=1)
    msg = tk.Message(fast_win, text='Please confirm the CLOSING of the FV2.', width=200)
    msg.grid(columnspan=2)
    
    def fast_confirm():
        GPI_driver.set_fast_1_trigger(0)
        #get_fast_status()
        fast_valve_indicator.itemconfig(fast_valve_status, fill='red')
        fast_win.destroy()
        
    confirm = tk.Button(fast_win, text='Confirm', width=10, command=fast_confirm)
    confirm.grid(row=1, column=0)
    cancel = tk.Button(fast_win, text='Cancel', width=10, command=fast_win.destroy)
    cancel.grid(row=1, column=1)


def get_slow_status(valve_number):
    fill = 'green' if getattr(GPI_driver, f'get_slow_{valve_number}_trigger')() else 'red'
    globals()[f'slow_valve_{valve_number}_indicator'].itemconfig(globals()[f'slow_valve_{valve_number}_status'], fill=fill)
    

def slow_valve_open(valve_number):
    valve_name = ['V5', 'V4', 'V3'][valve_number - 1]
    slow_win = tk.Toplevel()
    slow_win_width = 250
    slow_win_height = 75
    slow_win_x = (screen_width / 2) - (slow_win_width / 2)
    slow_win_y = (screen_height / 2) - (slow_win_height / 2)
    slow_win.geometry('%dx%d+%d+%d' % (slow_win_width, slow_win_height, slow_win_x, slow_win_y))
    slow_win.title(valve_name)
    slow_win.rowconfigure(0, weight=1)
    slow_win.rowconfigure(1, weight=1)
    slow_win.columnconfigure(0, weight=1)
    slow_win.columnconfigure(1, weight=1)
    msg = tk.Message(slow_win, text=f'Please confirm the OPENING of {valve_name}.', width=200)
    msg.grid(columnspan=2)
    
    def slow_confirm():
        if valve_name == 'V3': # reversed from normal
            getattr(GPI_driver, f'set_slow_{valve_number}_trigger')(0)
        else:
            getattr(GPI_driver, f'set_slow_{valve_number}_trigger')(1)
        #globals()[f'get_slow_status')](valve_number)
        globals()[f'slow_valve_{valve_number}_indicator'].itemconfig(globals()[f'slow_valve_{valve_number}_status'], fill='green')
        slow_win.destroy()
        
    confirm = tk.Button(slow_win, text='Confirm', width=10, command=slow_confirm)
    confirm.grid(row=1, column=0)
    cancel = tk.Button(slow_win, text='Cancel', width=10, command=slow_win.destroy)
    cancel.grid(row=1, column=1)
    
    
def slow_valve_close(valve_number):
    valve_name = ['V5', 'V4', 'V3'][valve_number - 1]
    slow_win = tk.Toplevel()
    slow_win_width = 250
    slow_win_height = 75
    slow_win_x = (screen_width / 2) - (slow_win_width / 2)
    slow_win_y = (screen_height / 2) - (slow_win_height / 2)
    slow_win.geometry('%dx%d+%d+%d' % (slow_win_width, slow_win_height, slow_win_x, slow_win_y))
    slow_win.title(valve_name)
    slow_win.rowconfigure(0, weight=1)
    slow_win.rowconfigure(1, weight=1)
    slow_win.columnconfigure(0, weight=1)
    slow_win.columnconfigure(1, weight=1)
    msg = tk.Message(slow_win, text=f'Please confirm the CLOSING of {valve_name}.', width=200)
    msg.grid(columnspan=2)
    
    def slow_confirm():
        if valve_name == 'V3': # reversed from normal
            getattr(GPI_driver, f'set_slow_valve_{valve_number}_trigger')(1)
        else:
            getattr(GPI_driver, f'set_slow_valve_{valve_number}_trigger')(0)
        #globals()[f'get_slow_status')](valve_number)
        globals()[f'slow_valve_{valve_number}_indicator'].itemconfig(globals()[f'slow_valve_{valve_number}_status'], fill='red')
        slow_win.destroy()
        
    confirm = tk.Button(slow_win, text='Confirm', width=10, command=slow_confirm)
    confirm.grid(row=1, column=0)
    cancel = tk.Button(slow_win, text='Cancel', width=10, command=slow_win.destroy)
    cancel.grid(row=1, column=1)
    

def print_check(check_number):
    if globals()[f'local_permission_{check_number}_var'].get():
        getattr(GPI_driver, f'set_fast_1_permission_{check_number}')(1)
    else:
        getattr(GPI_driver, f'set_fast_1_permission_{check_number}')(0)
        
        
def calc_clock_cycles(event):
    cycles_in_entry = int(int(timing_1_entry.get())/8e-9)
    cycles_in_duration = int(int(duration_1_entry.get())/8e-9)
    print(cycles_in_entry)
    print(cycles_in_duration)
    

if __name__ == '__main__':
    GPI_host = os.getenv('HOST', 'w7xrp1')
    GPI_client = koheron.connect(GPI_host, name='GPI_2')
    GPI_driver = koheron.GPI_2(GPI_client)

    root = tk.Tk()
    root.title('GPI Valve Control')

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

    image = Image.open('background.png')
    photo = ImageTk.PhotoImage(image)
    background = tk.Label(image=photo)
    background.image = photo
    background.grid(rowspan=10, columnspan=4)

    fast_valve_indicator = tk.Canvas(root,width=29, height=43)
    fast_valve_indicator.place(x=68, y=210)
    fast_valve_status = fast_valve_indicator.create_rectangle(0, 0, 29, 43)
    fast_valve_indicator.itemconfig(fast_valve_status, fill='red')

    # get_fast_valve_status()
    fast_valve_label_back = tk.Label(text='FV2', width=13)
    fast_valve_label_back.place(x=125, y=125)
        
    fast_valve_open_button = tk.Button(root, text='OPEN', fg='green', width=10, command=fast_valve_open)
    fast_valve_open_button.place(x=125, y=150)
    fast_valve_close_button = tk.Button(root, text='CLOSE', fg='red', width=10, command=fast_valve_close)
    fast_valve_close_button.place(x=125, y=180)

    slow_valve_1_indicator = tk.Canvas(root,width=29, height=43)
    slow_valve_1_indicator.place(x=417, y=464)
    slow_valve_1_status = slow_valve_1_indicator.create_rectangle(0, 0, 29, 43)
    slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill='red')

    get_slow_status(1)
    slow_valve_1_label_back = tk.Label(text='V5', width=13)
    slow_valve_1_label_back.place(x=475, y=380)

    slow_valve_1_open_button = tk.Button(root, text='OPEN', fg='green', width=10, command=lambda: slow_valve_open(1))
    slow_valve_1_open_button.place(x=475, y=405)
    slow_valve_1_close_button = tk.Button(root, text='CLOSE', fg='red', width=10, command=lambda: slow_valve_close(1))
    slow_valve_1_close_button.place(x=475, y=435)

    slow_valve_2_indicator = tk.Canvas(root,width=43, height=29)
    slow_valve_2_indicator.place(x=509, y=571)
    slow_valve_2_status = slow_valve_2_indicator.create_rectangle(0, 0, 43, 29)
    slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill='red')

    # get_slow_status(2)
    slow_valve_2_label_back = tk.Label(text='V4', width=13)
    slow_valve_2_label_back.place(x=310, y=545)
        
    slow_valve_2_open_button = tk.Button(root, text='OPEN', fg='green', width=10, command=lambda: slow_valve_open(2))
    slow_valve_2_open_button.place(x=310, y=570)
    slow_valve_2_close_button = tk.Button(root, text='CLOSE', fg='red', width=10, command=lambda: slow_valve_close(2)))
    slow_valve_2_close_button.place(x=310, y=600)

    slow_valve_3_indicator = tk.Canvas(root,width=43, height=29)
    slow_valve_3_indicator.place(x=661, y=374)
    slow_valve_3_status = slow_valve_3_indicator.create_rectangle(0, 0, 43, 29)
    slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill='green')

    # get_slow_status(3)
    slow_valve_3_label_back = tk.Label(text='V3', width=13)
    slow_valve_3_label_back.place(x=795, y=345)
        
    slow_valve_3_open_button = tk.Button(root, text='OPEN', fg='green', width=10, command=lambda: slow_valve_open(3))
    slow_valve_3_open_button.place(x=795, y=370)
    slow_valve_3_close_button = tk.Button(root, text='CLOSE', fg='red', width=10, command=lambda: slow_valve_close(3)))
    slow_valve_3_close_button.place(x=795, y=400)

    abs_gauge_label_back = tk.Label(text='Absolute Pressure Gauge')
    abs_gauge_label_back.place(x=605, y=5)
    diff_gauge_label_back = tk.Label(text='Differential Pressure Gauge')
    diff_gauge_label_back.place(x=855, y=170)

    abs_gauge_label = tk.Label(text='Absolute Pressure Gauge Reading:')
    abs_gauge_label.grid(row=0, column=4, columnspan=2)
    abs_gauge_graph = tk.Canvas(root, width=200, height=200, background='grey')
    abs_gauge_graph.grid(row=1, column=4, columnspan=2)

    diff_gauge_label = tk.Label(text='Differential Pressure Gauge Reading:')
    diff_gauge_label.grid(row=3, column=4, columnspan=2)
    diff_gauge_graph = tk.Canvas(root, width=200, height=200, background='grey')
    diff_gauge_graph.grid(row=4, column=4, columnspan=2)

    desired_pressure_label = tk.Label(text='Desired Pressure:')
    desired_pressure_label.grid(row=6, column=4)
    desired_pressure_entry = tk.Entry(root, width=10)
    desired_pressure_entry.grid(row=6, column=5)

    fill_button = tk.Button(root, text='Fill', width=10)
    fill_button.grid(row=7, column=4)

    pump_refill_button = tk.Button(root, text='Pump & Refill', width=10)
    pump_refill_button.grid(row=7, column=5)

    local_permission_1_label = tk.Label(text='Local Permission #1')
    local_permission_1_label.grid(row=10, column=0)
    timing_1_label = tk.Label(text='FV2 Opening Timing #1')
    timing_1_label.grid(row=11, column=0)
    duration_1_label = tk.Label(text='Opening Duration #1')
    duration_1_label.grid(row=12, column=0)

    local_permission_1_var = tk.IntVar()

    local_permission_1_check = tk.Checkbutton(root, variable=local_permission_1_var, command=lambda: print_check(1))
    local_permission_1_check.grid(row=10, column=1)
    timing_1_entry = tk.Entry(root, width=10)

    timing_1_entry.bind('<Return>', calc_clock_cycles)
    timing_1_entry.grid(row=11, column=1)
    duration_1_entry = tk.Entry(root, width=10)
    duration_1_entry.grid(row=12, column=1)
    duration_1_entry.bind('<Return>', calc_clock_cycles)

    local_permission_2_label = tk.Label(text='Local Permission #2')
    local_permission_2_label.grid(row=10, column=2)
    timing_2_label = tk.Label(text='FV2 Opening Timing #2')
    timing_2_label.grid(row=11, column=2)
    duration_2_label = tk.Label(text='Opening Duration #2')
    duration_2_label.grid(row=12, column=2)

    local_permission_2_var = tk.IntVar()

    local_permission_2_check = tk.Checkbutton(root, variable=local_permission_2_var, command=lambda: print_check(2))
    local_permission_2_check.grid(row=10, column=3)
    timing_2_entry = tk.Entry(root, width=10)
    timing_2_entry.grid(row=11, column=3)
    duration_2_entry = tk.Entry(root, width=10)
    duration_2_entry.grid(row=12, column=3)

    W7X_permission_label = tk.Label(text='W7-X Permission:')
    W7X_permission_label.grid(row=10, column=4)
    W7X_permission_status = tk.Label(text='Granted/Forbidden')
    W7X_permission_status.grid(row=10, column=5)

    GPI_safe_state_label = tk.Label(text='GPI Safe State:')
    GPI_safe_state_label.grid(row=12, column=4)
    GPI_safe_state_button = tk.Button(root, text='ENABLE', width=10)
    GPI_safe_state_button.grid(row=12, column=5)

    root.mainloop()
