'''
GUI for valve control in GPI system at W7-X. Original code by Kevin Tang.
'''

import sys
import os
import subprocess
import tkinter as tk
import tkinter.font
from tkinter import ttk
from PIL import Image, ImageTk
import time
import datetime
from xmlrpc.client import ServerProxy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


MIDDLE_SERVER_ADDR = 'http://127.0.0.1:50000'
SAVE_FOLDER = 'shot_data' # for puff pressure data
SOFTWARE_T1 = True  # send a T1 trigger through software (don't wait for hardware trigger)
PRETRIGGER = 5 # seconds between T0 and T1 (for T1 timing if SOFTWARE_T1 or for post-shot actions if not SOFTWARE_T1)
UPDATE_INTERVAL = .5  # seconds between plot updates
CONTROL_INTERVAL = 0.2 # seconds between pump/fill loop iterations
PLOT_TIME_RANGE = 30 # seconds of history shown in plots
DEFAULT_PUFF = 0.05  # seconds duration for each puff 
SHUTTER_CHANGE = 1 # seconds for the shutter to finish opening/closing
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
MECH_PUMP_LIMIT = 770 # Torr, max pressure the mechanical pump should work on
PUMPED_OUT = 0 # Torr, desired pumped out pressure
TORR_TO_BAR = 0.00133322
    
    
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


class GUI:
    def __init__(self, root):
        self.last_plot = None
        self.mainloop_running = True   
        self.starting_up = True
        self.middleServerConnected = False
        
        self.pressureTimes = []
        self.absPressures = []
        self.diffPressures = []
        
        # Used to cancel data display if a shot is interrupted
        self.afterShotGetData = None
        
        self.setupGUI(root)
        self._add_to_log('GUI initialized')
        
        self.connectToServer()
        
        self.mainloop()
        
    def setupGUI(self, root):
        self.root = root
        self.root.title('GPI Valve Control')
        win_width = int(1200)
        win_height = int(600)
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        x = (self.screen_width / 2) - (win_width / 2)
        y = (self.screen_height / 2) - (win_height / 2)
        self.root.geometry('%dx%d+%d+%d' % (win_width, win_height, x, y))
        self.root.protocol('WM_DELETE_WINDOW', self._quit_tkinter)
        s = ttk.Style()
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

        font = tkinter.font.Font(size=6)
        
        self.shutter_setting_indicator = tk.Label(system_frame, width=7, height=1, text='Shutter setting', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.shutter_sensor_indicator = tk.Label(system_frame, width=7, height=1, text='Shutter sensor', fg='white', bg='black', font=font)
    
        self.FV2_indicator = tk.Label(system_frame, width=3, height=1, text='FV2', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.V5_indicator = tk.Label(system_frame, width=2, height=1, text='V5', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.V4_indicator = tk.Label(system_frame, width=1, height=1, text='V4', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.V3_indicator = tk.Label(system_frame, width=2, height=1, text='V3', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.V7_indicator = tk.Label(system_frame, width=2, height=1, text='V7', fg='white', bg='black', font=font, relief=tk.RAISED, cursor='hand1')
        self.bindValveButtons()
        
        # Entire column to the right of the live graphs
        controls_frame = tk.Frame(self.root, background=gray)
        
        # State display and control
        ## Line 1
        state_frame = tk.Frame(controls_frame, background=gray)
        state_frame_line1 = tk.Frame(state_frame, background=gray, pady=5)
        self.state_text = tk.StringVar()
        self.state_text.set('State: middle server not connected')
        state_label = tk.Label(state_frame_line1, textvariable=self.state_text, background=gray)
        ## Line 2
        state_frame_line2 = tk.Frame(state_frame, background=gray, pady=5)
        cancel_button = ttk.Button(state_frame_line2, text='Cancel and reset', command=self.handleInterrupt)
        
        # Pump and fill controls
        fill_controls_frame = tk.Frame(controls_frame, background=gray)
        ## Line 1
        fill_controls_line1 = tk.Frame(fill_controls_frame, background=gray, pady=5)
        desired_pressure_label = tk.Label(fill_controls_line1, text='Desired pressure (Torr):', background=gray)
        self.desired_pressure_entry = ttk.Entry(fill_controls_line1, width=10, background=gray)
        ## Line 2
        fill_controls_line2 = tk.Frame(fill_controls_frame, background=gray)
        self.pumpOut = tk.IntVar()
        pump_out_label = tk.Label(fill_controls_line2, text='Pump out first', background=gray)
        pump_out_check = tk.Checkbutton(fill_controls_line2, variable=self.pumpOut, background=gray)
        self.exhaust = tk.IntVar()
        self.exhaust.set(1)
        exhaust_label = tk.Label(fill_controls_line2, text='Exhaust >770 Torr', background=gray)
        exhaust_check = tk.Checkbutton(fill_controls_line2, variable=self.exhaust, background=gray)
        ## Line 3
        fill_controls_line3 = tk.Frame(fill_controls_frame, background=gray)
        self.execute_button = ttk.Button(fill_controls_line3, text='Execute', command=self.handleChangePressure)

        # Puff controls
        ## Line 1
        self.permission_1 = tk.IntVar()
        puff_controls_frame = tk.Frame(controls_frame, background=gray)
        self.permission_1_check = tk.Checkbutton(puff_controls_frame, variable=self.permission_1, command=lambda: self.handle_permission(1), background=gray)
        self.start_1_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_1_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_1_entry.insert(0, str(DEFAULT_PUFF))
        ## Line 2
        self.permission_2 = tk.IntVar()
        self.permission_2_check = tk.Checkbutton(puff_controls_frame, variable=self.permission_2, command=lambda: self.handle_permission(2), background=gray)
        self.start_2_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_2_entry = ttk.Entry(puff_controls_frame, width=10)
        self.duration_2_entry.insert(0, str(DEFAULT_PUFF))
        
        permission_controls_line1 = tk.Frame(controls_frame, background=gray)
        self.w7x_permission_text = tk.StringVar()
        self.w7x_permission_text.set('W7-X permission signal: unknown')
        self.w7x_permission_label = tk.Label(permission_controls_line1, textvariable=self.w7x_permission_text, background=gray)
        permission_controls_line2 = tk.Frame(controls_frame, background=gray)
        self.t1_text = tk.StringVar()
        self.t1_text.set('T1 HW or SW signal: unknown')
        self.t1_label = tk.Label(permission_controls_line2, textvariable=self.t1_text, background=gray)
        
        action_controls_frame = tk.Frame(controls_frame, background=gray)
        self.T0_button = ttk.Button(action_controls_frame, text='T0 trigger', width=10, command=self.handleT0)

        self.fig = Figure(figsize=(3.5, 6), dpi=100, facecolor=gray)
        self.fig.subplots_adjust(left=0.3, right=0.7, top=0.925, hspace=0.5)
        # Absolute pressure plot matplotlib setup
        self.ax_abs = self.fig.add_subplot(211)
        self.ax_abs.set_ylabel('Torr')
        self.ax_abs.set_xlabel('Seconds')
        self.ax_abs.set_title('Absolute gauge')
        self.ax_abs.grid(True, color='#c9dae5')
        self.ax_abs.patch.set_facecolor('#e3eff7')
        self.line_abs, = self.ax_abs.plot([], [], c='C0', linewidth=1)
        self.ax_abs_conv = self.ax_abs.twinx()
        self.ax_abs_conv.set_ylabel('Bar')
        self.line_abs_conv, = self.ax_abs_conv.plot([], [], c='C0', alpha=0)
        self.abs_text = self.ax_abs.text(0.97, 0.97, '? Torr\n? Bar', horizontalalignment='right', verticalalignment='top', transform=self.ax_abs.transAxes, fontsize=10)
        # Differential pressure plot matplotlib setup
        self.ax_diff = self.fig.add_subplot(212)
        self.ax_diff.set_ylabel('Torr')
        self.ax_diff.set_xlabel('Seconds')
        self.ax_diff.set_title('Differential gauge')
        self.ax_diff.grid(True, color='#e5d5c7')
        self.ax_diff.patch.set_facecolor('#f7ebe1')
        self.line_diff, = self.ax_diff.plot([], [], c='C1', linewidth=1)
        self.ax_diff_conv = self.ax_diff.twinx()
        self.ax_diff_conv.set_ylabel('Bar')
        self.line_diff_conv, = self.ax_diff_conv.plot([], [], c='C1', alpha=0)
        self.diff_text = self.ax_diff.text(0.97, 0.97, '? Torr\n? Bar', horizontalalignment='right', verticalalignment='top', transform=self.ax_diff.transAxes, fontsize=10)
        # Plot tkinter setup
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        
        # Uncomment to see click x/y positions, useful for interface building
        # def click_location(event):
        #     print('%.4f, %.4f' % (event.x/469, event.y/600)) # divide by image dimensions
        # self.root.bind('<Button-1>', click_location)
        
        # GUI element placement
        ## Column 1
        background.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.V3_indicator.place(relx=.476, rely=.562, relwidth=.034, relheight=.038)
        self.V4_indicator.place(relx=.092, rely=.395, relwidth=.036, relheight=.038)
        self.V5_indicator.place(relx=.364, rely=.315, relwidth=.047, relheight=.026)
        self.V7_indicator.place(relx=.200, rely=.277, relwidth=.04, relheight=.028)
        self.FV2_indicator.place(relx=.635, rely=.067, relwidth=.05, relheight=.026)
        self.shutter_setting_indicator.place(relx=.817, rely=.062, relwidth=.2, relheight=.026)
        self.shutter_sensor_indicator.place(relx=.817, rely=.092, relwidth=.2, relheight=.026)
        system_frame.pack(side=tk.LEFT)
        ## Column 2
        self.canvas.get_tk_widget().pack(side=tk.LEFT)
        self.canvas.get_tk_widget().configure()
        ## Column 3
        ### Fill controls frame
        desired_pressure_label.pack(side=tk.LEFT)
        self.desired_pressure_entry.pack(side=tk.LEFT)
        self.execute_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        pump_out_label.pack(side=tk.LEFT, pady=5)
        pump_out_check.pack(side=tk.LEFT, pady=5, padx=5)
        exhaust_label.pack(side=tk.LEFT, pady=5)
        exhaust_check.pack(side=tk.LEFT, pady=5, padx=5)
        fill_controls_line1.pack(side=tk.TOP, fill=tk.X)
        fill_controls_line2.pack(side=tk.TOP, fill=tk.X)
        fill_controls_line3.pack(side=tk.TOP, fill=tk.X)
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
        ### Permission controls frame
        self.w7x_permission_label.pack(side=tk.LEFT)
        permission_controls_line1.pack(side=tk.TOP, fill=tk.X, pady=2)
        self.t1_label.pack(side=tk.LEFT)
        permission_controls_line2.pack(side=tk.TOP, fill=tk.X, pady=2)
        ### Action controls frame
        self.T0_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        action_controls_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### State frame
        state_label.pack(side=tk.LEFT)
        state_frame_line1.pack(side=tk.TOP, fill=tk.X)
        cancel_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        state_frame_line2.pack(side=tk.TOP, fill=tk.X)
        state_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).pack(side=tk.TOP, fill=tk.X)
        ### Log
        log_controls_frame = tk.Frame(controls_frame, background=gray)
        label_log_controls_frame = tk.Frame(log_controls_frame, background=gray)
        tk.Label(label_log_controls_frame, text='Event log', background=gray).pack(side=tk.LEFT, fill=tk.X)
        label_log_controls_frame.pack(side=tk.TOP, fill=tk.X)
        self.log = tk.Listbox(log_controls_frame, background=gray, highlightbackground=gray, font=font)
        self.log.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        log_controls_frame.pack(side=tk.TOP, fill=tk.BOTH, pady=10, expand=True)
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
    def connectToServer(self, hideFailureMessage=False):
        self.middle = ServerProxy(MIDDLE_SERVER_ADDR, verbose=False, allow_none=True)
        try:
            self.middle.serverIsAlive()
            self.middleServerConnected = True
            self._add_to_log('Connected to middle server ' + MIDDLE_SERVER_ADDR)
        except Exception as e:
            if not hideFailureMessage:
                print('Connect to middle server', MIDDLE_SERVER_ADDR, 'failed:', e)
                self._add_to_log('Not connected to middle server ' + MIDDLE_SERVER_ADDR)
        
    def mainloop(self):
        # self._add_to_log('Setting default state')
        # self._add_to_log('Finished setting default state')
        
        last_control = time.time()
        self.last_plot = time.time() + UPDATE_INTERVAL # +... to get more fast data before first average
        
        while self.mainloop_running:
            now = time.time()
            
            # Pump and fill loop logic
            if now - last_control > CONTROL_INTERVAL:
                last_control =  now
                
                # Get data on slower timescale now that it's queue-based
                # self.get_data()
                
                self.getDataUpdateUI()
             
            # Draw GUI and get callback results ((...).after(...))
            self.root.update()
            
            # Reduce CPU usage
            time.sleep(.005)
                             
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
            
    def handleDisconnected(self):
        self.middleServerConnected = False
        self.state_text.set('State: middle server not connected')
        self._add_to_log('Middle server disconnected')
        self.shutter_sensor_indicator.config(bg='black')
        self.shutter_setting_indicator.config(bg='black')
        self.V3_indicator.config(bg='black')
        self.V4_indicator.config(bg='black')
        self.V5_indicator.config(bg='black')
        self.V7_indicator.config(bg='black')
        self.FV2_indicator.config(bg='black')
        
    def getDataUpdateUI(self):
        try:
            data = self.middle.getDataForGUI()
            if not self.middleServerConnected:
                self._add_to_log('Reconnected to middle server')
                self.middleServerConnected = True
        except Exception as e:
            print('GUI.getDataUpdateUI', e)
            if self.middleServerConnected:
                self.handleDisconnected()
            return
        
        self.state_text.set('State: ' + data['state'])
        
        shutterSetting = data['shutter_setting']
        if shutterSetting == 1:
            self.shutter_setting_indicator.config(bg='green')
        elif shutterSetting == 0:
            self.shutter_setting_indicator.config(bg='red3')
        else:
            self.shutter_setting_indicator.config(bg='black')
            
        sensorStatus = data['shutter_sensor']
        if sensorStatus == 'open':
            self.shutter_sensor_indicator.config(bg='green')
        elif sensorStatus == 'closed':
            self.shutter_sensor_indicator.config(bg='red3')
        else:
            self.shutter_sensor_indicator.config(bg='black')
            
        for valve in ['V3', 'V4', 'V5', 'V7', 'FV2']:
            if data[valve] == 'open':
                fill = 'green'
            elif data[valve] == 'close':
                fill = 'red3'
            else:
                fill = 'black'
                print(data[valve])
            getattr(self, valve+'_indicator').config(bg=fill)
        
        for message in data['messages']:
            self._add_to_log(message)
            
        if data['w7x_permission'] == '4294967295':
            txt = 'high'
        elif data['w7x_permission'] == '0':
            txt = 'low'
        else:
            txt = data['w7x_permission']
        self.w7x_permission_text.set('W7-X permission signal: %s' % txt)
        
        if data['t1'] == '4294967295':
            txt = 'high'
        elif data['t1'] == '0':
            txt = 'low'
        else:
            txt = data['w7x_permission']
        self.t1_text.set('T1 HW or SW signal: %s' % txt)
            
        self.pressureTimes, self.absPressures, self.diffPressures = zip(*data['pressures_history'])
        if time.time() - self.last_plot > UPDATE_INTERVAL:
            self.draw_plots()
            self.last_plot = time.time()
            
    def start(self, puff_number):
        try:
            text = getattr(self, 'start_%d_entry' % puff_number).get().strip()
            return float(text)
        except Exception as e:
            return None
        
    def duration(self, puff_number):
        try:
            text = getattr(self, 'duration_%d_entry' % puff_number).get().strip()
            return float(text)
        except Exception as e:
            return None
    
    def draw_plots(self):
        # Do not attempt to draw plots if no data has been collected
        now = time.time()
        relative_times = [t - now for t in self.pressureTimes]
        if not relative_times:
            return
        
        # Update absolute gauge plot
        self.line_abs.set_data(relative_times, self.absPressures)
        self.ax_abs.relim()
        self.ax_abs.autoscale_view(True,True,True)
        self.line_abs_conv.set_data(relative_times, np.array(self.absPressures)*TORR_TO_BAR)
        self.ax_abs_conv.relim()
        self.ax_abs_conv.autoscale_view(True,True,True)
        self.abs_text.set_text('%.3g Torr\n%.3g Bar' % (self.absPressures[-1], self.absPressures[-1]*TORR_TO_BAR))
        
        # Update differential gauge plot
        self.line_diff.set_data(relative_times, self.diffPressures)
        self.ax_diff.relim()
        self.ax_diff.autoscale_view(True,True,True)
        self.line_diff_conv.set_data(relative_times, np.array(self.diffPressures)*TORR_TO_BAR)
        self.ax_diff_conv.relim()
        self.ax_diff_conv.autoscale_view(True,True,True)
        self.diff_text.set_text('%.3g Torr\n%.3g Bar' % (self.diffPressures[-1], self.diffPressures[-1]*TORR_TO_BAR))
        
        self.fig.canvas.draw_idle()

    def handle_safe_state(self):
        pass
        
    def handleInterrupt(self):
        self.middle.interrupt()
        self.enableButtons()
        self.root.after_cancel(self.afterShotGetData)
        
    def handle_permission(self, puffNumber):
        '''
        May be possible to remove this method. Does Red Pitaya even check permission?
        '''
        permissionGUIValue = getattr(self, 'permission_%d' % puffNumber).get()
        self.middle.handlePermission(puffNumber, permissionGUIValue)
        
    def handleChangePressure(self):
        desiredPressure = float(self.desired_pressure_entry.get().strip())
        self.middle.changePressure(desiredPressure, self.pumpOut.get(), self.exhaust.get())
        
    def handleT0(self):
        Tdone = self.middle.handleT0({'puff_1_permission': self.permission_1.get(),
                                      'puff_1_start': self.start(1),
                                      'puff_1_duration': self.duration(1),
                                      'puff_2_permission': self.permission_2.get(),
                                      'puff_2_start': self.start(2),
                                      'puff_2_duration': self.duration(2),
                                      'shutter_change_duration': SHUTTER_CHANGE,
                                      'software_t1': SOFTWARE_T1,
                                      'pretrigger': PRETRIGGER})
        # If a nonzero value is returned, settings were accepted and shot is happening for Tdone seconds
        if Tdone != 0:
            self.disableButtons()
            self.root.after(int((Tdone)*1000), self.enableButtons)
            self.afterShotGetData = self.root.after(int((Tdone+1)*1000), self.plotPuffs)
            
    def bindValveButtons(self):
        self.shutter_setting_indicator.bind("<Button-1>", lambda event: self.middle.handleToggleShutter())
        self.FV2_indicator.bind("<Button-1>", lambda event: self.middle.handleValve('FV2'))
        self.V5_indicator.bind("<Button-1>", lambda event: self.middle.handleValve('V5'))
        self.V4_indicator.bind("<Button-1>", lambda event: self.handleV4())
        self.V3_indicator.bind("<Button-1>", lambda event: self.middle.handleValve('V3'))
        self.V7_indicator.bind("<Button-1>", lambda event: self.middle.handleValve('V7'))        
        
    def handleV4(self):
        '''
        Prompt user for confirmation if opening V4 and pressure is high as the pump may be damaged.
        '''
        if self.absPressures[-1] > MECH_PUMP_LIMIT and self.middle.getValveStatus('V4') == 'close':
            result = tk.messagebox.askquestion("Overpressure Warning", "Are you sure? This may damage the pump.", icon='warning')
            if result == 'yes':
                self.middle.handleValve('V4', 'open')
        else:
            self.middle.handleValve('V4')
            
            
    def enableButtons(self):
        for button in [self.T0_button, self.execute_button]:
            button['state'] = 'normal'
        self.bindValveButtons()
        for button in [self.shutter_setting_indicator, self.FV2_indicator, self.V5_indicator, 
                       self.V4_indicator, self.V3_indicator, self.V7_indicator]:
            button.configure(relief=tk.RAISED, cursor='hand1')
        
    def disableButtons(self):
        for button in [self.T0_button, self.execute_button]:
            button['state'] = 'disabled'
        for button in [self.shutter_setting_indicator, self.FV2_indicator, self.V5_indicator, 
                       self.V4_indicator, self.V3_indicator, self.V7_indicator]:
            button.unbind('<Button-1>')
            button.configure(relief=tk.FLAT, cursor='arrow')
        
    def plotPuffs(self):
        # Get shot data from middle server
        try:
            T1, t, dp = self.middle.getLastShotData()
        except Exception as e:
            self._add_to_log('Get last shot data failed: %s' % e)
            return
            
        # Save shot data to file
        try:
            t = np.array(t)-T1
            if not os.path.isdir(SAVE_FOLDER):
                os.mkdir(SAVE_FOLDER)
            savepath = SAVE_FOLDER + '/diff_pressure_%d.npy' % int(T1)
            np.save(savepath, [t, dp])
            self._add_to_log('Saved shot data to %s' % savepath)
        except Exception as e:
            self._add_to_log('Save pressure data failed: %s' % e)
            return
            
        # Launch script to plot data using the same python executable that's running this script
        subprocess.Popen([sys.executable, 'plot_shot.py', savepath])

 
if __name__ == '__main__':
    tk_root = tk.Tk()
    main_ui = GUI(tk_root)
