# Log 8 - Poll Telegram for /arm and /disarm commands
# Run 06_wifi.py first (or connect to Wi-Fi) before running this.
import urequests
from time import sleep
from secrets import BOT_TOKEN, CHAT_ID

BASE_URL = 'https://api.telegram.org/bot' + BOT_TOKEN
last_id = 0
system_armed = True


def get_updates(offset):
    url = BASE_URL + '/getUpdates?timeout=1&offset=' + str(offset)
    r = urequests.get(url, timeout=5)
    data = r.json()
    r.close()
    return data


while True:
    for update in get_updates(last_id + 1).get('result', []):
        last_id = update['update_id']
        msg = update.get('message', {})
        # Only accept commands from the owner's chat ID
        if str(msg.get('chat', {}).get('id')) != CHAT_ID:
            continue
        text = msg.get('text', '')
        if text == '/arm':
            system_armed = True
        elif text == '/disarm':
            system_armed = False
        print('Command:', text, '| armed =', system_armed)
    sleep(2)
