'''
Server for valve control and data acquisition in GPI system at W7-X.

Methods starting with _ should only be called in middle_server.py.
Other methods can be called from gui.py.

TODO:
[ ] Data management (incl. analog input)
[x] Pumping/filling routines
[ ] Puffing routines and permission
[ ] Manual control
[x] Callbacks (.after commands in gui_reuse)
[x] Logging
[ ] Safe state
[ ] Log/print all exceptions
[ ] 100 ms timeout for network commands esp shutter
'''

import time
import datetime
import xmlrpc.server
import logging
import koheron
import numpy as np
from bottleneck import move_mean
from GPI_RP.GPI_RP import GPI_RP


# User settings
RP_HOSTNAME = 'rp3' # hostname of red pitaya being used
LOG_FILE = 'log.txt'
PUMPED_OUT = 0 # Torr, pressure at which to stop pumping out
FILL_MARGIN = 5 # Torr, stop this amount short of desired fill pressure to avoid overshoot
SIMULATE_RP = True # create fake data to test pump/puff methods, gui...

# Constants
CONTROL_INTERVAL = 0.1 # seconds between pump/fill loop iterations
PRETRIGGER = 10 # seconds between T0 and T1
MECH_PUMP_LIMIT = 770 # Torr, max pressure the mechanical pump should work on
MAX_FILL = 3*760 # Torr, max pressure that user can request
PLENUM_VOLUME = 0.802 # L
READING_HISTORY = 30 # seconds of pressure readings to keep in memory
MAX_PUFF_DURATION = 2 # seconds max for FV2 to remain open for an individual puff
PRESSURE_HZ = 10000 # sampling rate for absolute and differential pressure gauges


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
        self.state = 'idle' # filling, exhaust, pumping out, shot, manual control
        self.targetPressure = None
        self.pumpoutRefill = False
        self.gotFirstQueue = False
        logging.basicConfig(filename=LOG_FILE, format='%(message)s', level=logging.DEBUG)
        
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
        
        self.addToLog('Server setting default state')
        self.setDefault()
        
        self.addTask(10, self.announceServerHealth, [])
        
        self.mainloop()
        
    def mainloop(self):
        last_control = time.time()
        print('Serving...') 
        while True:
            now = time.time()
            
            if now - last_control > CONTROL_INTERVAL:
                last_control =  now
                
                # Get data on slower timescale now that it's queue-based
                if SIMULATE_RP:
                    self.getFakePressureData()
                else:
                    self.getPressureData()
                
                # Execute remote commands if any have been received
                self.RPCServer.handle_request()
                    
            # Do any required tasks in task queue
            self.handleTasks()
            
            # if self.state == 'idle':
            #     time.sleep(0.05)
            
            self.mainloopTimes.append(time.time()-now)
            
    def handleTasks(self):
        '''
        Carry out any tasks that are up for execution in the task queue. Any tasks added to the task queue while this method is running will be executed at the very earliest on the next call to handleTasks.
        '''
        for execTime, function, args in self.taskQueue.copy():
            if execTime < time.time():
                function(*args)
                self.taskQueue.remove((execTime, function, args))
            
    def addTask(self, execTime, function, args):
        '''
        execTime: seconds in future at which to execute this function
        '''
        self.taskQueue.append((time.time()+execTime, function, args))
        
    def addToLog(self, text):
        time_string = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        message = time_string + ' ' + text
        self.messageQueue.append(message)
        logging.info(message)
        print(message)
    
    def announceServerHealth(self):
        ml = np.array(self.mainloopTimes)*1000
        self.addToLog('MS main loop: mean %.3g ms, std %.3g ms, min %.3g ms, max %.3g ms' % (ml.mean(), ml.std(), ml.min(), ml.max()))
        self.mainloopTimes = []
        self.addTask(10, self.announceServerHealth, [])
            
    def setState(self, state):
        self.addToLog('Setting middle server state = ' + state)
        self.state = state
            
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
        self.addToLog('Finished setting default state')
        
    def disarm(self):
        pass
    
    def arm(self):
        pass
        
    def store(self):
        pass
        
    def serverIsAlive(self):
        return True
        
    def currentPressure(self):
        return np.mean(self.absPressures[-1000:])
        
    def lowerPressure(self, desiredPressure, fillPressure):
        '''
        Lower the pressure and optionally start filling to another pressure.
        
        Args:
            desiredPressure: (Torr) exhaust and/or pump down to this pressure
            fillPressure: (Torr) if not None, fill to this pressure after pumping out
        '''
        if self.state == 'exhaust':
            if desiredPressure < self.currentPressure() > MECH_PUMP_LIMIT:
                if self.getValveStatus('V7') == 'close':
                    self.addToLog('Beginning exhaust')
                    self.handleValve('V7', command='open')
                self.addTask(0, self.lowerPressure, [desiredPressure, fillPressure])
            elif desiredPressure < self.currentPressure() < MECH_PUMP_LIMIT:
                self.addToLog('Exhaust complete (%.3g Torr), beginning pump out' % self.currentPressure())
                self.setState('pumping out')
                self.handleValve('V7', command='close')
                self.handleValve('V4', command='open')
                self.addTask(0, self.lowerPressure, [desiredPressure, fillPressure])
            else:
                self.handleValve('V7', command='close')
                self.addToLog('Exhaust to %.3g Torr complete (%.3g Torr), pumping was not necessary' % (desiredPressure, self.currentPressure()))
                self.setState('idle')
        elif self.state == 'pumping out':
            if self.currentPressure() > desiredPressure:
                if self.getValveStatus('V4') == 'close':
                    self.handleValve('V4', command='open')
                self.addTask(0, self.lowerPressure, [desiredPressure, fillPressure])
            else:
                self.handleValve('V4', command='close')
                self.addToLog('Pump out to %.3g Torr complete (%.3g Torr)' % (desiredPressure, self.currentPressure()))
                self.setState('idle')
                if fillPressure is not None:
                    self.setState('filling')
                    self.addTask(0, self.raisePressure, [fillPressure])
            
    def raisePressure(self, desiredPressure):
        if self.state == 'filling':
            if self.currentPressure() < desiredPressure:
                if self.getValveStatus('V5') == 'close':
                    self.addToLog('Beginning fill')
                    self.handleValve('V5', command='open')
                self.addTask(0, self.raisePressure, [desiredPressure])
            else:
                self.handleValve('V5', command='close')
                self.addToLog('Fill to %.3g Torr complete (%.3g Torr)' % (desiredPressure, self.currentPressure()))
                self.setState('idle')
            
    def changePressure(self, desiredPressure, pumpOut, exhaust):
        '''
        Raise or lower pressure as necessary.
        
        Args:
            desiredPressure: (Torr)
            pumpOut: (bool) whether to pump to 0 Torr before filling to desired pressure
            exhaust: (bool) whether to exhaust when pressure is > 770 Torr
        '''
        if desiredPressure < PUMPED_OUT or desiredPressure > MAX_FILL:
            self.addToLog('User requested an invalid pressure')
            return
        # Proceed with raising/lowering the pressure
        # Open V3 so that the absolute pressure gauge will be able to read
        self.handleValve('V3', command='open')
        if self.currentPressure() < desiredPressure and not pumpOut:
            self.setState('filling')
            self.raisePressure(desiredPressure)
        else:
            if exhaust:
                self.setState('exhaust')
            else:
                self.setState('pumping out')
            if pumpOut:
                self.lowerPressure(PUMPED_OUT, desiredPressure)
            else:
                self.lowerPressure(desiredPressure, None)
        
    def getFakePressureData(self):
        now = time.time()
        delta = 1/PRESSURE_HZ
        # Create fake data for testing purposes
        if self.absPressures:
            # Continue creaking fake data
            dp = 0
            currentPressure = self.currentPressure()
            valves = [self.getValveStatus('V3'), self.getValveStatus('V4'), self.getValveStatus('V5'), self.getValveStatus('V7'), self.getValveStatus('FV2')]
            if valves == ['open', 'close', 'close', 'open', 'close'] and currentPressure > 760:
                dp = -100
            elif valves == ['open', 'open', 'close', 'close', 'close'] and currentPressure > 0:
                dp = -100
            elif valves == ['open', 'close', 'open', 'close', 'close'] and currentPressure < 2000:
                dp = 100
            dataLen = int((now-self.lastFakeDataTime)*PRESSURE_HZ)
            self.absPressures.extend([(currentPressure+i*dp/PRESSURE_HZ)*np.random.normal(1, 0.05) for i in range(dataLen)])
            self.diffPressures.extend(np.random.normal(1, 0.01, dataLen))
            self.pressureTimes = np.arange(now-delta*(len(self.absPressures)-1), now+delta, delta)
            self.lastFakeDataTime = now
        else:
            # Initialize fake data
            self.absPressures = list(300*np.random.normal(1, 0.05, 10000))
            self.diffPressures = list(np.random.normal(1, 0.1, 10000))
            self.pressureTimes = np.arange(now-delta*(len(self.absPressures)-1), now+delta, delta)
            self.lastFakeDataTime = now
               
        self.processPressureData(now)
        
    def getPressureData(self):
        now = time.time()
        delta = 1/PRESSURE_HZ
        try:
            # Get data from RP
            # This may raise an exception due to network timeout
            combined_pressure_history = self.RPKoheron.get_GPI_data()
                    
            # Add fast readings
            self.absPressures.extend([abs_torr(i) for i in combined_pressure_history])
            self.diffPressures.extend([diff_torr(i) for i in combined_pressure_history])
            self.pressureTimes = np.arange(now-delta*(len(self.absPressures)-1), now+delta, delta)
            
            if len(combined_pressure_history) == 50000:
                # Show this message except during program startup, when the FPGA queue is normally full
                if self.gotFirstQueue:
                    self.addToLog('Lost some data due to network lag')
                else:
                    self.gotFirstQueue = True
        except Exception as e:
            # Log disconnection and attempt to reconnect
            self.addToLog(str(e))
            self.addToLog('Attempting to reconnect to RP')
            rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
            self.RPKoheron = GPI_RP(rpConnection)
        
        self.processPressureData(now)
            
    def processPressureData(self, now):
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
            self.addToLog('OPENING shutter')
            value = 1
        elif state == 'close':
            self.addToLog('CLOSING shutter')
            value = 0
        else:
            self.addToLog('Bad shutter command')
            return
        self.RPKoheron.set_analog_out(value)
        
    def handleToggleShutter(self):
        currentSetting = self.RPKoheron.get_analog_out()
        if currentSetting == 0:
            self.setShutter('open')
        elif currentSetting == 1:
            self.setShutter('close')
        else:
            self.addToLog('Shutter register has bad value')
            
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
        self.addToLog(action_text + ' ' + valve_name)
            
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
            self.addToLog('Error: puff 1 must be used')
            return
        # Puff 1 should never bleed into puff 2
        if puff_1_happening and puff_2_happening:
            if not p['puff_1_start'] + p['puff_1_duration'] < p['puff_2_start']:
                self.addToLog('Error: puff 1 would bleed into puff 2')
                return
        
        self.setState('shot')
        self.addToLog('---T0---')
        self.addTask(PRETRIGGER, self.addToLog, args=['---T1---'])
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
            self.addTask(PRETRIGGER+p['puff_1_start'], self.addToLog, ['Puff 1 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_1(2+int(bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_1(2+int(bothPuffsDone*1000))
        if puff_2_happening:
            self.RPKoheron.set_fast_delay_2(int(p['puff_2_start']*1000))
            self.RPKoheron.set_fast_duration_2(int(p['puff_2_duration']*1000))
            self.addTask(PRETRIGGER+p['puff_2_start'], self.addToLog, ['Puff 2 should happen now'])
        else:
            self.RPKoheron.set_fast_delay_2(2+int(bothPuffsDone*1000))
            self.RPKoheron.set_fast_duration_2(2+int(bothPuffsDone*1000))


if __name__ == '__main__':
    rp = RPServer()
