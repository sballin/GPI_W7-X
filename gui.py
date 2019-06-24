'''
GUI for valve control in GPI system at W7-X. Original code by Kevin Tang.

FUTURE TODO: how to handle long puff delays
'''

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import math
import datetime
import koheron 
from GPI_RP.GPI_RP import GPI_RP
import numpy as np
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.signal import medfilt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


HOST = 'w7xrp2' # hostname of red pitaya being used
UPDATE_INTERVAL = 1  # seconds between plot updates
CONTROL_INTERVAL = 0.2 # seconds between pump/fill loop iterations
PLOT_TIME_RANGE = 30 # seconds of history shown in plots
DEFAULT_PUFF = 0.05  # seconds duration for each puff 
PRETRIGGER = 10 # seconds between T0 and T1
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
MECH_PUMP_LIMIT = 750 # Torr, max pressure the mechanical pump should work on
PUMPED_OUT = 0 # Torr, desired pumped out pressure
SAVE_FOLDER = '/usr/local/cmod/codes/spectroscopy/gpi/W7X/diff_pressures/' # for puff pressure data


def int_to_float(reading):
    return 2/(2**14-1)*signed_conversion(reading)
    
    
def signed_conversion(reading):
    '''
    Convert Red Pitaya binary output to a uint32.
    '''
    binConv = ''
    if int(reading[0], 2) == 1:
        for bit in reading[1::]:
            if bit == '1':
                binConv += '0'
            else:
                binConv += '1'
        intNum = -int(binConv, 2) - 1
    else:
        for bit in reading[1::]:
            binConv += bit
        intNum = int(binConv, 2)
    return intNum
    
    
def abs_bin_to_torr(binary_string):
    # Calibration for IN 1 of W7XRP2 with a 0.252 divider 
    abs_voltage = 0.0661+4.526*int_to_float(binary_string) # 
    # 500 Torr/Volt
    return 500*abs_voltage
    
    
def diff_bin_to_torr(binary_string):
    # Calibration for IN 2 of W7XRP2 with a 0.342 divider
    diff_voltage = 0.047+3.329*int_to_float(binary_string) 
    # 10 Torr/Volt
    return 10*diff_voltage
    
    
def abs_torr(combined_string):
    abs_binary_string = '{0:032b}'.format(combined_string)[-28:-14]
    return abs_bin_to_torr(abs_binary_string)
    
    
def diff_torr(combined_string):
    diff_binary_string = '{0:032b}'.format(combined_string)[-14:]
    return diff_bin_to_torr(diff_binary_string)
    
    
def find_nearest(array, value):
    '''
    Find index of first value in an ORDERED array closest to given value.
    Parameters
        array: NumPy array
        value: int or float
    Returns
        int: argument of array value closest to value supplied
    '''
    idx = np.searchsorted(array, value, side='left')
    if idx > 0 and (idx == len(array) or np.fabs(value - array[idx-1]) < np.fabs(value - array[idx])):
        return idx-1
    return idx
        
        
class FakeRedPitaya(object):
    '''
    Lets the GUI window open even if Red Pitaya cannot be reached.
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
        self.root.title('GPI Valve Control')
        win_width = int(1130)
        win_height = int(600)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        x = (self.screen_width / 2) - (win_width / 2)
        y = (self.screen_height / 2) - (win_height / 2)
        self.root.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
        self.root.protocol('WM_DELETE_WINDOW', self._quit_tkinter)
        s=ttk.Style()
        s.theme_use('alt')
        gray = '#A3A3A3'
        self.root.config(background=gray)
        
        system_frame = tk.Frame(self.root, background=gray)
        image = Image.open('background.png')
        #image = image.resize((469, 600)) # I just resized the actual image
        photo = ImageTk.PhotoImage(image)
        background = tk.Label(system_frame, image=photo)
        background.image = photo
        background.configure(background=gray)

        self.FV2_indicator = tk.Label(system_frame, width=3, height=1, text='FV2', fg='white', bg='red')
        self.FV2_indicator.bind("<Button-1>", lambda event: self.handle_valve('FV2'))

        self.V5_indicator = tk.Label(system_frame, width=2, height=1, text='V5', fg='white', bg='red')
        self.V5_indicator.bind("<Button-1>", lambda event: self.handle_valve('V5'))

        self.V4_indicator = tk.Label(system_frame, width=1, height=1, text='V4', fg='white', bg='red')
        self.V4_indicator.bind("<Button-1>", lambda event: self.handle_valve('V4'))

        self.V3_indicator = tk.Label(system_frame, width=2, height=1, text='V3', fg='white', bg='green')
        self.V3_indicator.bind("<Button-1>", lambda event: self.handle_valve('V3'))
        
        self.V7_indicator = tk.Label(system_frame, width=2, height=1, text='V7', fg='white', bg='red')
        self.V7_indicator.bind("<Button-1>", lambda event: self.handle_valve('V7'))

        self.abs_gauge_label = tk.Label(system_frame, text='0\nTorr', bg='#004DD4', fg='white', justify=tk.LEFT)
        self.diff_gauge_label = tk.Label(system_frame, text='0\nTorr', bg='#DF7D00', fg='white', justify=tk.LEFT)

        controls_frame = tk.Frame(self.root, background=gray)
        fill_controls_frame = tk.Frame(controls_frame, background=gray)
        fill_controls_line1 = tk.Frame(fill_controls_frame, background=gray, pady=5)
        desired_pressure_label = tk.Label(fill_controls_line1, text='Desired pressure (Torr):', background=gray)
        self.desired_pressure_entry = ttk.Entry(fill_controls_line1, width=10, background=gray)

        fill_controls_line2 = tk.Frame(fill_controls_frame, background=gray)
        fill_button = ttk.Button(fill_controls_line2, text='Fill', command=self.handle_fill)
        pump_refill_button = ttk.Button(fill_controls_line2, text='Pump down and refill', command=self.handle_pump_refill)

        self.permission_1 = tk.IntVar()
        puff_controls_frame = tk.Frame(controls_frame, background=gray)
        self.permission_1_check = tk.Checkbutton(puff_controls_frame, variable=self.permission_1, command=lambda: self.handle_permission(1), background=gray)
        self.start_1_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_1_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_1_entry.insert(0, str(DEFAULT_PUFF))

        self.permission_2 = tk.IntVar()
        self.permission_2_check = tk.Checkbutton(puff_controls_frame, variable=self.permission_2, command=lambda: self.handle_permission(2), background=gray)
        self.start_2_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_2_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_2_entry.insert(0, str(DEFAULT_PUFF))
        
        permission_controls_frame = tk.Frame(controls_frame, background=gray)
        W7X_permission_label = tk.Label(permission_controls_frame, text='W7-X permission', background=gray)
        W7X_permission_check = tk.Checkbutton(permission_controls_frame, background=gray, state=tk.DISABLED)
        
        GPI_safe_state_label = tk.Label(permission_controls_frame, text='GPI safe state', background=gray)
        self.GPI_safe_status = tk.IntVar()
        GPI_safe_state_check = tk.Checkbutton(permission_controls_frame, background=gray, command=self.handle_safe_state, variable=self.GPI_safe_status)
        
        action_controls_frame = tk.Frame(controls_frame, background=gray)
        GPI_T0_button = ttk.Button(action_controls_frame, text='T0 trigger', width=10, command=self.handle_T0)
        
        self.pressure_times = []
        self.abs_pressures = []
        self.diff_pressures = []
        self.pressure_avg_times = []
        self.abs_avg_pressures = []
        self.diff_avg_pressures = []
        
        self.fig = Figure(figsize=(3.5, 6), dpi=100, facecolor=gray)
        self.fig.subplots_adjust(left=0.2)
        # Absolute pressure plot matplotlib setup
        self.ax_abs = self.fig.add_subplot(211)
        # Differential pressure plot matplotlib setup
        self.ax_diff = self.fig.add_subplot(212)
        # Plot tkinter setup
        self.fig.set_tight_layout(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        
        # I use this to figure out valve label positions
        # def click_location(event):
        #     print('%.4f, %.4f' % (event.x/469, event.y/600)) # divide by image dimensions
        # self.root.bind('<Button-1>', click_location)
        
        # GUI element placement
        ## Column 1
        background.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.V3_indicator.place(relx=.476, rely=.562, relwidth=.034, relheight=.038)
        self.V4_indicator.place(relx=.092, rely=.395, relwidth=.036, relheight=.038)
        self.V5_indicator.place(relx=.364, rely=.315, relwidth=.047, relheight=.026)
        self.V7_indicator.place(relx=.204, rely=.277, relwidth=.03, relheight=.028)
        self.FV2_indicator.place(relx=.635, rely=.067, relwidth=.05, relheight=.026)
        self.abs_gauge_label.place(relx=.883, rely=.545)
        self.diff_gauge_label.place(relx=.605, rely=.761)
        system_frame.pack(side=tk.LEFT)
        ## Column 2
        self.canvas.get_tk_widget().pack(side=tk.LEFT)
        self.canvas.get_tk_widget().configure()
        ## Column 3
        ### Fill controls frame
        desired_pressure_label.pack(side=tk.LEFT)
        self.desired_pressure_entry.pack(side=tk.LEFT)
        fill_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        pump_refill_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        fill_controls_line1.pack(side=tk.TOP, fill=tk.X)
        fill_controls_line2.pack(side=tk.TOP, fill=tk.X)
        fill_controls_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### Puff controls frame
        tk.Label(puff_controls_frame, text='Permission', background=gray).grid(row=0, column=7)
        tk.Label(puff_controls_frame, text='Start (s)', background=gray).grid(row=0, column=8)
        tk.Label(puff_controls_frame, text='Duration (s)', background=gray).grid(row=0, column=9)
        tk.Label(puff_controls_frame, text='Puff 1', background=gray).grid(row=1, column=6)
        tk.Label(puff_controls_frame, text='Puff 2', background=gray).grid(row=2, column=6)
        self.permission_1_check.grid(row=1, column=7)
        self.start_1_entry.grid(row=1, column=8)
        self.duration_1_entry.grid(row=1, column=9)
        self.permission_2_check.grid(row=2, column=7)
        self.start_2_entry.grid(row=2, column=8)
        self.duration_2_entry.grid(row=2, column=9)
        puff_controls_frame.pack(side=tk.TOP, pady=10, fill=tk.X)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### Permission controls frame
        W7X_permission_label.pack(side=tk.LEFT)
        W7X_permission_check.pack(side=tk.LEFT)
        GPI_safe_state_label.pack(side=tk.LEFT)
        GPI_safe_state_check.pack(side=tk.LEFT)
        permission_controls_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### Action controls frame
        GPI_T0_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        action_controls_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### Log
        log_controls_frame = tk.Frame(controls_frame, background=gray)
        label_log_controls_frame = tk.Frame(log_controls_frame, background=gray)
        tk.Label(label_log_controls_frame, text='Event log', background=gray).pack(side=tk.LEFT, fill=tk.X)
        label_log_controls_frame.pack(side=tk.TOP, fill=tk.X)
        self.log = tk.Listbox(log_controls_frame, background=gray, highlightbackground=gray)
        self.log.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        log_controls_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10, expand=True)
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self._add_to_log('GUI initialized')
        
        try:
            GPI_host = os.getenv('HOST', HOST)
            GPI_client = koheron.connect(GPI_host, name='GPI_RP')
            self._add_to_log('Connected to Red Pitaya')
            self.RP_driver = GPI_RP(GPI_client)
        except Exception as e:
            print(e)
            self.RP_driver = FakeRedPitaya()
            self._add_to_log('Red Pitaya unreachable - simulating...')
        
        self.last_plot = None
        self.filling = False
        self.preparing_to_pump_out = False
        self.pumping_out = False
        self.mainloop_running = True   
        self.T0 = None
        self.sent_T1_to_RP = False
        self.done_puff_prep = False
        self.both_puffs_done = None
        self.starting_up = True
        
        #self.RP_driver.set_GPI_safe_state(0)
        
        self.mainloop()
        
    def mainloop(self):
        self._add_to_log('Setting default state')
        self.handle_valve('V3', command='open', no_confirm=True)
        self.handle_valve('V4', command='close', no_confirm=True)
        self.handle_valve('V5', command='close', no_confirm=True)
        self.handle_valve('V7', command='close', no_confirm=True)
        # self.handle_valve('FV2', command='close', no_confirm=True)
        self._add_to_log('Finished setting default state')
        self.RP_driver.send_T1(0)
        
        last_control = time.time()
        self.last_plot = time.time() + UPDATE_INTERVAL # to get more fast data before first average
        
        while self.mainloop_running:
            now = time.time()
            
            # Pump and fill loop logic
            if now - last_control > CONTROL_INTERVAL:
                if self.preparing_to_pump_out:
                    if self.abs_avg_pressures[-1] < MECH_PUMP_LIMIT:
                        self._add_to_log('Completed prep for pump out')
                        self.handle_valve('V7', command='close')
                        self.preparing_to_pump_out = False
                        self.handle_pump_refill(skip_prep=True)
                if self.pumping_out:
                    done_pumping = all([p < PUMPED_OUT for p in self.abs_avg_pressures[-5:]])
                    if done_pumping:
                        self.handle_valve('V4', command='close')
                        self.pumping_out = False
                        self._add_to_log('Completed pump out. Beginning fill.')
                        self.handle_valve('V5', command='open')
                        self.filling = True
                if self.filling:
                    desired_pressure = float(self.desired_pressure_entry.get())
                    if self.abs_pressures[-1] > desired_pressure - FILL_MARGIN:
                        self.handle_valve('V5', command='close')
                        self.filling = False
                        self._add_to_log('Completed fill to %.2f Torr' % desired_pressure)
                last_control =  now
                
                # Get data on slower timescale now that it's queue-based
                self.get_data()
            
            # Stuff to do before and after puffs
            if self.T0:
                first_puff_start = 0 if self.start(1) == 0 or self.start(2) == 0 else \
                                   min(self.start(1) or math.inf, self.start(2) or math.inf)
                if now > self.T0 + PRETRIGGER - 1 + first_puff_start and not self.done_puff_prep:
                    self.handle_valve('V3', command='close')
                    self.done_puff_prep = True
                if now > self.T0 + PRETRIGGER and not self.sent_T1_to_RP:
                    self.RP_driver.send_T1(1)
                    self.RP_driver.send_T1(0)
                    self.sent_T1_to_RP = True
                if now > self.T0 + PRETRIGGER + self.both_puffs_done + 2:
                    self.handle_valve('V3', command='open')
                    self._change_puff_gui_state(tk.NORMAL)
                    self.plot_puffs()
                    self.T0 = None
                    self.sent_T1_to_RP = False
                
            self.root.update_idletasks()
            self.root.update()
                             
    def _quit_tkinter(self):
        self.mainloop_running = False # ends our custom while loop
        self.root.quit()      # stops mainloop 
        self.root.destroy()   # this is necessary on Windows to prevent
                              # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        
    def _add_to_log(self, text):
        time_string = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        self.log.insert(tk.END, ' ' + time_string + ' ' + text)
        self.log.yview(tk.END)

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
        
    def _change_puff_gui_state(self, state):
        elements = [self.permission_1_check, self.start_1_entry, 
                    self.duration_1_entry, self.permission_2_check,
                    self.start_2_entry, self.duration_2_entry]
        for e in elements:
            e.config(state=state)
        
    def start(self, puff_number):
        try:
            text = getattr(self, 'start_%d_entry' % puff_number).get()
            return float(text)
        except:
            return None
        
    def duration(self, puff_number):
        try:
            text = getattr(self, 'duration_%d_entry' % puff_number).get()
            return float(text)
        except:
            return None
        
    def abs_torr_single_reading(self):
        abs_counts = self.RP_driver.get_abs_gauge()
        bin_number = '{0:014b}'.format(abs_counts)
        return abs_bin_to_torr(bin_number)

    def diff_torr_single_reading(self):
        diff_counts = self.RP_driver.get_diff_gauge()
        bin_number = '{0:014b}'.format(diff_counts)
        return diff_bin_to_torr(bin_number)
        
    def get_data(self):
        # Add fast readings
        combined_pressure_history = self.RP_driver.get_GPI_data()
        now = time.time()
        abs_pressures = [abs_torr(i) for i in combined_pressure_history]
        diff_pressures = [diff_torr(i) for i in combined_pressure_history]
        self.abs_pressures.extend(abs_pressures)
        self.diff_pressures.extend(diff_pressures)
        self.pressure_times = np.arange(now-0.0001*(len(self.abs_pressures)-1), now, 0.0001)
        if len(combined_pressure_history) == 50000:
            # Show this message except during program startup, 
            # when there is always a backlog of data
            if not self.starting_up:
                self._add_to_log('Lost some data due to network lag')
            else:
                self.starting_up = False
        
        now = time.time()
        if now - self.last_plot > UPDATE_INTERVAL:
            # Add latest average reading
            interval_start = find_nearest(np.array(self.pressure_times)-now, -UPDATE_INTERVAL)
            self.pressure_avg_times.append(np.mean(self.pressure_times[interval_start:]))
            self.abs_avg_pressures.append(np.mean(self.abs_pressures[interval_start:]))
            self.diff_avg_pressures.append(np.mean(self.diff_pressures[interval_start:]))
            
            # Remove fast readings older than PLOT_TIME_RANGE seconds
            if not self.T0: # in case the puff delays are longer than PLOT_TIME_RANGE
                range_start = find_nearest(np.array(self.pressure_times)-now, -PLOT_TIME_RANGE)
                self.pressure_times = self.pressure_times[range_start:]
                self.abs_pressures = self.abs_pressures[range_start:]
                self.diff_pressures = self.diff_pressures[range_start:]
            
            # Remove average readings older than PLOT_TIME_RANGE seconds
            avgs_start = find_nearest(np.array(self.pressure_avg_times)-now, -PLOT_TIME_RANGE)
            self.pressure_avg_times = self.pressure_avg_times[avgs_start:]
            self.abs_avg_pressures = self.abs_avg_pressures[avgs_start:]
            self.diff_avg_pressures = self.diff_avg_pressures[avgs_start:]

            self.draw_plots()
            self.last_plot = now
            
    def draw_plots(self):
        # Do not attempt to draw plots if no data has been collected
        now = time.time()
        relative_times = [t - now for t in self.pressure_avg_times]
        if not relative_times:
            return
        self.ax_diff.cla()
        self.ax_abs.cla()
        
        # Absolute gauge plot setup
        self.ax_abs.yaxis.tick_right()
        self.ax_abs.yaxis.set_label_position('right')
        self.ax_abs.plot(relative_times, self.abs_avg_pressures, c='C0', linewidth=2)
        self.ax_abs.set_ylabel('Torr')
        plt.setp(self.ax_abs.get_xticklabels(), visible=False)
        self.ax_abs.grid(True, color='#c9dae5')
        self.ax_abs.patch.set_facecolor('#e3eff7')
        
        # Differential gauge plot setup
        self.ax_diff.yaxis.tick_right()
        self.ax_diff.yaxis.set_label_position('right')
        self.ax_diff.plot(relative_times, self.diff_avg_pressures, c='C1', linewidth=2)
        self.ax_diff.set_ylabel('Torr')
        self.ax_diff.set_xlabel('Seconds')
        self.ax_diff.grid(True, color='#e5d5c7')
        self.ax_diff.patch.set_facecolor('#f7ebe1')
        
        # Update labels
        self.abs_gauge_label['text'] = '%.1f\nTorr' % round(self.abs_avg_pressures[-1], 1)
        self.diff_gauge_label['text'] = '%.1f\nTorr' % round(self.diff_avg_pressures[-1], 1)
        
        self.fig.canvas.draw_idle()
        
    def handle_valve(self, valve_name, command=None, no_confirm=True):
        if valve_name == 'FV2':
            getter_method = 'get_fast_sts'
            setter_method = 'set_fast'
        else:
            valve_number = ['V5', 'V4', 'V3', 'V7'].index(valve_name) + 1
            getter_method = 'get_slow_%s_sts' % valve_number
            setter_method = 'set_slow_%s' % valve_number
            
        # If command arg is not supplied, set to toggle state of valve
        if not command:
            current_status = getattr(self.RP_driver, getter_method)()
            # V3 has opposite status logic 
            current_status = int(not current_status) if valve_name == 'V3' else current_status
            command = 'open' if current_status == 0 else 'close'
        if command == 'open':
            signal, action_text, fill = 1, 'OPENING', 'green'
        elif command == 'close':
            signal, action_text, fill = 0, 'CLOSING', 'red'
        self._add_to_log(action_text + ' ' + valve_name)
            
        # V3 expects opposite signals
        signal = int(not signal) if valve_name == 'V3' else signal
        
        def action():
            # Send signal
            getattr(self.RP_driver, setter_method)(signal)
            
            # Change indicator color    
            getattr(self, '%s_indicator' % valve_name).config(bg=fill)
                
        if no_confirm:
            action()
        else:
            self._confirm_window('Please confirm the %s of %s.' % (action_text, valve_name), action)
                        
    def handle_safe_state(self):
        checkbox_status = self.GPI_safe_status.get()
        self.RP_driver.set_GPI_safe_state(checkbox_status)
        
    def handle_permission(self, puff_number):
        '''
        May be possible to remove this method. Does Red Pitaya even check permission?
        '''
        permission = getattr(self, 'permission_%d' % puff_number).get()
        getattr(self.RP_driver, 'set_fast_permission_%d' % puff_number)(permission)
        
    def handle_fill(self):
        self._add_to_log('Beginning fill')
        self.filling = True
        self.handle_valve('V5', command='open')

    def handle_pump_refill(self, skip_prep=False):
        '''
        # Prepping for pump out
        If the "pump-out and refill" button is pushed and the absolute pressure is > 750 Torr, 
        then OPEN V7. CLOSE V7 when the pressure is below 750 Torr, and then OPEN V4. After V4 
        is opened the logic is the same as it is now, i.e. pump out until the pressure has been 
        < ~0 for xx seconds.
        
        This method only initiates the above processes. For the rest of the code related to this 
        logic, see the mainloop method.
        '''
        if self.abs_avg_pressures[-1] > MECH_PUMP_LIMIT and not skip_prep:
            self._add_to_log('Preparing for pump out')
            self.handle_valve('V7', command='open')
            self.preparing_to_pump_out = True
        elif self.abs_avg_pressures[-1] > PUMPED_OUT:
            self._add_to_log('Starting to pump out')
            self.handle_valve('V4', command='open')
            self.pumping_out = True
        else:
            self._add_to_log('No need to pump out')
        
    def handle_T0(self):
        valid_start_1 = self.start(1) is not None and self.start(1) >= 0
        valid_start_2 = self.start(2) is not None and self.start(2) >= 0
        valid_duration_1 = self.duration(1) and 0 < self.duration(1) < 2
        valid_duration_2 = self.duration(2) and 0 < self.duration(2) < 2
        puff_1_happening = self.permission_1.get() and valid_start_1 and valid_duration_1
        puff_2_happening = self.permission_2.get() and valid_start_2 and valid_duration_2
        if not (puff_1_happening or puff_2_happening):
            self._add_to_log('Error: invalid puff entries')
            return
            
        self.T0 = time.time()
        self._add_to_log('---T0---')
        self.root.after(int(PRETRIGGER*1000), self._add_to_log, '---T1---')
        
        self.done_puff_prep = False
        
        puff_1_done = self.start(1) + self.duration(1) if puff_1_happening else 0
        puff_2_done = self.start(2) + self.duration(2) if puff_2_happening else 0
        self.both_puffs_done = max(puff_1_done, puff_2_done)
        self.RP_driver.reset_time(int(self.both_puffs_done*1000)) # reset puff countup timer
        
        self._change_puff_gui_state(tk.DISABLED)

        if puff_1_happening:
            self.RP_driver.set_fast_delay_1(int(self.start(1)*1000))
            self.RP_driver.set_fast_duration_1(int(self.duration(1)*1000))
            self.root.after(int((PRETRIGGER+self.start(1))*1000), self._add_to_log, 'Puff 1')
        else:
            self.RP_driver.set_fast_delay_1(2+int(self.both_puffs_done*1000))
            self.RP_driver.set_fast_duration_1(2+int(self.both_puffs_done*1000))
            
        if puff_2_happening:
            self.RP_driver.set_fast_delay_2(int(self.start(2)*1000))
            self.RP_driver.set_fast_duration_2(int(self.duration(2)*1000))
            self.root.after(int((PRETRIGGER+self.start(2))*1000), self._add_to_log, 'Puff 2')
        else:
            self.RP_driver.set_fast_delay_2(2+int(self.both_puffs_done*1000))
            self.RP_driver.set_fast_duration_2(2+int(self.both_puffs_done*1000))
        
    
    def plot_puffs(self):
        try:
            times = np.array(self.pressure_times) - (self.T0 + PRETRIGGER)
            times, pressures = zip(*[(_t, _d) for (_t, _d) in zip(times, self.diff_pressures) if _t > -1])
            np.save(SAVE_FOLDER + 'diff_pressure_%d.npy' % int(self.T0), [times, pressures])
            plt.figure()
            plt.suptitle(int(self.T0))
            plt.subplot(211)
            pressures = medfilt(pressures, 11)
            plt.plot(times, pressures)
            plt.ylabel('Diff. pressure (Torr)')
            plt.subplot(212)
            f = interp1d(times, pressures, kind='linear')
            newtimes = np.arange(times[0], times[-1], 0.0005)
            dp_coarse = [0.798*derivative(f, ti, dx=.02) for ti in newtimes[100:-100]]
            dp_fine = [0.798*derivative(f, ti, dx=.005) for ti in newtimes[100:-100]]
            plt.plot(newtimes[100:-100], medfilt(dp_fine,11))
            plt.plot(newtimes[100:-100], medfilt(dp_coarse,11))
            plt.xlabel('t-T1 (s)')
            plt.ylabel('Flow rate (Torr-L/sec)')
            plt.savefig(SAVE_FOLDER + 'diff_pressure_%d.png' % int(self.T0))
            plt.ion() # to continue execution after closing window
            plt.show()
            plt.pause(0.001) # to continue execution after closing window
            self._add_to_log('Saved data with suffix %d' % int(self.T0))
        except Exception as e:
            self._add_to_log('Save pressure data failed: %s' % e)

 
if __name__ == '__main__':
    tk_root = tk.Tk()
    main_ui = GUI(tk_root)
