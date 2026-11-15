# Log 9 - Append timestamped events to log.txt on the Pico's flash memory
import os
import time

LOG_FILE = 'log.txt'


def init_log():
    try:
        os.stat(LOG_FILE)
    except OSError:
        with open(LOG_FILE, 'w') as f:
            f.write('=== Intruder Detection Log ===\n')


def log_event(event_type, detail=''):
    # The full project took its timestamp from timeapi.io;
    # the Pico's local clock is used here so this test runs offline.
    t = time.localtime()
    timestamp = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(*t[:6])
    entry = '[{}] {} - {}'.format(timestamp, event_type, detail)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')


init_log()
log_event('TEST', 'log file working')
print(open(LOG_FILE).read())
