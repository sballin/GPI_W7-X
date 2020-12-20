#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math
import numpy as np

from koheron import command

class PCS(object):
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
    def set_Time_in(self, Time_in):
        pass

    @command()
    def set_ISat(self, ISat):
        pass

    @command()
    def set_Temperature(self, Temperature):
        pass

    @command()
    def set_Vfloating(self, Vfloating):
        pass

    @command()
    def set_Resistence(self, Resistence):
        pass

    @command()
    def set_Switch(self, Switch):
        pass

    @command()
    def set_Resistence(self, Resistence):
        pass

    @command()
    def set_Calibration_offset(self, Calibration_offset):
        pass

    @command()
    def set_Calibration_scale(self, Calibration_scale):
        pass



    @command()
    def get_Current(self):
        return self.client.recv_uint32()

    @command()
    def get_Bias(self):
        return self.client.recv_uint32()

    @command()
    def get_fifo_length(self):
        return self.client.recv_uint32()

    @command()
    def get_buffer_length(self):
        return self.client.recv_uint32()

    @command()
    def get_PCR_data(self):
        return self.client.recv_vector(dtype='uint32')





