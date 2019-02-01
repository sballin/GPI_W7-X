'''
GUI for valve control in GPI system at W7-X. Original code by Kevin Tang.

TODO: fix 0 entry in start time - do not accept 0 puff duration though
TODO: require 5 entries less than 0 torr to stop pumping down
TODO: save values only starting 1 second before T1
'''

from __future__ import print_function # for print to work inside lambda
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
import datetime
import multiprocessing
import koheron 
from GPI_2.GPI_2 import GPI_2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


UPDATE_INTERVAL = 1  # seconds between plot updates
PLOT_TIME_RANGE = 30 # seconds of history shown in plots
DEFAULT_PUFF = 0.05  # seconds duration for each puff 
LOOP_SLEEP = 0.2 # seconds between pump/fill loop iterations
PRETRIGGER = 5 # seconds between T0 and T1
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
PUMPED_OUT = 0 # Torr, desired pumped out pressure
SAVE_FOLDER = '/usr/local/cmod/codes/spectroscopy/gpi/W7X/diff_pressures' # for puff pressure data


def uint32_to_volts(reading):
    '''
    Not really volts, but proportional. 
    Calibration is inside diff_torr and abs_torr functions.
    '''
    return 2/(2**14-1)*signed_conversion(reading)
    
        
def signed_conversion(reading):
    '''
    Convert Red Pitaya binary output to a uint32.
    '''
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
        

class Worker:
    '''
    Sends all Red Pitaya commands and collects all Red Pitaya data,
    never executing operations concurrently, which can return garbage.
    '''
    def __init__(self, commands_queue, data_queue):
        self.commands_queue = commands_queue
        self.data_queue = data_queue
        self.commands = []
        
        try:
            GPI_host = os.getenv('HOST', 'w7xrp2')
            GPI_client = koheron.connect(GPI_host, name='GPI_2')
            self.data_queue.put('Connected to Red Pitaya')
            self.GPI_driver = GPI_2(GPI_client)
        except Exception as e:
            print(e)
            self.GPI_driver = FakeRedPitaya()
            # self.data_queue.put('Red Pitaya unreachable - simulating...')
        
        self.pressure_times = []
        self.abs_pressures = []
        self.diff_pressures = []
        
        self.last_send = 0
        self.mainloop()
        
    def mainloop(self):
        while True:
            now = time.time()
            if not self.commands_queue.empty():
                self.commands.append(self.commands_queue.get_nowait())
                print('Commands (worker perspective):', self.commands)
            
            # Run any commands scheduled to execute (technically) before now 
            if self.commands:
                commands_to_remove = []
                for i, c in enumerate(self.commands):
                    if now > c[0]:
                        if len(c) == 3: 
                            # Run command with an argument
                            result = getattr(self.GPI_driver, c[1])(c[2])
                        else: 
                            # Run command with no argument
                            result = getattr(self.GPI_driver, c[1])()
                        if type(result) is int:
                            self.data_queue.put((c[1], result))
                        commands_to_remove.append(i)
                for i in commands_to_remove:
                    del self.commands[i]
            
            now = time.time()
            self.pressure_times.append(now)
            self.abs_pressures.append(self.abs_torr())
            self.diff_pressures.append(self.diff_torr())
            if now - self.last_send > UPDATE_INTERVAL:
                self.data_queue.put(('pressures', self.pressure_times, self.abs_pressures, self.diff_pressures))
                self.pressure_times = []
                self.abs_pressures = []
                self.diff_pressures = []
                self.last_send = now
            
    def abs_torr(self):
        abs_counts = self.GPI_driver.get_abs_gauge()
        abs_voltage = 0.0661+4.526*uint32_to_volts(abs_counts) # calibration for IN 1 of W7XRP2 with a 0.252 divider 
        return 5000/10*abs_voltage

    def diff_torr(self):
        diff_counts = self.GPI_driver.get_diff_gauge()
        diff_voltage = 0.047+3.329*uint32_to_volts(diff_counts) # calibration for IN 2 of W7XRP2 with a 0.342 divider
        return 100/10*diff_voltage
        
    def loop_pump_down(self):        
        if self.abs_pressures[-1] > PUMPED_OUT:
            self.handle_valve('V4', command='open')
        
        self._add_to_log('Starting to pump out')    
        while self.abs_pressures[-1] > PUMPED_OUT:
            time.sleep(LOOP_SLEEP)
        
        self.handle_valve('V4', command='close')
        self._add_to_log('Completed pump out')    
        
    def loop_fill(self):
        desired_pressure = float(self.desired_pressure_entry.get())
        
        if self.abs_pressures[-1] > desired_pressure:
            self._add_to_log('No need to fill - already at desired pressure')
            return 
            
        self._add_to_log('Starting fill to %.2f Torr' % desired_pressure)
        while self.abs_pressures[-1] < desired_pressure-FILL_MARGIN:
            self.handle_valve('V5', command='open')
            time.sleep(LOOP_SLEEP)
        self.handle_valve('V5', command='close')
        self._add_to_log('Completed fill to %.2f Torr' % desired_pressure)


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title('GPI Valve Control')
        win_width = int(1020)
        win_height = int(600)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        x = (self.screen_width / 2) - (win_width / 2)
        y = (self.screen_height / 2) - (win_height / 2)
        self.root.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
        self.root.protocol('WM_DELETE_WINDOW', self._quit_tkinter)
        s=ttk.Style()
        s.theme_use('alt')
        gray = '#C3C3C3'
        self.root.config(background=gray)
        
        system_frame = tk.Frame(self.root, background=gray)
        image = Image.open('background.png')
        image = image.resize((384, 600))
        photo = ImageTk.PhotoImage(image)
        background = tk.Label(system_frame, image=photo)
        background.image = photo
        background.configure(background='#C3C3C3')

        self.FV2_indicator = tk.Label(system_frame, width=3, height=1, text='FV2', fg='white', bg='red')

        self.V5_indicator = tk.Label(system_frame, width=2, height=1, text='V5', fg='white', bg='red')
        self.V5_indicator.bind("<Button-1>", lambda event: self.handle_valve('V5'))

        self.V4_indicator = tk.Label(system_frame, width=1, height=1, text='V4', fg='white', bg='red')
        self.V4_indicator.bind("<Button-1>", lambda event: self.handle_valve('V4'))

        self.V3_indicator = tk.Label(system_frame, width=2, height=1, text='V3', fg='white', bg='green')
        self.V3_indicator.bind("<Button-1>", lambda event: self.handle_valve('V3'))

        self.abs_gauge_label = tk.Label(system_frame, text='0\nTorr', bg='#1f77b4', fg='white', justify=tk.LEFT)
        self.diff_gauge_label = tk.Label(system_frame, text='0\nTorr', bg='#ff7f0e', fg='white', justify=tk.LEFT)

        controls_frame = tk.Frame(self.root, background=gray)
        fill_controls_frame = tk.Frame(controls_frame, background=gray)
        fill_controls_line1 = tk.Frame(fill_controls_frame, background=gray, pady=5)
        desired_pressure_label = tk.Label(fill_controls_line1, text='Desired pressure (Torr):', background=gray)
        self.desired_pressure_entry = ttk.Entry(fill_controls_line1, width=10, background=gray)

        fill_controls_line2 = tk.Frame(fill_controls_frame, background=gray)
        fill_button = ttk.Button(fill_controls_line2, text='Fill', command=lambda: start_thread(self.loop_fill))
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
        GPI_safe_state_check = tk.Checkbutton(permission_controls_frame, background=gray, command=self.handle_safe_state, variable=self.GPI_safe_status, state=tk.DISABLED)
        
        action_controls_frame = tk.Frame(controls_frame, background=gray)
        GPI_T0_button = ttk.Button(action_controls_frame, text='T0 trigger', width=10, command=self.handle_puff)
        
        self.pressure_times = []
        self.abs_pressures = []
        self.diff_pressures = []
        self.pressure_avg_times = []
        self.abs_avg_pressures = []
        self.diff_avg_pressures = []
        
        self.fig = Figure(figsize=(3,6), dpi=100, facecolor=gray)
        self.fig.subplots_adjust(left=0.2)
        # Absolute pressure plot matplotlib setup
        self.ax_abs = self.fig.add_subplot(211)
        # Differential pressure plot matplotlib setup
        self.ax_diff = self.fig.add_subplot(212)
        # Plot tkinter setup
        self.fig.set_tight_layout(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        
        # GUI element placement
        ## Column 1
        background.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.V3_indicator.place(relx=.472, rely=.548, relwidth=.043, relheight=.038)
        self.V4_indicator.place(relx=.218, rely=.422, relwidth=.044, relheight=.039)
        self.V5_indicator.place(relx=.339, rely=.346, relwidth=.06, relheight=.026)
        self.FV2_indicator.place(relx=.665, rely=.055, relwidth=.06, relheight=.026)
        self.abs_gauge_label.place(relx=.853, rely=.537)
        self.diff_gauge_label.place(relx=.629, rely=.751)
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
        
        self.data_queue = multiprocessing.Queue()
        self.commands_queue = multiprocessing.Queue()
        self.worker_process = multiprocessing.Process(target=Worker, 
                                                      args=(self.commands_queue, self.data_queue), 
                                                      daemon=True)
        self.worker_process.start()
        
        self.data = {}
        self.plots_need_update = False
        self.mainloop_running = True   
        
        self.mainloop()
        
    def mainloop(self):
        self._add_to_log('Setting default state')
        self.handle_valve('V3', command='open', no_confirm=True)
        self.handle_valve('V4', command='close', no_confirm=True)
        self.handle_valve('V5', command='close', no_confirm=True)
        self.handle_valve('FV2', command='close', no_confirm=True)
        self._add_to_log('Finished setting default state')
        
        while self.mainloop_running:
            self.get_data()
                
            if self.plots_need_update:
                self.draw_plots()
                
            self.root.update_idletasks()
            self.root.update()
                             
    def _quit_tkinter(self):
        self.mainloop_running = False # ends our custom while loop
        self.root.quit()      # stops mainloop 
        self.root.destroy()   # this is necessary on Windows to prevent
                              # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        
    def _add_to_log(self, text):
        time_string = datetime.datetime.now().strftime('%H:%M:%S')
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
        for element in elements:
            try: 
                element.config(state=state)
            except: 
                pass
        
    @property
    def rel_avg_times(self):
        now = time.time()
        return [t - now for t in self.pressure_avg_times]
        
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
            
    def ask_worker(self, command):
        # Issue command to be executed at time 0 (ASAP)
        self.commands_queue.put((0, command))
        # Wait for result of command to appear in data queue
        while command not in self.data.keys():
            self.get_data()
        return self.data[command]
        
    def get_data(self):
        while not self.data_queue.empty():
            datum = self.data_queue.get_nowait()
            now = time.time()
            if datum[0] == 'pressures':
                # Add fast readings
                self.pressure_times.extend(datum[1])
                self.abs_pressures.extend(datum[2])
                self.diff_pressures.extend(datum[3])
                
                # Add averaged readings
                self.pressure_avg_times.append(np.mean(datum[1]))
                self.abs_avg_pressures.append(np.mean(datum[2]))
                self.diff_avg_pressures.append(np.mean(datum[3]))
                
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

                self.plots_need_update = True
            elif type(datum) is str:
                # Data is a message to be added to the GUI log
                self._add_to_log(datum)
            else:
                # Data is the result of a command
                self.data[datum[0]] = datum[1]
        
    def handle_valve(self, valve_name, command=None, no_confirm=True):
        if valve_name == 'FV2':
            speed = 'fast'
            valve_number = 1
        else:
            speed = 'slow'
            valve_number = ['V5', 'V4', 'V3'].index(valve_name) + 1
            
        # If command arg is not supplied, set to toggle state of valve
        if not command:
            s = self.ask_worker('get_%s_%s_trigger' % (speed, valve_number))
            if valve_name == 'V3':
                if s == 0:
                    command = 'close'
                else:
                    command = 'open'
            else:
                if s == 0:
                    command = 'open'
                else:
                    command = 'close'
            
        signal =      1         if command == 'open' else 0
        action_text = 'OPENING' if command == 'open' else 'CLOSING'
        fill =        'green'   if command == 'open' else 'red'
        self._add_to_log(action_text + ' ' + valve_name)
        
            
        if valve_name == 'V3': # this valve's signals are reversed relative to normal
            signal = int(not signal)
        
        def action():
            # Send signal
            self.commands_queue.put((0, 'set_%s_%s_trigger' % (speed, valve_number), signal))
            
            # Getting rid of this means you have to click twice to change apparent state
            if speed == 'slow':
                self.ask_worker('get_%s_%s_trigger' % (speed, valve_number))
            
            # Change indicator color    
            getattr(self, '%s_indicator' % valve_name).config(bg=fill)
                
        if no_confirm:
            action()
        else:
            self._confirm_window('Please confirm the %s of %s.' % (action_text, valve_name), action)
                        
    def handle_safe_state(self):
        checkbox_status = self.GPI_safe_status.get()
        # self.GPI_driver.set_GPI_safe_state(checkbox_status)
        
    def handle_permission(self, puff_number):
        '''
        May be possible to remove this method. Does Red Pitaya even check permission?
        '''
        permission = getattr(self, 'permission_%d' % puff_number).get()
        # getattr(self.GPI_driver, 'set_fast_%d_permission' % puff_number)(int(permission))
        
    def handle_pump_refill(self):
        pass
        
    def handle_puff(self):
        self._add_to_log('---T0---')
        self._change_puff_gui_state(tk.DISABLED)
        valid_duration_1 = 0 < self.duration(1) < 2
        puff_1_happening = self.permission_1.get() and self.start(1) and valid_duration_1
        if puff_1_happening:
            self.commands_queue.put((0, 'set_fast_1_trigger', self.start(1)*1000))
            self.commands_queue.put((0, 'set_fast_1_duration', self.duration(1)*1000))
            self._add_to_log('Dispatched puff 1')
            
        valid_duration_2 = 0 < self.duration(2) < 2
        puff_2_happening = self.permission_2.get() and self.start(2) and valid_duration_2
        if puff_2_happening:
            self.commands_queue.put((0, 'set_fast_2_trigger', self.start(2)*1000))
            self.commands_queue.put((0, 'set_fast_2_duration', self.duration(2)*1000))
            self._add_to_log('Dispatched puff 2')
            
    def loop_puff(self):
        T0 = time.time()
        self.handle_valve('V3', command='close')
                
        # Save pressure data
        time.sleep(2)
        try:
            relative_times = self.rel_avg_times
            # matplotlib.use('Agg')
            pressures = [p for t,p in zip(relative_times, self.diff_pressures) if t > -1]
            relative_times = [t for t in relative_times if t > -1] 
            np.save(SAVE_FOLDER + 'diff_pressure_%d.npy' % int(T0), [relative_times, pressures])
            plt.plot(relative_times, pressures)
            plt.xlabel('t-T1 (s)')
            plt.ylabel('Diff. pressure (Torr)')
            plt.savefig(SAVE_FOLDER + 'diff_pressure_%d.png' % int(T0))
            self._add_to_log('Pressure data saved with ID %d' % T0)
        except Exception as e:
            self._add_to_log('Save pressure data failed')
            print('Save pressure data failed:', e)
            
        self.handle_valve('V3', command='open')
        self._change_puff_gui_state(tk.NORMAL)

    def draw_plots(self):
        # Do not attempt to draw plots if no data has been collected
        relative_times = self.rel_avg_times
        if not relative_times:
            return
        self.ax_diff.cla()
        self.ax_abs.cla()
        
        # Absolute gauge plot setup
        self.ax_abs.plot(relative_times, self.abs_avg_pressures, c='C0', linewidth=2)
        self.ax_abs.set_ylabel('Torr')
        plt.setp(self.ax_abs.get_xticklabels(), visible=False)
        self.ax_abs.grid(True, color='#c9dae5')
        self.ax_abs.patch.set_facecolor('#e3eff7')
        
        # Differential gauge plot setup
        self.ax_diff.plot(relative_times, self.diff_avg_pressures, c='C1', linewidth=2)
        self.ax_diff.set_ylabel('Torr')
        self.ax_diff.set_xlabel('Seconds')
        self.ax_diff.grid(True, color='#e5d5c7')
        self.ax_diff.patch.set_facecolor('#f7ebe1')
        
        # Update labels
        self.abs_gauge_label['text'] = '%.1f\nTorr' % round(self.abs_avg_pressures[-1], 1)
        self.diff_gauge_label['text'] = '%.1f\nTorr' % round(self.diff_avg_pressures[-1], 1)
        
        self.fig.canvas.draw_idle()
        
        self.plots_need_update = False
 
if __name__ == '__main__':
    tk_root = tk.Tk()
    main_ui = GUI(tk_root)
