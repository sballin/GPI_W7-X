#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math
import numpy as np

from koheron import command

class GPI_RP(object):
    def __init__(self, client):
        self.client = client
        # self.n_pts = 16384
        self.n_pts = 8192
        self.fs = 125e6 # sampling frequency (Hz)

        self.adc = np.zeros((2, self.n_pts))
        self.dac = np.zeros((2, self.n_pts))

    @command()
    def set_led(self, led):
        pass

    @command()
    def set_analog_out(self, analog_out):
        '''
        Controls the 4 analog output pins on E2. AO0 is controlled by 0b0000/0b0001, AO1 with 
        0b0000/0b0010, etc.
        '''
        pass

    @command()
    def get_fifo_length(self):
        return self.client.recv_uint32()

    @command()
    def get_buffer_length(self):
        return self.client.recv_uint32()

    @command()
    def get_GPI_data(self):
        return self.client.recv_vector(dtype='uint32')

    @command()
    def reset_fifo(self):
        pass

    @command()
    def set_GPI_safe_state(self, state):
        pass

    @command()
    def set_slow_1(self, state):
        pass

    @command()
    def set_slow_2(self, state):
        pass

    @command()
    def set_slow_3(self, state):
        pass

    @command()
    def set_slow_4(self, state):
        pass

    @command()
    def reset_time(self, state):
        pass

    @command()
    def set_fast(self, state):
        pass

    @command()
    def set_fast_permission_1(self, state):
        pass
        
    @command()
    def set_fast_permission_2(self, state):
        pass
        
    @command()
    def set_fast_permission_3(self, state):
        pass
        
    @command()
    def set_fast_permission_4(self, state):
        pass

    @command()
    def set_fast_delay_1(self, state):
        pass
        
    @command()
    def set_fast_delay_2(self, state):
        pass
        
    @command()
    def set_fast_delay_3(self, state):
        pass
        
    @command()
    def set_fast_delay_4(self, state):
        pass
        
    @command()
    def set_fast_duration_1(self, state):
        pass
        
    @command()
    def set_fast_duration_2(self, state):
        pass
        
    @command()
    def set_fast_duration_3(self, state):
        pass
        
    @command()
    def set_fast_duration_4(self, state):
        pass
         
    @command()
    def send_T1(self, state):
        pass

    @command()
    def get_W7X_permission(self):
        return self.client.recv_uint32()
        
    @command()
    def get_W7X_T1(self):
        return self.client.recv_uint32()
    
    @command()
    def get_analog_out(self):
        return self.client.recv_uint32()

    @command()
    def get_abs_gauge(self):
        return self.client.recv_uint32()

    @command()
    def get_diff_gauge(self):
        return self.client.recv_uint32()

    @command()
    def get_analog_input_0(self):
        return self.client.recv_uint32()

    @command()
    def get_analog_input_1(self):
        return self.client.recv_uint32()

    @command()
    def get_slow_1_sts(self):
        return self.client.recv_uint32()

    @command()
    def get_slow_2_sts(self):
        return self.client.recv_uint32()

    @command()
    def get_slow_3_sts(self):
        return self.client.recv_uint32()
        
    @command()
    def get_slow_4_sts(self):
        return self.client.recv_uint32()

    @command()
    def get_fast_sts(self):
        return self.client.recv_uint32()
