# Log 7 - Send a test alert through the Telegram Bot API over HTTPS
# Run 06_wifi.py first (or connect to Wi-Fi) before running this.
import urequests
from secrets import BOT_TOKEN, CHAT_ID

URL = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage'
payload = '{"chat_id":"' + CHAT_ID + '","text":"Test alert!"}'

response = urequests.post(URL, data=payload,
    headers={'Content-Type': 'application/json'})
response.close()
print('Alert sent!')
