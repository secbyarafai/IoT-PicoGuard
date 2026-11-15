# Log 2 - Flash the external LED on GPIO 9 (1 second cycle)
from machine import Pin
from time import sleep

led = Pin(9, Pin.OUT)

while True:
    led.on()
    sleep(0.5)
    led.off()
    sleep(0.5)
