# Log 6 - Connect the Pico W to Wi-Fi (credentials live in secrets.py)
import network
from time import sleep
from secrets import SSID, PASSWORD

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    sleep(1)
    print('Connecting...')

print('Connected:', wlan.ifconfig())
