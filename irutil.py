import json
import time

import RPi.GPIO as GPIO
import pigpio
from dotenv import dotenv_values

config = {
    **dotenv_values('.env'),
    **dotenv_values('.env.local'),
}

GPIO.setmode(GPIO.BCM)

IR_RX_PIN = int(config['GPIO_BCM_PIN_NO_IR'])
GLITCH = 100
PRE_MS = 200
POST_MS = 15
FREQ = 38.0
SHORT = 10
TOLERANCE = 15

POST_US = POST_MS * 1000
PRE_US = PRE_MS * 1000
TOLER_MIN = (100 - TOLERANCE) / 100.0
TOLER_MAX = (100 + TOLERANCE) / 100.0

pi = pigpio.pi()  # Connect to Pi.

if not pi.connected:
    exit(0)

print('GPIO connect OK.')

last_tick = 0
in_code = False
code = []
fetching_code = False


def normalise(c):
    entries = len(c)
    p = [0] * entries  # Set all entries not processed.
    for i in range(entries):
        if not p[i]:  # Not processed?
            v = c[i]
            tot = v
            similar = 1.0

            # Find all pulses with similar lengths to the start pulse.
            for j in range(i + 2, entries, 2):
                if not p[j]:  # Unprocessed.
                    if (c[j] * TOLER_MIN) < v < (c[j] * TOLER_MAX):  # Similar.
                        tot = tot + c[j]
                        similar += 1.0

            # Calculate the average pulse length.
            newv = round(tot / similar, 2)
            c[i] = newv

            # Set all similar pulses to the average value.
            for j in range(i + 2, entries, 2):
                if not p[j]:  # Unprocessed.
                    if (c[j] * TOLER_MIN) < v < (c[j] * TOLER_MAX):  # Similar.
                        c[j] = newv
                        p[j] = 1


def compare(p1, p2):
    if len(p1) != len(p2):
        return False

    #    print(f'compare {p1}, {p2}')

    for i in range(len(p1)):
        v = p1[i] / p2[i]
        if (v < TOLER_MIN) or (v > TOLER_MAX):
            return False

    #    print('HIT!!')
    for i in range(len(p1)):
        p1[i] = int(round((p1[i] + p2[i]) / 2.0))

    return True


def end_of_code():
    global code, fetching_code

    print('end_of_code')

    if len(code) > SHORT:
        normalise(code)
        fetching_code = False
    #        print(code)
    else:
        code = []
        print("Short code, probably a repeat, try again")


def cbf(gpio, level, tick):
    global last_tick, in_code, code, fetching_code

#    print(f'START cbf {level} {tick}')
    if level != pigpio.TIMEOUT:

        edge = pigpio.tickDiff(last_tick, tick)
        last_tick = tick

        if fetching_code:

            if (edge > PRE_US) and (not in_code):  # Start of a code.
                in_code = True
                pi.set_watchdog(IR_RX_PIN, POST_MS)  # Start watchdog.

            elif (edge > POST_US) and in_code:  # End of a code.
                in_code = False
                pi.set_watchdog(IR_RX_PIN, 0)  # Cancel watchdog.
                end_of_code()

            elif in_code:
                code.append(edge)

    else:
        pi.set_watchdog(IR_RX_PIN, 0)  # Cancel watchdog.
        if in_code:
            in_code = False
            end_of_code()


with open('codes.json') as f:
    key_config = json.load(f)

    pi.set_mode(IR_RX_PIN, pigpio.INPUT)

    pi.set_glitch_filter(IR_RX_PIN, GLITCH)

    cb = pi.callback(IR_RX_PIN, pigpio.EITHER_EDGE, cbf)

    print('FINISH set ir callback method')


class InfraredServer:

    def __init__(self, callback, *args):
        self.callback = callback
        print('InfraredServer::init start')
        pass

    def start(self):
        global code, fetching_code
        print('InfraredServer::start')
        try:
            while True:
                code = []
                fetching_code = True
                while fetching_code:
                    # print('time.sleep(0.1)')
                    time.sleep(0.1)
                print('fetching_code = False')
                time.sleep(0.1)
                key_name = "-"
                for key, val in key_config.items():
                    if compare(val, code[:]):
                        key_name = key
                print(f'key_name = {key_name}')
                self.callback(key_name)

        except KeyboardInterrupt:
            pass
        finally:
            pi.stop()  # Disconnect from Pi.

