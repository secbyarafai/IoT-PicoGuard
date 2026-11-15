# Log 5 - 300ms debounce: only count motion if the PIR stays HIGH for 300ms
from machine import Pin
from time import ticks_ms, ticks_diff

pir = Pin(16, Pin.IN, Pin.PULL_DOWN)
DEBOUNCE = 300
motion_start = 0

while True:
    if pir.value() == 1:
        if motion_start == 0:
            motion_start = ticks_ms()
        elif ticks_diff(ticks_ms(), motion_start) > DEBOUNCE:
            print('Confirmed motion!')
    else:
        motion_start = 0
