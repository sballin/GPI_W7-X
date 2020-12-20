#!/usr/bin/env python
import os
from os.path import dirname, realpath
import sys

root = dirname(dirname(dirname(realpath(__file__))))
sys.path.insert(0, root + "/instruments")
sys.path.insert(0, root + "/python")

import koheron
from GPI_RP.GPI_RP import GPI_RP
import time
import numpy
import subprocess
import signal

serverd = root + '/tmp/instruments/GPI_RP/serverd'
p = subprocess.Popen(serverd)
print(serverd)
time.sleep(.1)

c = koheron.connect('localhost', name='GPI_RP')
rp = GPI_RP(c)
times = []

start = time.time()
try:
    while True:
        time.sleep(time.time() - start + .1)
        start = time.time()
        data = rp.get_GPI_data()
        print(hex(data[0]) if data.size else [], len(data))
finally:
    p.terminate()
    p.wait()
