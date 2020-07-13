'''
Server for valve control and data acquisition in GPI system at W7-X.
'''

import os
import time
import math
import datetime
import logging
import xmlrpc.server
import koheron
import numpy as np
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.signal import medfilt
from GPI_RP.GPI_RP import GPI_RP


RP_HOSTNAME = 'rp3' # hostname of red pitaya being used
FAKE_RP = True
UPDATE_INTERVAL = 1  # seconds between plot updates
CONTROL_INTERVAL = 0.2 # seconds between pump/fill loop iterations
PLOT_TIME_RANGE = 30 # seconds of history shown in plots
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
        address = ('localhost', 50000)
        self.server = xmlrpc.server.SimpleXMLRPCServer(address)
        self.server.register_instance(self)
        
        rpConnection = koheron.connect(RP_HOSTNAME, name='GPI_RP')
        self.rpKoheron = GPI_RP(rpConnection)
        self.pressure_times = []
        self.abs_pressures = []
        self.diff_pressures = []
        self.pressure_avg_times = []
        self.abs_avg_pressures = []
        self.diff_avg_pressures = []
        
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
        
        self.last_plot = time.time() + UPDATE_INTERVAL # +... to get more fast data before first average
        
    def mainloop(self):
        print('Serving...') 
        while True:
            self._getData()
            print(len(self.abs_pressures), len(self.diff_pressures))
            self.server.handle_request()
            
    def test(self):
        return 1
        
    def init(self):
        pass
        
    def pumpoutRefill(self):
        pass
        
    def disarm(self):
        pass
    
    def arm(self):
        pass
        
    def store(self):
        pass
        
    def _getData(self):
        # Add fast readings
        combined_pressure_history = self.rpKoheron.get_GPI_data()
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
            self.last_plot = now


if __name__ == '__main__':
    rp = RPServer()
    rp.mainloop()
