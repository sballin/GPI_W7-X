#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import time

from threevolt import MLP
from koheron import connect

host = os.getenv('HOST', 'rp1')
client = connect(host, name='three-volt-cycle')
driver = MLP(client)

#########################################################
# Function for converting an integer to a signed binary
def int2signed(convInt):
    convInt = int(np.floor(convInt))
    if convInt < 0:
        retBin = '{:032b}'.format(convInt & 0xffffffff)
    else:
        retBin = '{:032b}'.format(convInt)

    print(convInt, retBin)
        
    return retBin
##########################################################

driver.set_voltage_1(int(int2signed(100), 2))
driver.set_voltage_2(int(int2signed(500), 2))
driver.set_voltage_3(int(int2signed(50), 2))
driver.set_led(int(1250))

print("Loop back is: ", driver.get_LoopBack())
print("Bias is: ", driver.get_Bias())
print("Plasma Current is: ", driver.get_PlasmaCurrent())
