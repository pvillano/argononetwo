from typing import *

"""
    every simulation block must be put,take,put...
"""


def pi1(fan_speed: Iterable[float], wattage=10, fan_efficacy=1, thermal_mass=0):
    temperature = 20
    yield temperature
    for fan_percent in fan_speed:
        temperature = wattage / (fan_percent * fan_efficacy)
        yield temperature


def algorithm1(pi, setpoint=35):
    fanspeed = 100
    yield fanspeed
    next(pi)
    yield fanspeed
    for temperature in pi:
        power = temperature * fanspeed
        fanspeed = power / setpoint
        yield fanspeed


def run_sim(pi, algorithm, steps=20):
    temperature_list = []
    fan_speed_list = []
    my_pi = pi(iter(fan_speed_list))
    my_algorithm = algorithm(iter(temperature_list))
    for i in range(steps):
        next_temperature = next(my_pi)
        next_speed = next(my_algorithm)
        temperature_list.append(next_temperature)
        fan_speed_list.append(next_speed)
        print(f"{i: 2} {next_temperature: 3.1f} {next_speed: 3.1f}")


if __name__ == '__main__':
    run_sim(pi1, algorithm1)