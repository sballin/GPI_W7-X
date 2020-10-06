'''
Server for valve control and data acquisition in GPI system at W7-X.

TODO:
[ ] Data management
[ ] Pumping/filling routines
[ ] Puffing routines and permission
[ ] Manual control
[ ] Callbacks (.after commands in gui_reuse)
[ ] Logging
[ ] Safe state
'''

import os
import time
import math
import datetime
import logging
import xmlrpc.server
from threading import Timer
import koheron
import numpy as np
from GPI_RP.GPI_RP import GPI_RP


RP_HOSTNAME = 'rp3' # hostname of red pitaya being used
FAKE_RP = True
CONTROL_INTERVAL = 0.2 # seconds between pump/fill loop iterations
DEFAULT_PUFF = 0.05  # seconds duration for each puff 
PRETRIGGER = 10 # seconds between T0 and T1
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
MECH_PUMP_LIMIT = 770 # Torr, max pressure the mechanical pump should work on
PUMPED_OUT = 0 # Torr, desired pumped out pressure
PLENUM_VOLUME = 0.802 # L 


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


class RPServer:
    def __init__(self):
        # Create new xmlrpc server and register RPServer with it to expose RPServer functions
        address = ('127.0.0.1', 50000)
        self.RPCServer = xmlrpc.server.SimpleXMLRPCServer(address, allow_none=True)
        self.RPCServer.register_instance(self)
        # Timeout is how long handle_request() blocks the main thread even when there are no requests
        self.RPCServer.timeout = .001
        
        rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
        self.RPKoheron = GPI_RP(rpConnection)
        
        self._addToLog('Setting default state')
        self.handleValve('V3', command='open')
        self.handleValve('V4', command='close')
        self.handleValve('V5', command='close')
        self.handleValve('V7', command='close')
        self.RPKoheron.send_T1(0)
        self._addToLog('Finished setting default state')
        
        # Queues emptied every time the GUI asks for more data to display
        self.GUIDataQueue = []
        # Used for pump/fill logic and shot data
        self.pressureTimes = []
        self.absPressures = []
        self.diffPressures = []
        
        self.state = 'idle' # filling, venting before pump out, pumping out, shot/puffing, manual control
        self.T0 = None
        self.sentT1toRP = False
        self.firstPuffStart = None
        self.donePuffPrep = False
        self.bothPuffsDone = None
        self.targetPressure = None
        self.pumpoutRefill = False
        self.startingUp = True
        
        self._mainloop()
        
    def _mainloop(self):
        last_control = time.time()
        print('Serving...') 
        while True:
            now = time.time()
            
            # Pump and fill loop logic
            if now - last_control > CONTROL_INTERVAL:
                # if self.state == 'venting before pump out':
                #     if self.absPressures[-1] < MECH_PUMP_LIMIT: 
                #         self._addToLog('Completed venting before pump out')
                #         self.handleValve('V7', command='close')
                #         self.startPumpdown(skipPrep=True)
                # if self.state == 'pumping out':
                #     donePumping = all([p < PUMPED_OUT for p in self.absPressures[-5:]]) 
                #     if donePumping:
                #         self.handleValve('V4', command='close')
                #         self._addToLog('Completed pump out. Beginning fill.')
                #         self.startFill(self.targetPressure)
                # if self.state == 'filling':
                #     if self.absPressures[-1] > self.targetPressure - FILL_MARGIN:
                #         self.handleValve('V5', command='close')
                #         self.state = 'idle'
                #         self.targetPressure = None
                #         self._addToLog('Completed fill to %.2f Torr' % self.targetPressure)
                last_control =  now
                
                # Get data on slower timescale now that it's queue-based
                # self._getKoheronData()
                
                # Execute remote commands if any have been received
                self.RPCServer.handle_request()
            
            # Stuff to do before and after puffs
            if self.T0:
                if now > self.T0 + PRETRIGGER - 1 + self.firstPuffStart and not self.donePuffPrep:
                    self.handleValve('V3', command='close')
                    self.donePuffPrep = True
                if now > self.T0 + PRETRIGGER and not self.sentT1toRP:
                    self.RPKoheron.send_T1(1)
                    self.RPKoheron.send_T1(0)
                    self.sentT1toRP = True
                if now > self.T0 + PRETRIGGER + self.bothPuffsDone + 2:
                    self.handleValve('V3', command='open')
                    self.T0 = None
                    self.sentT1toRP = False
                    
            # if now - self.lastPrune > UPDATE_INTERVAL:
            #     # Remove fast readings older than PLOT_TIME_RANGE seconds
            #     if not self.T0: # in case the puff delays are longer than PLOT_TIME_RANGE
            #         range_start = find_nearest(np.array(self.pressureTimes)-now, -PLOT_TIME_RANGE)
            #         self.pressureTimes = self.pressureTimes[range_start:]
            #         self.absPressures = self.absPressures[range_start:]
            #         self.diffPressures = self.diffPressures[range_start:]
             
            # IMPORTANT: get callback results ((...).after(...))
            
    def init(self):
        pass
        
    def disarm(self):
        pass
    
    def arm(self):
        pass
        
    def store(self):
        pass
        
    def setManualControl(self, value):
        if value:
            self.state = 'manual control'
        else:
            self.state = 'idle'
        
    def startFill(self, targetPressure):
        self.targetPressure = targetPressure
        self._addToLog('Beginning fill')
        self.state = 'filling'
        self.handleValve('V5', command='open')
        
    def startPumpdown(self, targetPressure=PUMPED_OUT, skipPrep=False):
        self.targetPressure = targetPressure
        if self.absPressures[-1] > MECH_PUMP_LIMIT and not skipPrep:
            self._addToLog('Venting before pump out')
            self.handleValve('V7', command='open')
            self.state = 'venting before pump out'
        elif self.absPressures[-1] > PUMPED_OUT:
            self._addToLog('Starting to pump out')
            self.handleValve('V4', command='open')
            self.state = 'pumping out'
        else:
            self._addToLog('No need to pump out')
        
    def startPumpoutRefill(self, targetPressure, skipPrep=False):
        '''
        # Prepping for pump out
        If the "pump-out and refill" button is pushed and the absolute pressure is > 750 Torr, 
        then OPEN V7. CLOSE V7 when the pressure is below 750 Torr, and then OPEN V4. After V4 
        is opened the logic is the same as it is now, i.e. pump out until the pressure has been 
        < ~0 for xx seconds.
        
        This method only initiates the above processes. For the rest of the code related to this 
        logic, see the mainloop method.
        '''
        self.startPumpdown()
        
    def _addToLog(self, text):
        time_string = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(time_string + ' ' + text)
        
    def _getKoheronData(self):
        # Add fast readings
        combined_pressure_history = self.RPKoheron.get_GPI_data()
        now = time.time()
        absPressures = [abs_torr(i) for i in combined_pressure_history]
        diffPressures = [diff_torr(i) for i in combined_pressure_history]
        self.absPressures.extend(absPressures)
        self.diffPressures.extend(diffPressures)
        delta = 0.0001
        self.pressureTimes = np.arange(now-delta*(len(self.absPressures)-1), now+delta, delta)
        self.GUIDataQueue.extend(list(zip(self.pressureTimes.tolist(), absPressures, diffPressures)))
        if len(combined_pressure_history) == 50000:
            # Show this message except during program startup, 
            # when there is always a backlog of data
            if not self.startingUp:
                self._addToLog('Lost some data due to network lag')
            else:
                self.startingUp = False
                
    def getPressureData(self):
        data = self.GUIDataQueue.copy()
        self.GUIDataQueue = []
        return data
                
    def handleValve(self, valve_name, command=None):
        if valve_name == 'FV2':
            getter_method = 'get_fast_sts'
            setter_method = 'set_fast'
        else:
            valve_number = ['V5', 'V4', 'V3', 'V7'].index(valve_name) + 1
            getter_method = 'get_slow_%s_sts' % valve_number
            setter_method = 'set_slow_%s' % valve_number
            
        # If command arg is not supplied, set to toggle state of valve
        if not command:
            current_status = getattr(self.RPKoheron, getter_method)()
            # V3 has opposite status logic 
            current_status = int(not current_status) if valve_name == 'V3' else current_status
            command = 'open' if current_status == 0 else 'close'
        if command == 'open':
            signal = 1
            action_text = 'OPENING'
        elif command == 'close':
            signal = 0
            action_text = 'CLOSING'
        self._addToLog(action_text + ' ' + valve_name)
            
        # V3 expects opposite signals
        signal = int(not signal) if valve_name == 'V3' else signal
        
        # Send signal
        getattr(self.RPKoheron, setter_method)(signal)
            
    def setSafeState(self, value):
        self.RPKoheron.set_GPI_safe_state(int(value))
        
    def setPermission(self, puff_number, value):
        '''
        May be possible to remove this method. Does Red Pitaya even check permission?
        '''
        getattr(self.RPKoheron, 'set_fast_permission_%d' % puff_number)(int(value))
        
    def handleT0(self, p):
        self.T0 = time.time()
        self._addToLog('---T0---')
        Timer(PRETRIGGER, self._addToLog, args=['---T1---']).start()
        
        # Set variables used in main loop
        self.donePuffPrep = False
        if p['puff_1_start'] == 0 or p['puff_2_start'] == 0:
            self.firstPuffStart = 0
        else: 
            self.firstPuffStart = min(p['puff_1_start'] or math.inf, p['puff_2_start'] or math.inf)
        
        # Calculate when both puffs will be done, for main loop actions and FPGA reset
        if p['puff_1_happening']:
            puff_1_done = p['puff_1_start'] + p['puff_1_duration']
        else:
            puff_1_done = 0
        if p['puff_2_happening']:
            puff_2_done = p['puff_2_start'] + p['puff_2_duration']
        else:
            puff_2_done = 0
        self.bothPuffsDone = max(puff_1_done, puff_2_done)
        self.RPKoheron.reset_time(int(self.bothPuffsDone*1000)) # reset puff countup timer
        
        # Send fast puff timing info to FPGA 
        if p['puff_1_happening']:
            self.RPKoheron.set_fast_delay_1(int(p['puff_1_start']*1000))
            self.RPKoheron.set_fast_duration_1(int(p['puff_1_duration']*1000))
            Timer(PRETRIGGER+p['puff_1_start'], self._addToLog, args=['Puff 1 should happen now']).start()
        else:
            self.RPKoheron.set_fast_delay_1(2+int(self.bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_1(2+int(self.bothPuffsDone*1000))
        if p['puff_2_happening']:
            self.RPKoheron.set_fast_delay_2(int(p['puff_2_start']*1000))
            self.RPKoheron.set_fast_duration_2(int(p['puff_2_duration']*1000))
            Timer(PRETRIGGER+p['puff_2_start'], self._addToLog, args=['Puff 2 should happen now']).start()
        else:
            self.RPKoheron.set_fast_delay_2(2+int(self.bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_2(2+int(self.bothPuffsDone*1000))
        
        return 0


if __name__ == '__main__':
    rp = RPServer()
