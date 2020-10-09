'''
Server for valve control and data acquisition in GPI system at W7-X.

TODO:
[ ] Data management (incl. analog input)
[ ] Pumping/filling routines
[ ] Puffing routines and permission
[ ] Manual control
[x] Callbacks (.after commands in gui_reuse)
[ ] Logging
[ ] Safe state
[ ] Log/print all exceptions
[ ] 100 ms timeout for network commands esp shutter
'''

import time
import datetime
import xmlrpc.server
import koheron
import numpy as np
from bottleneck import move_mean
from GPI_RP.GPI_RP import GPI_RP


RP_HOSTNAME = 'rp3' # hostname of red pitaya being used
CONTROL_INTERVAL = 0.1 # seconds between pump/fill loop iterations
DEFAULT_PUFF = 0.05  # seconds duration for each puff 
PRETRIGGER = 10 # seconds between T0 and T1
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
MECH_PUMP_LIMIT = 770 # Torr, max pressure the mechanical pump should work on
PUMPED_OUT = 0 # Torr, desired pumped out pressure
PLENUM_VOLUME = 0.802 # L 
READING_HISTORY = 30 # seconds of pressure readings to keep in memory


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
        self.state = 'idle' # filling, venting before pump out, pumping out, shot, manual control
        self.T0 = None
        self.sentT1toRP = False
        self.firstPuffStart = None
        self.donePuffPrep = False
        self.bothPuffsDone = None
        self.targetPressure = None
        self.pumpoutRefill = False
        self.gotFirstQueue = False
        
        # Queues emptied every time the GUI asks for more data to display
        self.GUIData = []
        # Queue of (time to execute, function, args) objects like threading.Timer does. We want to 
        # avoid threading for Koheron interactions because of potential bugs
        self.taskQueue = []
        # Queue of strings to send to GUI for logging
        self.messageQueue = []
        # Used for pump/fill logic and shot data
        self.pressureTimes = []
        self.absPressures = []
        self.diffPressures = []
        
        # Create new xmlrpc server and register RPServer with it to expose RPServer functions
        address = ('127.0.0.1', 50000)
        self.RPCServer = xmlrpc.server.SimpleXMLRPCServer(address, allow_none=True)
        self.RPCServer.register_instance(self)
        # This timeout is how long handle_request() blocks the main thread even when there are no requests
        self.RPCServer.timeout = .001
        
        rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
        self.RPKoheron = GPI_RP(rpConnection)
        
        self._addToLog('Server setting default state')
        self.setDefault()
        
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
                self._getKoheronData()
                
                # Execute remote commands if any have been received
                self.RPCServer.handle_request()
            
            # Stuff to do before and after puffs
            if self.T0:
                self.state = 'shot'
                now = time.time()
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
                    self.state = 'idle'
                    self.sentT1toRP = False
                    
            # Do any required tasks in task queue
            # remainingTasks = []
            now = time.time()
            for execTime, function, args in self.taskQueue:
                if execTime < now:
                    function(*args)
                    self.taskQueue.remove((execTime, function, args))
                # else:
                    # remainingTasks.append((execTime, function, args))
            # self.taskQueue = remainingTasks
                    
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
        
    def setDefault(self):
        self.handleValve('V3', command='open')
        self.handleValve('V4', command='close')
        self.handleValve('V5', command='close')
        self.handleValve('V7', command='close')
        self.handleValve('FV2', command='close')
        self.setShutter('close')
        self.RPKoheron.send_T1(0)
        self._addToLog('Finished setting default state')
        
    def disarm(self):
        pass
    
    def arm(self):
        pass
        
    def store(self):
        pass
        
    def serverIsAlive(self):
        return True
        
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
        
    def addTask(self, execTime, function, args):
        '''
        execTime: seconds in future at which to execute this function
        '''
        self.taskQueue.append((time.time()+execTime, function, args))
        
    def _addToLog(self, text):
        time_string = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        message = time_string + ' ' + text
        self.messageQueue.append(message)
        print(message)
        
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
        
        # Remove fast readings older than READING_HISTORY seconds, except during a shot cycle
        if self.state != 'shot': 
            range_start = find_nearest(np.array(self.pressureTimes)-now, -READING_HISTORY)
            self.pressureTimes = self.pressureTimes[range_start:]
            self.absPressures = self.absPressures[range_start:]
            self.diffPressures = self.diffPressures[range_start:]
            
        # Calculate moving mean of 1000 samples (0.1 s) to send to GUI
        self.GUIData = list(zip(move_mean(self.pressureTimes, 1000)[::1000].tolist(), 
                                move_mean(self.absPressures, 1000)[::1000].tolist(),
                                move_mean(self.diffPressures, 1000)[::1000].tolist()))
        
        if len(combined_pressure_history) == 50000:
            # Show this message except during program startup, when the FPGA queue is normally full
            if self.gotFirstQueue:
                self._addToLog('Lost some data due to network lag')
            else:
                self.gotFirstQueue = True

                
    def getPressureData(self):
        data = self.GUIDataQueue.copy()
        self.GUIDataQueue = []
        return data
        
    def setShutter(self, state):
        if state == 'open':
            value = 1
        elif state == 'close':
            value = 0
        else:
            self._addToLog('Bad shutter command')
            return
        self._addToLog('Telling shutter to ' + state)
        self.RPKoheron.set_analog_out(value)
        
    def handleToggleShutter(self):
        currentSetting = self.RPKoheron.get_analog_out()
        if currentSetting == 0:
            self.setShutter('open')
        elif currentSetting == 1:
            self.setShutter('close')
        else:
            self._addToLog('Shutter register has bad value')
            
    def getData(self):
        # Copy and flush message queue
        messageQueue = self.messageQueue
        self.messageQueue = []
        
        return {'shutter_setting': self.getShutterSetting(),
                'shutter_sensor': self.getShutterSensor(),
                'V3': self.getValveStatus('V3'),
                'V4': self.getValveStatus('V4'),
                'V5': self.getValveStatus('V5'),
                'V7': self.getValveStatus('V7'),
                'FV2': self.getValveStatus('FV2'),
                'pressures_history': self.GUIData,
                'messages': messageQueue}
            
    def getShutterSetting(self):
        return self.RPKoheron.get_analog_out()
            
    def getShutterSensor(self):
        ai0 = self.RPKoheron.get_analog_input_0()
        ai1 = self.RPKoheron.get_analog_input_1()
        if ai0 < 9000 < ai1:
            return 'closed'
        elif ai0 > 9000 > ai1:
            return 'open'
        else:
            return 'bad'
        
    def handlePermission(self, puffNumber, permissionValue):
        '''
        This method may be unnecessary. Does FPGA even check permission?
        '''
        getattr(self.RPKoheron, 'set_fast_permission_%d' % puffNumber)(permissionValue)
        
    def getValveStatus(self, valveName):
        if valveName == 'FV2':
            statusInt = self.RPKoheron.get_fast_sts()
        else:
            valve_number = ['V5', 'V4', 'V3', 'V7'].index(valveName) + 1
            statusInt = getattr(self.RPKoheron, 'get_slow_%s_sts' % valve_number)()
        # V3 has opposite status logic 
        if valveName == 'V3':
            statusInt = int(not statusInt)
        if statusInt == 1:
            status = 'open'
        else:
            status = 'close'
        return status
                
    def handleValve(self, valve_name, command=None):
        if valve_name == 'FV2':
            setter_method = 'set_fast'
        else:
            valve_number = ['V5', 'V4', 'V3', 'V7'].index(valve_name) + 1
            setter_method = 'set_slow_%s' % valve_number
            
        # If command arg is not supplied, set to toggle state of valve
        if not command:
            current_status = self.getValveStatus(valve_name)
            if current_status == 'close':
                command = 'open'
            else:
                command = 'close'
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
        self.addTask(PRETRIGGER, self._addToLog, args=['---T1---'])
        
        # Set variables used in main loop
        self.donePuffPrep = False
        self.firstPuffStart = p['puff_1_start']
        
        # Calculate when both puffs will be done, for main loop actions and FPGA reset
        if p['puff_1_happening']:
            puff_1_done = p['puff_1_start'] + p['puff_1_duration']
            self.addTask(PRETRIGGER+p['puff_1_start']-p['shutter_change_duration'], self.setShutter, ['open'])
        else:
            puff_1_done = 0
        if p['puff_2_happening']:
            puff_2_done = p['puff_2_start'] + p['puff_2_duration']
        else:
            puff_2_done = 0
        self.bothPuffsDone = max(puff_1_done, puff_2_done)
        self.RPKoheron.reset_time(int(self.bothPuffsDone*1000)) # reset puff countup timer
        # Close shutter after both puffs are done
        self.addTask(PRETRIGGER+self.bothPuffsDone+1, self.setShutter, ['close'])
        # Close shutter in between puffs if they're far apart
        if p['puff_1_happening'] and p['puff_2_happening']:
            if p['puff_2_start'] - puff_1_done > 2*p['shutter_change_duration'] + 3:
                self.addTask(PRETRIGGER+puff_1_done+1, self.setShutter, ['close'])
                self.addTask(PRETRIGGER+p['puff_2_start']-p['shutter_change_duration'], self.setShutter, ['open'])
        
        # Send fast puff timing info to FPGA 
        if p['puff_1_happening']:
            self.RPKoheron.set_fast_delay_1(int(p['puff_1_start']*1000))
            self.RPKoheron.set_fast_duration_1(int(p['puff_1_duration']*1000))
            self.addTask(PRETRIGGER+p['puff_1_start'], self._addToLog, ['Puff 1 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_1(2+int(self.bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_1(2+int(self.bothPuffsDone*1000))
        if p['puff_2_happening']:
            self.RPKoheron.set_fast_delay_2(int(p['puff_2_start']*1000))
            self.RPKoheron.set_fast_duration_2(int(p['puff_2_duration']*1000))
            self.addTask(PRETRIGGER+p['puff_2_start'], self._addToLog, ['Puff 2 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_2(2+int(self.bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_2(2+int(self.bothPuffsDone*1000))
        
        return 0


if __name__ == '__main__':
    rp = RPServer()
