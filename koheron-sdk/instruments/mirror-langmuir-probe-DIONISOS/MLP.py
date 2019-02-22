#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math
import numpy as np

from koheron import command

class MLP(object):
    def __init__(self, client):
        self.client = client
        # self.n_pts = 16384
        self.n_pts = 8192
        self.fs = 125e6 # sampling frequency (Hz)

        self.adc = np.zeros((2, self.n_pts))
        self.dac = np.zeros((2, self.n_pts))


    @command()
    def set_trigger(self):
        pass

    @command()
    def set_output(self):
        pass
    
    @command()
    def set_led(self, led):
        pass
 
    @command()
    def set_lower_temp_lim(self, lower_temp_lim):
        pass

    @command()
    def set_upper_temp_lim(self, upper_temp_lim):
        pass

    @command()
    def set_period(self, period):
        pass

    @command()
    def set_acquisition_length(self, acquisition_length):
        pass

    @command()
    def set_scale_LB(self, scale_LB):
        pass

    @command()
    def set_scale_PC(self, scale_PC):
        pass

    @command()
    def set_offset_LB(self, offset_LB):
        pass

    @command()
    def set_offset_PC(self, offset_PC):
        pass
    
    @command()
    def get_Temperature(self):
        return self.client.recv_uint32()

    @command()
    def get_Isaturation(self):
        return self.client.recv_uint32()

    @command()
    def get_vFloat(self):
        return self.client.recv_uint32()   

    @command()
    def get_MLP_data(self):
        return self.client.recv_vector(dtype='uint32')

    @command()
    def get_buffer_length(self):
        return self.client.recv_uint32() 

    @command()
    def reset_fifo(self):
        pass

