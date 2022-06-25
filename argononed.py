#!/usr/bin/python3
import smbus
import RPi.GPIO as GPIO
import os
import time
from threading import Thread

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
shutdown_pin = 4
GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def shutdown_check():
    while True:
        pulse_time = 1
        GPIO.wait_for_edge(shutdown_pin, GPIO.RISING)
        time.sleep(0.01)
        while GPIO.input(shutdown_pin) == GPIO.HIGH:
            time.sleep(0.01)
            pulse_time += 1
        if 2 <= pulse_time <= 3:
            os.system("reboot")
        elif 4 <= pulse_time <= 5:
            os.system("shutdown now -h")


def get_fanspeed(temp_val, config_list):
    for cur_config in config_list:
        cur_pair = cur_config.split("=")
        temp_cfg = float(cur_pair[0])
        fan_cfg = int(float(cur_pair[1]))
        if temp_val >= temp_cfg:
            if fan_cfg < 1:
                return 0
            elif fan_cfg < 25:
                return 25
            return fan_cfg
    return 0


def load_config(fname):
    new_config = []
    try:
        with open(fname, "r") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                if line[0] == "#":
                    continue
                temp_pair = line.split("=")
                if len(temp_pair) != 2:
                    continue
                try:
                    tempval = float(temp_pair[0])
                    if tempval < 0 or tempval > 100:
                        continue
                except:
                    continue
                try:
                    fanval = int(float(temp_pair[1]))
                    if fanval < 0 or fanval > 100:
                        continue
                except:
                    continue
                new_config.append("{:5.1f}={}".format(tempval, fanval))
        if len(new_config) > 0:
            new_config.sort(reverse=True)
    except:
        return []
    return new_config


def temp_check():
    fanconfig = ["65=100", "60=55", "55=10"]
    tmpconfig = load_config("/etc/argononed.conf")
    if len(tmpconfig) > 0:
        fanconfig = tmpconfig
    address = 0x1A
    prevblock = 0
    while True:
        try:
            tempfp = open("/sys/class/thermal/thermal_zone0/temp", "r")
            temp = tempfp.readline()
            tempfp.close()
            val = float(int(temp) / 1000)
        except IOError:
            val = 0
        block = get_fanspeed(val, fanconfig)
        if block < prevblock:
            time.sleep(30)
        prevblock = block
        try:
            if block > 0:
                bus.write_byte(address, 100)
                time.sleep(1)
            bus.write_byte(address, block)
        except IOError:
            temp = ""
        time.sleep(30)


t1 = Thread(target=shutdown_check)
t2 = Thread(target=temp_check)
try:
    t1.start()
    t2.start()
except:
    # t1.stop()
    # t2.stop()
    GPIO.cleanup()
