# Log 3 - Test the active buzzer on GPIO 5
from machine import Pin
from time import sleep

buzzer = Pin(5, Pin.OUT)
buzzer.on()
sleep(1)
buzzer.off()
