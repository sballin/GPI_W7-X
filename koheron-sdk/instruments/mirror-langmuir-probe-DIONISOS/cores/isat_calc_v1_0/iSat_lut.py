# Python script to generate the saturation current look up table

import numpy as np
#import matplotlib.pyplot as plt

dataArray = []

xVal = np.linspace(-8, 8, num=2**13)

def lutFunction(x):
    exp = np.exp(x)
    func = 1/(exp - 1)
    if x > -1 and x < 1:
        func = func*(2**2)
    else:
        func = func*(2**13)

    return int(round(func))

for i in range(len(xVal)):
    dataArray.append(round(lutFunction(xVal[i])))

#dataArray = np.array(dataArray)

with open("iSat_lut.coe", "w") as lut_file:
    lut_file.write("memory_initialization_radix=10;\n")
    lut_file.write("memory_initialization_vector=")
    for val in dataArray:
        lut_file.write("%i " % val) 
