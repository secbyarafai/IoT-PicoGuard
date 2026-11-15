# IoT PicoGuard - Smart Intruder Alarm
# Raspberry Pi Pico W + HC-SR501 PIR + active buzzer + LED + Telegram Bot API
#
# Wiring:  PIR OUT -> GPIO 16 | Buzzer + -> GPIO 5 | LED (330 ohm) -> GPIO 9
# Setup:   copy secrets.example.py to secrets.py and fill in your values.

import network
import urequests
import os
from machine import Pin
from time import sleep, ticks_ms, ticks_diff
from secrets import SSID, PASSWORD, BOT_TOKEN, CHAT_ID

# ---------------- Settings ----------------
DEBOUNCE_MS = 300          # PIR must stay HIGH this long to count as motion
COOLDOWN_MS = 30000        # minimum gap between two alerts
POLL_MS = 2000             # how often to check Telegram for commands
LOG_FILE = 'log.txt'
BASE_URL = 'https://api.telegram.org/bot' + BOT_TOKEN

# ---------------- Hardware ----------------
pir = Pin(16, Pin.IN, Pin.PULL_DOWN)
buzzer = Pin(5, Pin.OUT)
led = Pin(9, Pin.OUT)
wlan = network.WLAN(network.STA_IF)

# ---------------- State ----------------
system_armed = True
last_update_id = 0
motion_start = 0
last_alert = -COOLDOWN_MS
last_poll = 0


# ---------------- Wi-Fi ----------------
def connect_wifi():
    wlan.active(True)
    if wlan.isconnected():
        return True
    print('Connecting to Wi-Fi...')
    wlan.connect(SSID, PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            print('Connected:', wlan.ifconfig()[0])
            return True
        sleep(1)
    print('Wi-Fi connection failed, will retry')
    return False


# ---------------- Logging ----------------
def get_timestamp():
    try:
        r = urequests.get(
            'https://timeapi.io/api/Time/current/zone?timeZone=Europe/London',
            timeout=5)
        t = r.json()
        r.close()
        return t['dateTime'][:19].replace('T', ' ')
    except Exception:
        return 'time unavailable'


def init_log():
    try:
        os.stat(LOG_FILE)
    except OSError:
        with open(LOG_FILE, 'w') as f:
            f.write('=== Intruder Detection Log ===\n')


def log_event(event_type, detail=''):
    entry = '[{}] {} - {}'.format(get_timestamp(), event_type, detail)
    print(entry)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')


def read_log():
    with open(LOG_FILE) as f:
        text = f.read()
    # Telegram messages are limited to 4096 characters - send the newest part
    return text[-4000:]


# ---------------- Telegram ----------------
def send_message(text):
    if not connect_wifi():
        return
    try:
        payload = {'chat_id': CHAT_ID, 'text': text}
        r = urequests.post(BASE_URL + '/sendMessage', json=payload)
        r.close()
    except Exception as e:
        print('Send failed:', e)


def get_updates(offset):
    try:
        url = BASE_URL + '/getUpdates?timeout=1&offset=' + str(offset)
        r = urequests.get(url, timeout=5)
        data = r.json()
        r.close()
        return data.get('result', [])
    except Exception as e:
        print('Update check failed:', e)
        return []


def handle_commands():
    global last_update_id, system_armed
    for update in get_updates(last_update_id + 1):
        last_update_id = update['update_id']
        msg = update.get('message', {})

        # Security: ignore anyone who is not the owner
        if str(msg.get('chat', {}).get('id')) != str(CHAT_ID):
            log_event('BLOCKED', 'command from unknown chat')
            continue

        text = msg.get('text', '').strip().lower()
        if text == '/arm':
            system_armed = True
            log_event('ARMED', 'via Telegram')
            send_message('🔒 System ARMED')
        elif text == '/disarm':
            system_armed = False
            alarm_off()
            log_event('DISARMED', 'via Telegram')
            send_message('🔓 System DISARMED')
        elif text == '/status':
            state = 'ARMED 🔒' if system_armed else 'DISARMED 🔓'
            send_message('Status: ' + state)
        elif text == '/logs':
            send_message(read_log())
        else:
            send_message('Commands: /arm /disarm /status /logs')


# ---------------- Alarm ----------------
def alarm_off():
    buzzer.off()
    led.off()


def sound_alarm(cycles=10):
    # Fast siren pattern on the buzzer and LED
    for _ in range(cycles):
        buzzer.on()
        led.on()
        sleep(0.1)
        buzzer.off()
        led.off()
        sleep(0.1)


def check_motion():
    """Return True once motion has been HIGH for at least DEBOUNCE_MS."""
    global motion_start
    if pir.value() == 1:
        if motion_start == 0:
            motion_start = ticks_ms()
        elif ticks_diff(ticks_ms(), motion_start) > DEBOUNCE_MS:
            motion_start = 0
            return True
    else:
        motion_start = 0
    return False


# ---------------- Main loop ----------------
def main():
    global last_alert, last_poll
    init_log()
    connect_wifi()
    log_event('STARTUP', 'system online')
    send_message('✅ PicoGuard online. Send /status, /arm, /disarm or /logs')

    while True:
        # Self-healing Wi-Fi
        if not wlan.isconnected():
            connect_wifi()

        # Motion detection with cooldown
        if system_armed and check_motion():
            now = ticks_ms()
            if ticks_diff(now, last_alert) > COOLDOWN_MS:
                last_alert = now
                send_message('⚠️ Motion detected! Intruder alert.')
                log_event('MOTION', 'PIR triggered')
                sound_alarm()

        # Check Telegram for commands every POLL_MS
        if ticks_diff(ticks_ms(), last_poll) > POLL_MS:
            last_poll = ticks_ms()
            if wlan.isconnected():
                handle_commands()

        sleep(0.05)


try:
    main()
except KeyboardInterrupt:
    alarm_off()
    print('Stopped')
