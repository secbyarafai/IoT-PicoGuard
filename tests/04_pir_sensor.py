# Log 4 - Read the HC-SR501 PIR sensor on GPIO 16
from machine import Pin
from time import sleep

pir = Pin(16, Pin.IN, Pin.PULL_DOWN)

while True:
    if pir.value() == 1:
        print('Motion detected!')
    else:
        print('No motion')
    sleep(0.5)
