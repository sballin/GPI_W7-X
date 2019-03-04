import os
import time
import koheron
from GPI_RP.GPI_RP import GPI_RP
from pylab import *
import numpy as np

GPI_host = os.getenv('HOST', 'w7xrp2')
GPI_client = koheron.connect(GPI_host, name='GPI_RP')
GPI_driver = GPI_RP(GPI_client)

def signed_conversion(reading):
    '''
    Convert Red Pitaya binary output to a uint32.
    '''
    binConv = ""
    if int(reading[0], 2) == 1:
        for bit in reading[1::]:
            if bit == "1":
                binConv += "0"
            else:
                binConv += "1"
        intNum = -int(binConv, 2) - 1
    else:
        for bit in reading[1::]:
            binConv += bit
        intNum = int(binConv, 2)
    return intNum
    
    
def uint32_to_volts(reading):
    '''
    Not really volts, but proportional. 
    Calibration is inside diff_torr and abs_torr functions.
    '''
    return 2/(2**14-1)*signed_conversion(reading)
    
def abs_torr(combined_string):
    bin_number = "{0:032b}".format(combined_string)
    abs_voltage = 0.0661+4.526*uint32_to_volts(bin_number[-28:-14]) # calibration for IN 1 of W7XRP2 with a 0.252 divider 
    return 5000/10*abs_voltage
    
def diff_torr(combined_string):
    bin_number = "{0:032b}".format(combined_string)
    diff_voltage = 0.047+3.329*uint32_to_volts(bin_number[-14:]) # calibration for IN 2 of W7XRP2 with a 0.342 divider
    return 100/10*diff_voltage

    
gpi_data_1 = GPI_driver.get_GPI_data()
abs_hist_1 = [abs_torr(i) for i in gpi_data_1]
diff_hist_1 = [diff_torr(i) for i in gpi_data_1]
print('std abs 1', np.std(abs_hist_1)/np.mean(abs_hist_1))
print('std diff 1', np.std(diff_hist_1)/np.mean(diff_hist_1))
time.sleep(0.5)
gpi_data_2 = GPI_driver.get_GPI_data()
abs_hist_2 = [abs_torr(i) for i in gpi_data_2]
diff_hist_2 = [diff_torr(i) for i in gpi_data_2]
print('std abs 2', np.std(abs_hist_2)/np.mean(abs_hist_2))
print('std diff 2', np.std(diff_hist_2)/np.mean(diff_hist_2))
