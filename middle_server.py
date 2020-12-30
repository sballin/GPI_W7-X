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
MAX_PUFF_DURATION = 2 # seconds max for FV2 to remain open for an individual puff


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
        # Keep track of server health
        self.mainloopTimes = []
        
        # Create new xmlrpc server and register RPServer with it to expose RPServer functions
        address = ('127.0.0.1', 50000)
        self.RPCServer = xmlrpc.server.SimpleXMLRPCServer(address, allow_none=True, logRequests=False)
        self.RPCServer.register_instance(self)
        # This timeout is how long handle_request() blocks the main thread even when there are no requests
        self.RPCServer.timeout = .001
        
        rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
        self.RPKoheron = GPI_RP(rpConnection)
        
        self._addToLog('Server setting default state')
        self.setDefault()
        
        self.addTask(10, self.announceServerHealth, [])
        
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
                    
            # Do any required tasks in task queue
            remainingTasks = []
            for execTime, function, args in self.taskQueue:
                if execTime < time.time():
                    function(*args)
                else:
                    remainingTasks.append((execTime, function, args))
            self.taskQueue = remainingTasks
            
            # if self.state == 'idle':
            #     time.sleep(0.05)
            
            self.mainloopTimes.append(time.time()-now)
    
    def announceServerHealth(self):
        ml = np.array(self.mainloopTimes)*1000
        self._addToLog('MS main loop: mean %.3g ms, std %.3g ms, min %.3g ms, max %.3g ms' % (ml.mean(), ml.std(), ml.min(), ml.max()))
        self.mainloopTimes = []
        self.addTask(10, self.announceServerHealth, [])
            
    def setState(self, state):
        self.state = state
        self._addToLog('Setting middle server state = ' + state)
            
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
        now = time.time()
        try:
            # This may raise an exception due to network timeout
            combined_pressure_history = self.RPKoheron.get_GPI_data()
            
            # Add fast readings
            self.absPressures.extend([abs_torr(i) for i in combined_pressure_history])
            self.diffPressures.extend([diff_torr(i) for i in combined_pressure_history])
            delta = 0.0001
            self.pressureTimes = np.arange(now-delta*(len(self.absPressures)-1), now+delta, delta)
            
            if len(combined_pressure_history) == 50000:
                # Show this message except during program startup, when the FPGA queue is normally full
                if self.gotFirstQueue:
                    self._addToLog('Lost some data due to network lag')
                else:
                    self.gotFirstQueue = True
        except Exception as e:
            self._addToLog(str(e))
            self._addToLog('Attempting to reconnect to RP')
            rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
            self.RPKoheron = GPI_RP(rpConnection)
        
        # Remove fast readings older than READING_HISTORY seconds, except during a shot cycle
        if self.state != 'shot': 
            range_start = find_nearest(np.array(self.pressureTimes)-now, -READING_HISTORY)
            self.pressureTimes = self.pressureTimes[range_start:]
            self.absPressures = self.absPressures[range_start:]
            self.diffPressures = self.diffPressures[range_start:]
            
        # Calculate moving mean of 1000 samples (0.1 s) to send to GUI
        if len(self.pressureTimes) > 1000:
            self.GUIData = list(zip(move_mean(self.pressureTimes, 1000)[::1000].tolist(), 
                                    move_mean(self.absPressures, 1000)[::1000].tolist(),
                                    move_mean(self.diffPressures, 1000)[::1000].tolist()))
        else:
            self.GUIData = [[],[],[]]
        
    def setShutter(self, state):
        if state == 'open':
            self._addToLog('OPENING shutter')
            value = 1
        elif state == 'close':
            self._addToLog('CLOSING shutter')
            value = 0
        else:
            self._addToLog('Bad shutter command')
            return
        self.RPKoheron.set_analog_out(value)
        
    def handleToggleShutter(self):
        currentSetting = self.RPKoheron.get_analog_out()
        if currentSetting == 0:
            self.setShutter('open')
        elif currentSetting == 1:
            self.setShutter('close')
        else:
            self._addToLog('Shutter register has bad value')
            
    def getDataForGUI(self):
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
                'messages': messageQueue,
                'state': self.state}
            
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
        
    def sendT1toRP(self):
        self.RPKoheron.send_T1(1)
        self.RPKoheron.send_T1(0)
        
    def postShotActions(self):
        self.handleValve('V3', command='open')
        self.setState('idle')
        
    def handleT0(self, p):
        valid_start_1 = p['puff_1_start'] and p['puff_1_start'] >= 0
        valid_start_2 = p['puff_2_start'] and p['puff_2_start'] >= 0
        valid_duration_1 = p['puff_1_duration'] and 0 < p['puff_1_duration'] < MAX_PUFF_DURATION
        valid_duration_2 = p['puff_2_duration'] and 0 < p['puff_2_duration'] < MAX_PUFF_DURATION
        puff_1_happening = p['puff_1_permission'] and valid_start_1 and valid_duration_1
        puff_2_happening = p['puff_2_permission'] and valid_start_2 and valid_duration_2
        # Puff 1 should always be used
        if not puff_1_happening:
            self._addToLog('Error: puff 1 must be used')
            return
        # Puff 1 should never bleed into puff 2
        if puff_1_happening and puff_2_happening:
            if not p['puff_1_start'] + p['puff_1_duration'] < p['puff_2_start']:
                self._addToLog('Error: puff 1 would bleed into puff 2')
                return
        
        self.setState('shot')
        self._addToLog('---T0---')
        self.addTask(PRETRIGGER, self._addToLog, args=['---T1---'])
        self.addTask(PRETRIGGER - 1 + p['puff_1_start'], self.handleValve, ['V3', 'close'])
        self.addTask(PRETRIGGER, self.sendT1toRP, [])
        
        # Calculate when both puffs will be done to queue post-shot actions
        if puff_1_happening: # never False
            puff_1_done = p['puff_1_start'] + p['puff_1_duration']
            self.addTask(PRETRIGGER+p['puff_1_start']-p['shutter_change_duration'], self.setShutter, ['open'])
        else:
            puff_1_done = 0
        if puff_2_happening:
            puff_2_done = p['puff_2_start'] + p['puff_2_duration']
        else:
            puff_2_done = 0
        bothPuffsDone = max(puff_1_done, puff_2_done)
        # Close shutter after both puffs are done
        self.addTask(PRETRIGGER+bothPuffsDone+1, self.setShutter, ['close'])
        # Close shutter in between puffs if they're far apart
        if puff_1_happening and puff_2_happening:
            if p['puff_2_start'] - puff_1_done > 2*p['shutter_change_duration'] + 3:
                self.addTask(PRETRIGGER+puff_1_done+1, self.setShutter, ['close'])
                self.addTask(PRETRIGGER+p['puff_2_start']-p['shutter_change_duration'], self.setShutter, ['open'])
        # Open V3 and set state 'idle' after both puffs are done
        self.addTask(PRETRIGGER + bothPuffsDone + 2, self.postShotActions, [])
        self.RPKoheron.reset_time(int(bothPuffsDone*1000)) # reset puff countup timer
        
        # Send fast puff timing info to FPGA 
        if puff_1_happening: # never False
            self.RPKoheron.set_fast_delay_1(int(p['puff_1_start']*1000))
            self.RPKoheron.set_fast_duration_1(int(p['puff_1_duration']*1000))
            self.addTask(PRETRIGGER+p['puff_1_start'], self._addToLog, ['Puff 1 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_1(2+int(bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_1(2+int(bothPuffsDone*1000))
        if puff_2_happening:
            self.RPKoheron.set_fast_delay_2(int(p['puff_2_start']*1000))
            self.RPKoheron.set_fast_duration_2(int(p['puff_2_duration']*1000))
            self.addTask(PRETRIGGER+p['puff_2_start'], self._addToLog, ['Puff 2 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_2(2+int(bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_2(2+int(bothPuffsDone*1000))


if __name__ == '__main__':
    rp = RPServer()
