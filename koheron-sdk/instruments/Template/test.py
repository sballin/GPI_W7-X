#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import time

from PCS import PCS
from koheron import connect

host = os.getenv('HOST', 'rp4')
client = connect(host, name='Template')
driver = Template(client)




driver.set_reg_1(500)
driver.set_reg_2(2)
driver.get_reg_1()

