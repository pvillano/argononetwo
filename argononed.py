#!/usr/bin/python3
import sys

import smbus
import RPi.GPIO as GPIO
import os
import time
from threading import Thread

# bus = None
SHUTDOWN_PIN = 4
FAN_BUS_ADDRESSS = 0x1A
bus = None  # declaring global? idk
"""
no abbreviations because temp might mean temperature or temporary
"""

"""
    CPU soft-throttle is at 60c, hard-throttle at 80c
    recommended curve is 0=3 60=100, right?

    #background
    a computer uses an unknown amount of power and outputs an equal amount of heat
    fan removes heat
    delta T is proportional to power/airflow
    delta T also depends on room temp, which we do not know
    there are also delays and non-linearity mixed in

    delays lead to oscillation, non=linearity leads to oscillation

    if we knew room temp, power, heatsink characteristics, fan characteristics,
    we could set a

    # Design constraints
    don't constantly change fan speed
    be fail-safe
    find set point


    like, what is the goal with fan curves anyway? be as quiet as possible for a given acceptable wear rate
    is wear proportional to temperature?

"""
"""
    ok so with going between no fan and lowest speed

    heat removal rate at minspeed: 1 degree/cpu-watt
    heat removal rate at fan off:  2 degree/cpu-watt
        fan  pass
    wat delT delT
    0   0   0
    1   1   2
    2   2   4
    3   3   6

    at 2 watts, if transition at 3 degrees, oscillation
    at 1 watts, if transition at 1.5 degrees, oscillation

    hypothetical code: keep fan off until 10 degrees
        10 degrees passive implies minimum 5 watts
        5 watts lets fan bring down to 5 degrees
        fan should stay on until temp < 4.9 degrees
            now we have less than 5 watts
            turn off fan
    conclusion: knowing ratio of efficacy allows calculation of hysteresis

    
    """
"""
    main algorithm:
    60c+ = 100%
    
    target temp 55c
    if under slowly decrease
    if over slowly increase
    if at 60 jump to 100%
    
    slow ramp down
    unless temp rises
    
    fanless up to 59?
    then fans stay on until well under max wattage for no fan
"""

"""
    algorithm: estimate wattage
    deltaT = power/fan speed
    power = deltaT*fan speed
    new fan speed = power/max_deltaT
    
    
    
"""


def main():
    global bus
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    t1 = Thread(target=shutdown_check)
    t2 = Thread(target=temp_check)
    try:
        t1.start()
        t2.start()
    except:
        # t1.stop()
        # t2.stop()
        GPIO.cleanup()


def shutdown_check():
    """Unmodified because I didn't feel like it"""
    while True:
        pulse_time = 1
        GPIO.wait_for_edge(SHUTDOWN_PIN, GPIO.RISING)
        time.sleep(0.01)
        while GPIO.input(SHUTDOWN_PIN) == GPIO.HIGH:
            time.sleep(0.01)
            pulse_time += 1
        if 2 <= pulse_time <= 3:
            os.system("reboot")
        elif 4 <= pulse_time <= 5:
            os.system("shutdown now -h")


def parse_config_file(file_name):
    parsed_config = []
    with open(file_name, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            try:
                temp, fan_speed = line.split("=")
                temp, fan_speed = float(temp), float(fan_speed)
                if fan_speed > 100 or fan_speed < 0:
                    raise ValueError
            except ValueError:  # too many values, float parse failure, fan percent oob
                print(f"parse failed for line: ", line, file=sys.stderr, flush=True)
                continue
            parsed_config.append((temp, fan_speed))
        return sorted(parsed_config)


def get_temp() -> float:
    try:
        f = open("/sys/class/thermal/thermal_zone0/temp", "r")
        temp = f.readline()
        f.close()
        return int(temp) / 1000
    except IOError:
        raise ValueError  # idk


def set_fan(fan_speed: int):
    if fan_speed > 100 or fan_speed < 0:
        raise ValueError
    bus.write_byte(FAN_BUS_ADDRESSS, fan_speed)


def temp_check():
    parsed_config = parse_config_file("/etc/argononed.conf")
    if not parsed_config:
        parsed_config = [(20, 3), (55, 3), (65, 100)]

    set_fan(100)
    time.sleep(1)
    while True:
        current_temperature = get_temp()
        target_speed = interpolate(current_temperature, parsed_config)
        set_fan(target_speed)
        time.sleep(1)


def interpolate(value, spline):
    if value <= spline[0][0]:
        return spline[0][1]
    elif value >= spline[-1][0]:
        return spline[-1][1]
    else:
        for left, right in zip(spline, spline[1:]):
            if left[0] <= value <= right[0]:
                t = unlerp(left[0], right[0], value)
                return lerp(left[1], right[1], t)
    raise ValueError


def lerp(a, b, t):
    return a + (b - a) * t


def unlerp(a, b, x):
    return (x - a) / (b - a)


if __name__ == '__main__':
    main()
