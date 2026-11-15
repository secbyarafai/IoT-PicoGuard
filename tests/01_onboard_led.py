# Log 1 - Confirm the Pico W works by blinking the onboard LED once
from machine import Pin
from time import sleep

led = Pin('LED', Pin.OUT)
led.on()
sleep(1)
led.off()
