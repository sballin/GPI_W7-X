'''
GUI for valve control in GPI system at W7-X.

Original code by Kevin Tang.
'''

from __future__ import print_function # for print to work inside lambda
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import koheron 
from GPI_2.GPI_2 import GPI_2


class DummyDriver(object):
    '''
    Lets the window open even if RP is not reachable.
    '''
    def __getattr__(self, name):
        def method(*args):
            return 0
        return method


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
        
        
def get_slow_status(valve_number):
    getter = getattr(GPI_driver, 'get_slow_%s_trigger' % valve_number)
    fill = 'green' if getter() else 'red'
    indicator = globals()['slow_valve_%s_indicator' % valve_number]
    status = globals()['slow_valve_%s_status' % valve_number]
    indicator.itemconfig(status, fill=fill)
    
    
def _confirm_window(question, action_if_confirmed):
    win = tk.Toplevel()
    win_width = 250
    win_height = 75
    x = (screen_width / 2) - (win_width / 2)
    y = (screen_height / 2) - (win_height / 2)
    win.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
    win.title('Confirm')
    win.rowconfigure(0, weight=1)
    win.rowconfigure(1, weight=1)
    win.columnconfigure(0, weight=1)
    win.columnconfigure(1, weight=1)
    msg = tk.Message(win, text=question, width=200)
    msg.grid(columnspan=2)
    
    def action_and_close():
        action_if_confirmed()
        win.destroy()
    
    confirm = tk.Button(win, text='Confirm', width=10, command=action_and_close)
    confirm.grid(row=1, column=0)
    cancel = tk.Button(win, text='Cancel', width=10, command=win.destroy)
    cancel.grid(row=1, column=1)


def toggle_valve(speed, valve_number, command, no_confirm=False):
    signal = 1              if command == 'open' else 0
    action_text = 'OPENING' if command == 'open' else 'CLOSING'
    fill = 'green'          if command == 'open' else 'red'
    
    if speed == 'slow':
        valve_name = ['V5', 'V4', 'V3'][valve_number - 1] 
    else:
        valve_name = 'FV2'
        
    if valve_name == 'V3': # this valve's signals are reversed relative to normal
        signal = int(not signal) 
        
    
    def action():
        # Send signal
        set_trigger = getattr(GPI_driver, 'set_%s_%s_trigger' % (speed, valve_number))
        set_trigger(signal)
            
        # Change indicator color
        if speed == 'slow':
            indicator = globals()['slow_valve_%s_indicator' % valve_number]
            status = globals()['slow_valve_%s_status' % valve_number]
            indicator.itemconfig(status, fill=fill)
        elif speed == 'fast':
            fast_valve_indicator.itemconfig(fast_valve_status, fill=fill)
            
    if no_confirm:
        action()
    else:
        _confirm_window('Please confirm the %s of %s.' % (action_text, valve_name), action)
        

def print_check(check_number):
    if globals()['local_permission_%s_var' % check_number].get():
        getattr(GPI_driver, 'set_fast_1_permission_%s' % check_number)(1)
    else:
        getattr(GPI_driver, 'set_fast_1_permission_%s' % check_number)(0)
        
        
def calc_clock_cycles(event):
    cycles_in_entry = int(int(timing_1_entry.get())/8e-9)
    cycles_in_duration = int(int(duration_1_entry.get())/8e-9)
    print(cycles_in_entry)
    print(cycles_in_duration)
    
    
def uint32_to_volts(reading):
    return .318+1.509*(20/(2**13-1)*signed_conversion(reading))
    
    
def abs_torr(rp1_reading):
    return 5000/10*uint32_to_volts(rp1_reading)
    
    
def diff_torr(rp2_reading):
    return 100/10*uint32_to_volts(rp2_reading)
    
    
def fill():
    desired_pressure = float(desired_pressure_entry.get())
    desired_volts = 10/5000*desired_pressure
    
    globals()['desired_pressure'] = desired_pressure
    globals()['filling'] = True
    
    
def pump_refill():
    globals()['pumping_down'] = True


def signed_conversion(reading):
    binNumber = "{0:014b}".format(int(reading))
    binConv = ""
    if int(binNumber[0], 2) == 1:
        for bit in binNumber[1::]:
            if bit == "1":
                binConv += "0"
            else:
                binConv += "1"
        intNum = -int(binConv, 2) - 1
    else:
        for bit in binNumber[1::]:
            binConv += bit
        intNum = int(binConv, 2)
    return intNum


if __name__ == '__main__':
    root = tk.Tk()
    try:
        GPI_host = os.getenv('HOST', 'w7xrp2')
        GPI_client = koheron.connect(GPI_host, name='GPI_2')
        GPI_driver = GPI_2(GPI_client)
        root.title('GPI Valve Control')
    except Exception as e:
        print(e)
        GPI_driver = DummyDriver()
        root.title('GPI Valve Control (NOT CONNECTED)')

    scale_down = 1.2
    win_width = int(1450/scale_down)
    win_height = int(880/scale_down)
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
    image = image.resize((int(1200/scale_down), int(768/scale_down)))
    photo = ImageTk.PhotoImage(image)
    background = tk.Label(image=photo)
    background.image = photo
    background.grid(rowspan=10, columnspan=4)

    fast_valve_indicator = tk.Canvas(root,width=29/scale_down, height=43/scale_down)
    fast_valve_indicator.place(x=68/scale_down, y=210/scale_down)
    fast_valve_status = fast_valve_indicator.create_rectangle(0, 0, int(29/scale_down), int(43/scale_down))
    fast_valve_indicator.itemconfig(fast_valve_status, fill='red')

    fast_valve_label_back = tk.Label(text='FV2', width=int(13/scale_down))
    fast_valve_label_back.place(x=125/scale_down, y=125/scale_down)
        
    fast_valve_open_button = tk.Button(root, text='OPEN', fg='green', width=int(10/scale_down), command=toggle_valve('fast', 1, 'open'))
    fast_valve_open_button.place(x=125/scale_down, y=150/scale_down)
    fast_valve_close_button = tk.Button(root, text='CLOSE', fg='red', width=int(10/scale_down), command=toggle_valve('fast', 1, 'close'))
    fast_valve_close_button.place(x=125/scale_down, y=180/scale_down)

    slow_valve_1_indicator = tk.Canvas(root,width=int(29/scale_down), height=int(43/scale_down))
    slow_valve_1_indicator.place(x=417/scale_down, y=464/scale_down)
    slow_valve_1_status = slow_valve_1_indicator.create_rectangle(0, 0, int(29/scale_down), int(43/scale_down))
    slow_valve_1_indicator.itemconfig(slow_valve_1_status, fill='red')

    get_slow_status(1)
    slow_valve_1_label_back = tk.Label(text='V5', width=int(13/scale_down))
    slow_valve_1_label_back.place(x=475/scale_down, y=380/scale_down)

    slow_valve_1_open_button = tk.Button(root, text='OPEN', fg='green', width=int(10/scale_down), command=lambda: toggle_valve('slow', 1, 'open'))
    slow_valve_1_open_button.place(x=475/scale_down, y=405/scale_down)
    slow_valve_1_close_button = tk.Button(root, text='CLOSE', fg='red', width=int(10/scale_down), command=lambda: toggle_valve('slow', 1, 'close'))
    slow_valve_1_close_button.place(x=475/scale_down, y=435/scale_down)

    slow_valve_2_indicator = tk.Canvas(root,width=int(43/scale_down), height=int(29/scale_down))
    slow_valve_2_indicator.place(x=509/scale_down, y=571/scale_down)
    slow_valve_2_status = slow_valve_2_indicator.create_rectangle(0, 0, int(43/scale_down), int(29/scale_down))
    slow_valve_2_indicator.itemconfig(slow_valve_2_status, fill='red')

    slow_valve_2_label_back = tk.Label(text='V4', width=int(13/scale_down))
    slow_valve_2_label_back.place(x=310/scale_down, y=545/scale_down)
        
    slow_valve_2_open_button = tk.Button(root, text='OPEN', fg='green', width=int(10/scale_down), command=lambda: toggle_valve('slow', 2, 'open'))
    slow_valve_2_open_button.place(x=310/scale_down, y=570/scale_down)
    slow_valve_2_close_button = tk.Button(root, text='CLOSE', fg='red', width=int(10/scale_down), command=lambda: toggle_valve('slow', 2, 'close'))
    slow_valve_2_close_button.place(x=310/scale_down, y=600/scale_down)

    slow_valve_3_indicator = tk.Canvas(root,width=int(43/scale_down), height=int(29/scale_down))
    slow_valve_3_indicator.place(x=661/scale_down, y=374/scale_down)
    slow_valve_3_status = slow_valve_3_indicator.create_rectangle(0, 0, int(43/scale_down), int(29/scale_down))
    slow_valve_3_indicator.itemconfig(slow_valve_3_status, fill='green')

    slow_valve_3_label_back = tk.Label(text='V3', width=int(13/scale_down))
    slow_valve_3_label_back.place(x=795/scale_down, y=345/scale_down)
        
    slow_valve_3_open_button = tk.Button(root, text='OPEN', fg='green', width=int(10/scale_down), command=lambda: toggle_valve('slow', 3, 'open'))
    slow_valve_3_open_button.place(x=795/scale_down, y=370/scale_down)
    slow_valve_3_close_button = tk.Button(root, text='CLOSE', fg='red', width=int(10/scale_down), command=lambda: toggle_valve('slow', 3, 'close'))
    slow_valve_3_close_button.place(x=795/scale_down, y=400/scale_down)

    abs_gauge_label_back = tk.Label(text='Absolute Pressure Gauge')
    abs_gauge_label_back.place(x=605/scale_down, y=5/scale_down)
    diff_gauge_label_back = tk.Label(text='Differential Pressure Gauge')
    diff_gauge_label_back.place(x=855/scale_down, y=170/scale_down)

    abs_gauge_label = tk.Label(text='Absolute Pressure Gauge Reading:\n0 Torr')
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

    fill_button = tk.Button(root, text='Fill', width=10, command=fill)
    fill_button.grid(row=7, column=4)

    pump_refill_button = tk.Button(root, text='Pump & Refill', width=10, command=pump_refill)
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
    
    desired_pressure = 0
    filling = False
    pumping_down = False
    last_voltage = 0
    average_samples = 100

    while True:
        readings = list(zip(*[(GPI_driver.get_abs_gauge(),
                               GPI_driver.get_diff_gauge()) 
                              for i in range(average_samples)]))
        abs_reading = sum(readings[0])/len(readings[0])
        abs_voltage = uint32_to_volts(int(abs_reading))
        abs_pressure = abs_torr(abs_reading)
        print(abs_reading, signed_conversion(abs_reading), abs_voltage, abs_pressure)
        
        diff_reading = sum(readings[1])/len(readings[1])
        diff_pressure = diff_torr(diff_reading)
        abs_gauge_label['text'] = 'Absolute Pressure Gauge Reading:\n%f Torr' % abs_pressure
        diff_gauge_label['text'] = 'Diff Pressure Gauge Reading:\n%f Torr' % diff_pressure
        
        if filling:
            sleep_seconds = 0.2
            if abs_pressure > 0 and desired_pressure > 0:
                if abs_pressure < desired_pressure:
                    if not GPI_driver.get_slow_1_trigger():
                        toggle_valve('slow', 1, 'open', no_confirm=True)
                elif abs_pressure > 0.97*desired_pressure:
                    toggle_valve('slow', 1, 'close', no_confirm=True)
                    filling = False
            else:
                filling = False
        else:
            sleep_seconds = 1
        
        if pumping_down:
            sleep_seconds = 0.2
            if abs_pressure > 0 and desired_pressure > 0:                    
                if not GPI_driver.get_slow_2_trigger():
                    toggle_valve('slow', 2, 'open', no_confirm=True)
                if (abs_voltage < 0.02 and last_voltage < 0.02) or \
                   abs_pressure < desired_pressure:
                    toggle_valve('slow', 2, 'close', no_confirm=True)
                    pumping_down = False
                    filling = True
                    sleep_seconds = 1
        
        last_voltage = abs_voltage
        time.sleep(sleep_seconds)
        root.update_idletasks()
        root.update()
