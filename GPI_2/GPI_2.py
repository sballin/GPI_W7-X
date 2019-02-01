#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math
import numpy as np
from koheron import command


class GPI_2(object):
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
    def get_fifo_length(self):
        return self.client.recv_uint32()


    @command()
    def get_buffer_length(self):
        return self.client.recv_uint32()


    @command()
    def get_Template_data(self):
        return self.client.recv_vector(dtype='uint32')


    @command()
    def set_GPI_safe_state(self, state):
        pass


    @command()
    def set_slow_1_trigger(self, state):
        pass


    @command()
    def set_slow_2_trigger(self, state):
        pass


    @command()
    def set_slow_3_trigger(self, state):
        pass


    @command()
    def set_slow_4_trigger(self, state):
        pass


    @command()
    def reset_time(self, state):
        pass


    @command()
    def set_fast_1_trigger(self, state):
        pass


    @command()
    def set_fast_1_permission(self, state):
        pass


    @command()
    def set_fast_1_duration(self, state):
        pass


    @command()
    def set_fast_2_trigger(self, state):
        pass


    @command()
    def set_fast_2_permission(self, state):
        pass


    @command()
    def set_fast_2_duration(self, state):
        pass


    @command()
    def get_W7X_permission(self):
        return self.client.recv_uint32()


    @command()
    def get_abs_gauge(self):
        return self.client.recv_uint32()


    @command()
    def get_diff_gauge(self):
        return self.client.recv_uint32()


    @command()
    def get_slow_1_trigger_sts(self):
        return self.client.recv_uint32()


    @command()
    def get_slow_2_trigger_sts(self):
        return self.client.recv_uint32()


    @command()
    def get_slow_3_trigger_sts(self):
        return self.client.recv_uint32()


    @command()
    def get_slow_4_trigger_sts(self):
        return self.client.recv_uint32()

