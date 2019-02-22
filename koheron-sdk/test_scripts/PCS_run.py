#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import time

from PCS import PCS
from koheron import connect

host = os.getenv('HOST', 'rp3')
client = connect(host, name='plasma-current-response')
driver = PCS(client)

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

driver.set_Temperature(100)
driver.set_ISat(int(int2signed(-2),2))
driver.set_Vfloating(int(int2signed(0),2))
driver.set_Resistence(50)
driver.set_Switch(1)
driver.set_Calibration_offset(0)
driver.set_Calibration_scale(1024)

driver.set_Time_in(1000)
driver.set_trigger()
 
while True:
	try:
		time.sleep(0.2)
		samples = driver.get_buffer_length()
		if samples == 0:
			break
		print(samples)
	except KeyboardInterrupt:
		break

dataArray = driver.get_PCR_data()

saveStr = "PCR_test_data"
print(saveStr)
np.save(saveStr, dataArray)

print("Current is: ",driver.get_Current())
print("Bias is: ",driver.get_Bias())


