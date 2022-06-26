#!/usr/bin/python3
import sys

import smbus
import RPi.GPIO as GPIO

FAN_BUS_ADDRESSS = 0x1A


def main():
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
    fan_speed = float(sys.argv[1])
    if fan_speed > 100 or fan_speed < 0:
        raise ValueError(f"Invalid fan speed {fan_speed}")
    bus.write_byte(FAN_BUS_ADDRESSS, int(fan_speed))
    print("set speed to fan_speed")


if __name__ == "__main__":
    main()
