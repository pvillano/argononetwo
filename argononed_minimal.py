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
    bus.write_byte(FAN_BUS_ADDRESSS, int(fan_speed))


def temp_check():
    max_temp = 60
    fan_off = 40
    fan_on = 50
    min_speed = 1
    max_acceleration = 1  # .1 % fan speed per second
    update_interval = 1

    current_speed = 100
    set_fan(current_speed)
    time.sleep(update_interval)
    while True:
        current_temperature = get_temp()
        if current_temperature < fan_off:
            set_fan(0)
            current_speed = 0
        elif current_temperature > fan_on:

            percent_fan = unlerp(fan_on, max_temp, current_temperature)
            target_speed = lerp(min_speed, 100, percent_fan)

            if target_speed > current_speed:
                set_fan(target_speed)
                current_speed = target_speed
            else:
                target_speed -= max_acceleration * update_interval
                set_fan(current_speed)
                current_speed = target_speed
        time.sleep(update_interval)


def lerp(a, b, t):
    return a + (b - a) * t


def unlerp(a, b, x):
    return (x - a) / (b - a)


if __name__ == "__main__":
    main()
