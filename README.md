# W7-X gas puff imaging diagnostic codebase

![](https://user-images.githubusercontent.com/2719004/52680534-b71dbf00-2f06-11e9-89de-4859e10b7c67.png)

## Installation

Clone this repo or download the files. Running middle_server.py requires

    pip3 install bottleneck

and the presence of the koheron and koheron-sdk directories (avoid making it use the pip-installed koheron library).

Running gui.py requires

    pip3 install pillow numpy scipy matplotlib

The correct addresses must be set in the middle_server.py and gui.py files. middle_server.py and gui.py can be run on different computers or the same computer:

* middle_server.py will need to have RP_HOSTNAME set to the hostname or IP address of the Red Pitaya
* gui.py must have MIDDLE_SERVER_ADDR set to "hostname_or_ip:50000" where hostname_or_ip is for the machine on which the middle server is running.

## Usage

The "middle server" bridges communication between the gui and RP, and will eventually take care of uploading data to the Archive. Run it with

    python3 middle_server.py

In a separate terminal, you can run

    python3 gui.py

### Hardware and software T0/T1 triggers

The user can switch between hardware and software T1 modes by modifying the SOFTWARE_T1 variable in gui.py. "Software T1" mode does all slow valve and fast valve actions automatically after the user presses the T0 button. "Hardware T1" mode requires the user to press the T0 button, then supply a hardware T1 signal approximately N seconds after T0, where N is controlled by the PRETRIGGER variable that must be set near the top of middle_server.py and gui.py files. N should be accurate to within less than 1 second.

⚠️ Hardware T1 mode uses a signal on RP pin DIO1_P (H16). If you are doing software T1 triggering, this pin should be kept at a low voltage because a hardware T1 can occur due to the floating voltage.

# FPGA documentation

## Overview

The Red Pitaya running the code in koheron-sdk/instruments/GPI_RP has two jobs:

- Send open or close signals to several different valves
- Monitor pressure readings from two gauges using two fast analog inputs

## Valve control

Red Pitaya outputs are connected to the black box, which contains

- "Card 1"
    - Fast circuit board 1
    - Fast circuit board 2
- "Card 2": slow valve circuit board

[Circuit schematics](https://drive.google.com/file/d/1h2XiICZbf8ahQjyZW7o4v7BePNzfH2qf/view) for the black box are available.

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

Note that there is also a "w7x permission" signal going to the black box. This is processed by the black box, and not the RP, but the RP can view its value (binary low/high) in the status register named W7X_permission as the signal is connected to RP pin G17.

## Pressure monitoring

Every 0.1 ms, the `data_collector` core on the RP takes two 14-bit readings from two fast analog inputs and glues them together in a zero-padded 32-bit number before sending them to a FIFO queue core. This queue is checked every 1 ms and entries are stored in the C++ `adc_data_queue` as they are popped off. When queried via Python, `adc_data_queue` will get copied to the `adc_data` vector by popping all its entries, and the vector will be returned.

## Modifying the FPGA code

Requires Vivado 2017.4, which can be downloaded for free from [Xilinx](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/archive.html) (you will need to register for an account though). It takes up about 15 GB of space. 

## View the FPGA block diagram

In the koheron-sdk directory, do

    make CONFIG=instruments/GPI_RP/config.yml block_design

## Compiling the FPGA code

In the koheron-sdk directory, do

    make CONFIG=instruments/GPI_RP/config.yml all

## Upload FPGA code to Red Pitaya

In the koheron-sdk directory, do

    make CONFIG=instruments/GPI_RP/config.yml HOST=hostname_or_ip_goes_here run

or if you have the GPI_RP.zip file in your current directory, and you can ping the RP from your computer, simply do 

    HOST=hostname_or_ip_goes_here
    NAME=GPI_RP
    INSTRUMENT_ZIP=./GPI_RP.zip
    curl -v -F $(NAME).zip=@$(INSTRUMENT_ZIP) http://$(HOST)/api/instruments/upload
    curl http://$(HOST)/api/instruments/run/$(NAME)
