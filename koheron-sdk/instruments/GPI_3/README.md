# GPI controller



## Inputs



## Outputs

Red Pitaya outputs are connected to

- "Card 1"
    - Fast circuit board 1
    - Fast circuit board 2
- "Card 2": slow valve circuit board

### Slow valve opening circuit

```
J18 slow_1_trigger
K17 slow_2_trigger
L14 slow_3_trigger
L16 slow_4_trigger
```

### Fast valve openening circuit

There is only one fast valve, but there are two fast actuating circuits for redundancy. We will be using circuit 1 until it fries. Each circuit uses different pins to communicate with the Red Pitaya. To actuate the valve, each circuit requires both an open/close pulse and a constant permission signal. Each circuit has "registers" for two separate actuations (can't be simultaneous), and this entails two open/close pins and two permission pins.

```
# Fast circuit card 1
G18 fast_1_trigger       (manual open?)
H17 fast_1_permission_1  
H18 fast_1_duration_1    (pulse for open/close)
K18 fast_1_permission_2 
L15 fast_1_duration_2

# Fast circuit card 2
L17 fast_2_trigger
J16 fast_2_permission_1
M15 fast_2_duration_1
K16 fast_2_permission_2
M14 fast_2_duration_2
```

