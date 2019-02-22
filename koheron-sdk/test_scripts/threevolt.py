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
    def trig_pulse(self):
        pass

    @command()
    def set_led(self, led):
        pass

    @command()
    def set_voltage_1(self, voltage1):
        pass

    @command()
    def set_voltage_2(self, voltage2):
        pass

    @command()
    def set_voltage_3(self, voltage3):
        pass

    @command()
    def get_LoopBack(self):
        return self.client.recv_uint32()

    @command()
    def get_PlasmaCurrent(self):
        return self.client.recv_uint32()

    @command()
    def get_Bias(self):
        return self.client.recv_uint32()
