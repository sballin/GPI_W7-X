#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import time

from GPI_2 import GPI_2
from koheron import connect

GPI_host = os.getenv('HOST', 'rp1')
GPI_client = connect(GPI_host, name='GPI_2')
driver = GPI_2(GPI_client)


while True:
	driver.set_slow_1_trigger(0)
	time.sleep(1)
	driver.set_slow_1_trigger(1)
	time.sleep(1)

