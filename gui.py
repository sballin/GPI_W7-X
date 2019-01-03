'''
GUI for valve control in GPI system at W7-X. Original code by Kevin Tang.

Architecture
------------
- manage_pressures thread records fast and averaged pressure readings
- manage_plots thread updates plots when required
'''

from __future__ import print_function # for print to work inside lambda
import tkinter as tk
from PIL import Image, ImageTk
import os
import time
import threading
import koheron 
from GPI_2.GPI_2 import GPI_2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


UPDATE_INTERVAL = 1 # seconds between plot updates
PLOT_TIME_RANGE = 30 # seconds of history shown in plots


def uint32_to_volts(reading):
    measured=(2/(2**14-1)*signed_conversion(reading))
    #return 0.0661+4.526*measured # for 1 V jumper and the 0.252 voltage divider
    #return 0.01097+1.135*measured  # for 1V jumper and no voltage divider
    #return 0.3917+1.448*measured # for 20V jumper
    return measured #to return the the RP measured voltage (no calibration)                  
    #return (20./(2**13-1)*signed_conversion(reading)) # first 1 should be changed to 20 if the jumper is toggled
    
        
def signed_conversion(reading):
    binNumber = "{0:014b}".format(int(round(reading)))
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
    
    
def find_nearest(array, value):
    '''
    Find index of first value in ORDERED array closest to given value.
    Parameters
        array: NumPy array
        value: int or float
    Returns
        int: argument of array value closest to value supplied
    '''
    idx = np.searchsorted(array, value, side='left')
    if idx > 0 and (idx == len(array) or np.fabs(value - array[idx-1]) < np.fabs(value - array[idx])):
        return idx-1
    else:
        return idx
           
    
class FakeRedPitaya(object):
    '''
    Lets the GUI window open even if Red Pitaya is not reachable.
    '''
    def __getattr__(self, name):
        '''
        Returns 0 for all Red Pitaya functions instead of raising errors.
        '''
        def method(*args):
            return 0
        return method


class GUI:
    def __init__(self, root):
        self.root = root
        try:
            GPI_host = os.getenv('HOST', 'w7xrp2')
            GPI_client = koheron.connect(GPI_host, name='GPI_2')
            self.GPI_driver = GPI_2(GPI_client)
            self.root.title('GPI Valve Control')
        except Exception as e:
            print(e)
            self.GPI_driver = FakeRedPitaya()
            self.root.title('GPI Valve Control (RED PITAYA NOT FOUND)')

        win_width = int(1200)
        win_height = int(880)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        x = (self.screen_width / 2) - (win_width / 2)
        y = (self.screen_height / 2) - (win_height / 2)
        self.root.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
        # weight=1 means the element stretches with window resize, weight=0 (default) means its size stays fixed
        self.root.columnconfigure(4, weight=1)
        self.root.columnconfigure(5, weight=1)
        self.root.rowconfigure(10, weight=1)
        self.root.rowconfigure(11, weight=1)
        self.root.rowconfigure(12, weight=1)
        
        self.root.protocol('WM_DELETE_WINDOW', self._quit_tkinter)

        image = Image.open('background.png')
        image = image.resize((int(768/2), int(1200/2)))
        photo = ImageTk.PhotoImage(image)
        background = tk.Label(image=photo)
        background.image = photo
        background.grid(rowspan=10, columnspan=4)

        self.FV2_indicator = tk.Label(self.root,width=3, height=1, text='FV2', fg='white', bg='red')
        self.FV2_indicator.place(x=323, y=100)
        # self.fast_valve_status = self.FV_indicator.create_rectangle(0, 0, int(29/scale_down), int(43/scale_down))
        # self.FV_indicator.itemconfig(self.fast_valve_status, fill='red')
        # self.FV_indicator.create_text(12, 8, text='FV2', anchor='nw', fill='white')
        self.FV2_indicator.bind("<Button-1>", lambda event: self.toggle_valve('FV2', 'open', no_confirm=True))

        self.V5_indicator = tk.Label(self.root, width=2, height=1, text='V5', fg='white', bg='red')
        self.V5_indicator.place(x=200, y=275)
        self.V5_indicator.bind("<Button-1>", lambda event: self.toggle_valve('V5', 'open', no_confirm=True))

        self.V4_indicator = tk.Label(self.root, width=1, height=1, text='V4', fg='white', bg='red')
        self.V4_indicator.place(x=154, y=323)
        self.V4_indicator.bind("<Button-1>", lambda event: self.toggle_valve('V4', 'open', no_confirm=True))

        self.V3_indicator = tk.Label(self.root, width=2, height=1, text='V3', fg='white', bg='green')
        self.V3_indicator.place(x=250, y=400)
        self.V3_indicator.bind("<Button-1>", lambda event: self.toggle_valve('FV3', 'open', no_confirm=True))

        # abs_gauge_label = tk.Label(text='Absolute Pressure Gauge Reading:\n0 Torr')
        # abs_gauge_label.grid(row=0, column=4, columnspan=2)
        # self.pressure_plot = tk.Canvas(self.root, width=300, height=300, background='grey')
        # self.pressure_plot.grid(row=1, column=4, columnspan=2)

        # diff_gauge_label = tk.Label(text='Differential Pressure Gauge Reading:')
        # diff_gauge_label.grid(row=3, column=4, columnspan=2)

        desired_pressure_label = tk.Label(text='Desired Pressure:')
        desired_pressure_label.grid(row=6, column=4)
        desired_pressure_entry = tk.Entry(self.root, width=10)
        desired_pressure_entry.grid(row=6, column=5)

        fill_button = tk.Button(self.root, text='Fill', width=10, command=self.fill)
        fill_button.grid(row=7, column=4)

        pump_refill_button = tk.Button(self.root, text='Pump & Refill', width=10, command=self.pump_refill)
        pump_refill_button.grid(row=7, column=5)

        local_permission_1_label = tk.Label(text='Local Permission #1')
        local_permission_1_label.grid(row=10, column=0)
        timing_1_label = tk.Label(text='FV2 Opening Timing #1')
        timing_1_label.grid(row=11, column=0)
        duration_1_label = tk.Label(text='Opening Duration #1')
        duration_1_label.grid(row=12, column=0)

        self.local_permission_1_var = tk.IntVar()

        local_permission_1_check = tk.Checkbutton(self.root, variable=self.local_permission_1_var, command=lambda: self.toggle_permission(1))
        local_permission_1_check.grid(row=10, column=1)
        self.timing_1_entry = tk.Entry(self.root, width=10)

        self.timing_1_entry.bind('<Return>', self.calc_clock_cycles)
        self.timing_1_entry.grid(row=11, column=1)
        duration_1_entry = tk.Entry(self.root, width=10)
        duration_1_entry.grid(row=12, column=1)
        duration_1_entry.bind('<Return>', self.calc_clock_cycles)

        local_permission_2_label = tk.Label(text='Local Permission #2')
        local_permission_2_label.grid(row=10, column=2)
        timing_2_label = tk.Label(text='FV2 Opening Timing #2')
        timing_2_label.grid(row=11, column=2)
        duration_2_label = tk.Label(text='Opening Duration #2')
        duration_2_label.grid(row=12, column=2)

        self.local_permission_2_var = tk.IntVar()

        local_permission_2_check = tk.Checkbutton(self.root, variable=self.local_permission_2_var, command=lambda: self.toggle_permission(2))
        local_permission_2_check.grid(row=10, column=3)
        self.timing_2_entry = tk.Entry(self.root, width=10)
        self.timing_2_entry.grid(row=11, column=3)
        self.duration_2_entry = tk.Entry(self.root, width=10)
        self.duration_2_entry.grid(row=12, column=3)

        W7X_permission_label = tk.Label(text='W7-X Permission:')
        W7X_permission_label.grid(row=10, column=4)
        W7X_permission_status = tk.Label(text='Granted/Forbidden')
        W7X_permission_status.grid(row=10, column=5)

        GPI_T0_button = tk.Button(self.root, text='T0 trigger', width=10, command=self.puff)
        GPI_T0_button.grid(row=11, column=5)
        
        GPI_safe_state_label = tk.Label(text='GPI Safe State:')
        GPI_safe_state_label.grid(row=12, column=4)
        GPI_safe_state_button = tk.Button(self.root, text='ENABLE', width=10)
        GPI_safe_state_button.grid(row=12, column=5)
        
        self.gpi_routine_executing = False
        self.plots_need_update = True #False
        
        self.pressure_times = []
        self.abs_pressures = []
        self.diff_pressures = []
        self.pressure_avg_times = []
        self.abs_avg_pressures = []
        self.diff_avg_pressures = []

        self.manage_pressures_thread = threading.Thread(target=self.manage_pressures, daemon=True)
        self.manage_pressures_thread.start()
        
        self.fig = Figure(figsize=(3,6))
        self.fig.subplots_adjust(left=0.2)
        # Absolute pressure plot matplotlib setup
        self.ax_abs = self.fig.add_subplot(211)
        self.ax_abs.set_ylabel('Pressure (Torr)')
        # Differential pressure plot matplotlib setup
        self.ax_diff = self.fig.add_subplot(212)
        self.setup_plots()
        # Plot tkinter setup
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=4, columnspan=2)
        
        # Start plotting thread
        self.manage_plots_thread = threading.Thread(target=self.manage_plots, daemon=True)
        self.manage_plots_thread.start()

        # while True:
            # x = root.winfo_pointerx()
            # y = root.winfo_pointery()
            # abs_coord_x = root.winfo_pointerx() - root.winfo_rootx()
            # abs_coord_y = root.winfo_pointery() - root.winfo_rooty()
            # print(abs_coord_x, abs_coord_y)
            
            # if self.pressure_avg_times:
            #     abs_gauge_label['text'] = 'Absolute Pressure Gauge Reading:\n%f Torr' % self.abs_avg_pressures[-1]
            #     diff_gauge_label['text'] = 'Diff Pressure Gauge Reading:\n%f Torr' % self.diff_avg_pressures[-1]

            # now = time.time()
            # abs_pressure_plot.append(abs_pressure)
            # diff_pressure_plot.append(diff_pressure)

            
    #         if filling:
    #             sleep_seconds = 0.2
    #             if abs_pressure > 0 and desired_pressure > 0:
    #                 if abs_pressure < desired_pressure:
    #                     if not self.GPI_driver.get_slow_1_trigger():
    #                         self.toggle_valve('V5', 'open', no_confirm=True)
    #                 elif abs_pressure > 0.97*desired_pressure:
    #                     self.toggle_valve('V5', 'close', no_confirm=True)
    #                     filling = False
    #             else:
    #                 filling = False
    #         else:
    #             sleep_seconds = 1
            
    #         if pumping_down:
    #             sleep_seconds = 0.2
    #             if abs_pressure > 0 and desired_pressure > 0:                    
    #                 if not self.GPI_driver.get_slow_2_trigger():
    #                     self.toggle_valve('V4', 'open', no_confirm=True)
    #                 if (abs_voltage < 0.02 and last_voltage < 0.02):# or \
    # #                   abs_pressure < desired_pressure:
    #                     self.toggle_valve('V4', 'close', no_confirm=True)
    #                     pumping_down = False
    #                     filling = True
    #                     sleep_seconds = 1
            
    #         last_voltage = abs_voltage
            # time.sleep(sleep_seconds)
            
        # while True:
        #     # self.canvas.draw()
        #     # Required for tkinter 
        #     self.root.update_idletasks()
        #     self.root.update()
        #     time.sleep(1)

    def _quit_tkinter(self):
        self.root.quit()     # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def abs_torr(self):
        abs_counts = self.GPI_driver.get_abs_gauge()
        abs_voltage = 0.0661+4.526*uint32_to_volts(abs_counts) # calibration for IN 1 of W7XRP2 with a 0.252 divider 
        return 5000/10*abs_voltage

    def diff_torr(self):
        diff_counts = self.GPI_driver.get_diff_gauge()
        diff_voltage = 0.047+3.329*uint32_to_volts(diff_counts) # calibration for IN 2 of W7XRP2 with a 0.342 divider
        return 100/10*diff_voltage
            
    def manage_pressures(self):
        last_number_crunch = 0
        while True:
            time.sleep(1e-4) # REMOVE FOR REAL RED PITAYA
            self.pressure_times.append(time.time())
            
            # Append pressure readings to fast timeseries
            self.abs_pressures.append(self.abs_torr())
            self.diff_pressures.append(self.diff_torr())
            
            now = time.time()
            if now - last_number_crunch > UPDATE_INTERVAL:
                if not self.gpi_routine_executing:
                    # Remove fast readings older than PLOT_TIME_RANGE seconds
                    pressures_start = find_nearest(np.array(self.pressure_times)-now, -PLOT_TIME_RANGE)
                    self.pressure_times = self.pressure_times[pressures_start:]
                    self.abs_pressures = self.abs_pressures[pressures_start:]
                    self.diff_pressures = self.diff_pressures[pressures_start:]
                    
                    # Remove average readings older than PLOT_TIME_RANGE seconds
                    avgs_start = find_nearest(np.array(self.pressure_avg_times)-now, -PLOT_TIME_RANGE)
                    self.pressure_avg_times = self.pressure_avg_times[avgs_start:]
                    self.abs_avg_pressures = self.abs_avg_pressures[avgs_start:]
                    self.diff_avg_pressures = self.diff_avg_pressures[avgs_start:]
                
                # Append new average reading
                interval_start = find_nearest(np.array(self.pressure_times)-now, -UPDATE_INTERVAL)
                # print('len pressures', len(self.pressure_times), 
                #       'earliest time', now-self.pressure_times[0], 
                #       'avg samples', len(self.pressure_times)-interval_start, 
                #       'avg start time', self.pressure_times[interval_start]-now, sep='\t')
                avg_time = np.mean(self.pressure_times[interval_start:])
                abs_avg_pressure = np.mean(self.abs_pressures[interval_start:])
                diff_avg_pressure = np.mean(self.diff_pressures[interval_start:])
                self.pressure_avg_times.append(avg_time)
                self.abs_avg_pressures.append(abs_avg_pressure)
                self.diff_avg_pressures.append(diff_avg_pressure)
                
                self.plots_need_update = True
                last_number_crunch = now
                # print('{: >10} {: >10} {: >10}'
                #       .format(len(self.pressure_avg_times), 
                #               round(now-self.pressure_avg_times[0], 2),
                #               round(now-self.pressure_avg_times[-1],2)))
                
    def setup_plots(self):
        relative_times = self.rel_avg_times
        self.ax_abs.set_title('Absolute gauge pressure')
        self.ax_abs.set_ylabel('Torr', weight='bold')
        plt.setp(self.ax_abs.get_xticklabels(), visible=False)
        self.ax_abs.grid(True)
        self.ax_diff.set_title('Differential gauge pressure')
        self.ax_diff.set_ylabel('Torr', weight='bold')
        self.ax_diff.set_xlabel('Seconds', weight='bold')
        self.ax_abs.plot(relative_times, self.abs_avg_pressures, c='C0')
        self.ax_diff.plot(relative_times, self.diff_avg_pressures, c='C1')
        self.ax_diff.grid(True)
        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=10.0)
                
    def manage_plots(self):
        '''
        TODO: optimization if the lines don't need to be completely redrawn (will probably have to set xlim and ylim too)
        '''
        while True:
            if self.plots_need_update:
                relative_times = self.rel_avg_times
                self.ax_diff.cla()
                self.ax_abs.cla()
                self.setup_plots()
                self.fig.canvas.draw_idle()
                self.plots_need_update = False
    
    @property
    def rel_avg_times(self):
        now = time.time()
        return [t - now for t in self.pressure_avg_times]
            
    @property 
    def pt1(self):
        return self.timing_1_entry.get()
        
    @property 
    def pt2(self):
        return self.timing_2_entry.get()

    def _confirm_window(self, question, action_if_confirmed):
        win = tk.Toplevel()
        win_width = 250
        win_height = 75
        x = (self.screen_width / 2) - (win_width / 2)
        y = (self.screen_height / 2) - (win_height / 2)
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

    def toggle_valve(self, valve_name, command, no_confirm=False):
        signal =      1         if command == 'open' else 0
        action_text = 'OPENING' if command == 'open' else 'CLOSING'
        fill =        'green'   if command == 'open' else 'red'
        
        if valve_name == 'FV2':
            speed = 'fast'
            valve_number = 1
        else:
            speed = 'slow'
            valve_number = ['V5', 'V4', 'V3'].index(valve_name) + 1
            
        if valve_name == 'V3': # this valve's signals are reversed relative to normal
            signal = int(not signal)
        
        def action():
            # Send signal
            set_trigger = getattr(self.GPI_driver, 'set_%s_%s_trigger' % (speed, valve_number))
            set_trigger(signal)
            
            # Change indicator color    
            getattr(self, '%s_indicator' % valve_name).config(bg=fill)
                
        if no_confirm:
            action()
        else:
            self._confirm_window('Please confirm the %s of %s.' % (action_text, valve_name), action)
            
    def toggle_permission(self, puff_number):
        permission = getattr(self, 'local_permission_%d_var' % puff_number).get()
        getattr(self.GPI_driver, 'set_fast_%d_permission' % puff_number)(int(permission))

    def print_check(self, check_number):
        if globals()['local_permission_%s_var' % check_number].get():
            getattr(self.GPI_driver, 'set_fast_1_permission_%s' % check_number)(1)
        else:
            getattr(self.GPI_driver, 'set_fast_1_permission_%s' % check_number)(0)
            
    def calc_clock_cycles(self, event):
        cycles_in_entry = int(int(self.timing_1_entry.get())/8e-9)
        cycles_in_duration = int(int(self.duration_1_entry.get())/8e-9)
        print(cycles_in_entry)
        print(cycles_in_duration)
        
    def fill(self):
        desired_pressure = float(desired_pressure_entry.get())
        desired_volts = 10/5000*desired_pressure
        
        self.desired_pressure = desired_pressure
        self.filling = True
        
    def pump_refill(self):
        self.pumping_down = True
        
    def puff(self):
        pt1 = self.timing_1_entry.get()
        pt1p = self.local_permission_1_var.get()
        pt2 = self.timing_2_entry.get()
        pt2p = self.local_permission_2_var.get()
        if (pt1 and pt1p) or (pt2 and pt2p):
            self.timing_1_entry.config(state='disabled')
            self.timing_2_entry.config(state='disabled')
            
            # Convert the puff times into floats 
            never = 1e10
            pt1 = float(pt1) if pt1 else never
            pt2 = float(pt2) if pt2 else never
            
            # Loop until all actions are completed while monitoring diff pressure
            donePrep = doneT1 = donePuff1 = doneClose1 = donePuff2 = doneClose2 = doneSave = False
            closeTime = never
            FVduration = 0.1
            T0 = time.time()
            T1relative = 10
            T1 = T0+T1relative
            diffPressure = []
            diffPressureTimes = []
            print('T0 received, T1 in',T1relative)
            while not (donePrep and doneT1 and donePuff1 and doneClose1 
                       and donePuff2 and doneClose2 and doneSave):
                t = time.time()
                if not donePrep and t > T1-5+min(pt1, pt2):    
                    print('T0 +', t-T0, 'closing V3')
                    self.toggle_valve('V3', 'close', no_confirm=True)
                    # Set fast timings in milliseconds
                    if pt1p and pt1p < never:
                        self.GPI_driver.set_fast_1_trigger(pt1*1000) 
                        self.GPI_driver.set_fast_1_duration(FVduration*1000)
                    if pt2p and pt2 < never:
                        self.GPI_driver.set_fast_2_trigger(pt2*1000)
                        self.GPI_driver.set_fast_2_duration(FVduration*1000)
                    self.GPI_driver.reset_time(max(pt1+FVduration, pt2+FVduration)*1000)
                    donePrep = True
                
                if not doneT1 and t > T1:
                    print('T0 +', t-T0, 'T1 should have been received')
                    doneT1 = True
                
                if pt1p and pt1 < never:
                    t = time.time()
                    if not donePuff1 and t > T1+pt1:
                        print('T1 +', t-T1, 'FV should have opened')
                        donePuff1 = True
                    if not doneClose1 and t > T1+pt1+FVduration:
                        print('T1 +', t-T1, 'FV should have closed')
                        doneClose1 = True
                        closeTime = t
                else:
                    donePuff1 = True
                    doneClose1 = True
                if pt2p and pt2 < never:
                    t = time.time()
                    if not donePuff2 and t > T1+pt2:
                        print('T1 +', t-T1, 'FV should have opened')
                        donePuff2 = True
                    if not doneClose2 and t > T1+pt2+FVduration:
                        print('T1 +', t-T1, 'FV should have closed')
                        doneClose2 = True
                        closeTime = t
                else:
                    donePuff2 = True
                    doneClose2 = True
                
                if not doneSave and t > closeTime + 5:
                    np.save('diff_pressures/diff_pressure_%d.npy' % int(t), [diffPressureTimes, diffPressure])
                    # matplotlib.use('Agg')
                    plt.plot(diffPressureTimes, diffPressure)
                    plt.xlabel('t-T1 (s)')
                    plt.ylabel('Diff. pressure (Torr)')
                    plt.savefig('diff_pressures/diff_pressure_%d.png' % int(t))
                    doneSave = True
                diffPressureTimes.append(time.time()-T1)
                diffPressure.append(self.GPI_driver.get_diff_gauge())
            self.toggle_valve('V3', 'open', no_confirm=True)
            self.timing_1_entry.config(state='normal')
            self.timing_2_entry.config(state='normal')

 
if __name__ == '__main__':
    tkRoot = tk.Tk()
    main_ui = GUI(tkRoot)
    tkRoot.mainloop()
