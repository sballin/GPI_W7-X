import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from scipy.misc import derivative
from scipy.signal import medfilt


PLENUM_VOLUME = 0.802 # L 

datafile = sys.argv[1]
t, dp = np.load(datafile)

plt.figure()
plt.suptitle(datafile.split('.npy')[0])
plt.subplot(211)
pressures = medfilt(dp, 11)
plt.plot(t, dp)
plt.ylabel('Diff. pressure (Torr)')
plt.subplot(212)
f = interp1d(t, dp, kind='linear')
newtimes = np.arange(t[0], t[-1], 0.0005)
dp_coarse = [PLENUM_VOLUME*derivative(f, ti, dx=.02) for ti in newtimes[100:-100]]
dp_fine = [PLENUM_VOLUME*derivative(f, ti, dx=.005) for ti in newtimes[100:-100]]
plt.plot(newtimes[100:-100], medfilt(dp_fine,11))
plt.plot(newtimes[100:-100], medfilt(dp_coarse,11))
plt.xlabel('t-T1 (s)')
plt.ylabel('Flow rate (Torr-L/sec)')
plt.savefig(datafile.split('.npy')[0] + '.png', dpi=300)
plt.show()
