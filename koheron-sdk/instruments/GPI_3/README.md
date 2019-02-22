# GPI controller

## Overview

The Red Pitaya running this code will have two jobs:

- Send open or close signals to several different valves
- Monitor pressure readings from two gauges using two fast analog inputs

## Valve control

Red Pitaya outputs are connected to

- "Card 1"
    - Fast circuit board 1
    - Fast circuit board 2
- "Card 2": slow valve circuit board

[Circuit schematics](https://drive.google.com/file/d/14E3xMDY9xz2H-v23pEr-3am8calt1lfd/view) are available.

### Slow valves

These valves do not require precise timing to open or close. The following RP pins control them:

```
J18 slow_1_manual (called V5 in GUI)
K17 slow_2_manual (V4)
L14 slow_3_manual (V3, expects and returns inverted values rel. others)
L16 slow_4_manual (not used)
```

### Fast valves

This valve will need to open/close at precise times. The timing logic is implemented in the RP `trig_delay` core. The timer starts after a T1 signal is supplied, currently through the python/C++ bridge but eventually this will be a real signal going to one of the pins.

There is only one fast valve, but there are two fast actuating circuits for redundancy. We will have circuit 1 hard-coded in the RP logic and can switch to circuit 2 if it fries. Each circuit uses different pins to communicate with the RP. To actuate the valve with the timing logic, each circuit requires both an open/close pulse and a constant permission signal. Each circuit has "registers" for two separate actuations (order doesn't matter), and this entails two open/close pins and two permission pins. The valves can also be actuated manually at any time without permission using a different set of pins—we won't be using this feature regularly.

```
# Fast circuit card 1
G18 fast_manual        (actuate FV2 at any time without permission)
H17 fast_permission_1  (required for fast_puff_1 signal to have any effect)
H18 fast_puff_1        (pulse to open/close)
K18 fast_permission_2  (required for fast_puff_2 signal to have any effect)
L15 fast_puff_2        (pulse to open/close at a different time)

# Fast circuit card 2
L17 fast_manual
J16 fast_permission_1
M15 fast_puff_1
K16 fast_permission_2
M14 fast_puff_2
```

## Pressure monitoring

Every 0.1 ms, the `data_collector` core on the RP takes two 14-bit readings from two fast analog inputs and glues them together in a zero-padded 32-bit number before sending them to a FIFO queue core. This queue is checked every 1 ms and entries are stored in the C++ `adc_data_queue` as they are popped off. When queried via Python, `adc_data_queue` will get copied to the `adc_data` vector by popping all its entries, and the vector will be returned.