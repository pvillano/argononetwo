from typing import *

"""
    every simulation block must be put,take,put...
    
    0 <= fan speed <= 1
    temp > 20
    fan efficacy = watts/degree steady state
"""
ROOM_TEMPERATURE = 20


def clamp01(x):
    return min(max(x, 0), 1)


def pi1(fan_speed: Iterable[float], wattage=10, fan_efficacy=1):
    temperature = ROOM_TEMPERATURE
    yield temperature
    for fan_percent in fan_speed:
        temperature = wattage / (fan_percent * fan_efficacy)
        yield temperature


def pi2(fan_speed: Iterable[float], step=.1, wattage=20, fan_efficacy=1, passive_efficacy=.2, thermal_mass=20):
    temperature = ROOM_TEMPERATURE
    energy = 0
    yield temperature
    for fan_percent in fan_speed:
        energy += wattage * step
        temperature = energy / thermal_mass + ROOM_TEMPERATURE
        delta_e = (temperature - ROOM_TEMPERATURE) * (fan_percent * fan_efficacy + passive_efficacy) * step
        assert delta_e >= 0
        assert delta_e < energy
        energy -= delta_e
        temperature = energy / thermal_mass + ROOM_TEMPERATURE
        yield temperature


def algorithm1(pi, step=.1, setpoint=65, multiplier=1.5):
    fanspeed = .9
    yield fanspeed
    next(pi)
    yield fanspeed
    for temperature in pi:
        power = (temperature - ROOM_TEMPERATURE) * fanspeed * multiplier
        fanspeed = power / setpoint
        yield clamp01(fanspeed)


def run_sim(pi, algorithm, steps=99999):
    temperature_list = []
    fan_speed_list = []
    my_pi = pi(iter(fan_speed_list))
    my_algorithm = algorithm(iter(temperature_list))
    for i in range(steps):
        next_temperature = next(my_pi)
        next_speed = next(my_algorithm)
        assert 0 <= next_speed <= 1
        temperature_list.append(next_temperature)
        fan_speed_list.append(next_speed)
        print(f"{i: 9d} {next_temperature: 9.1f} {next_speed: 9.1f}")


if __name__ == '__main__':
    run_sim(pi2, algorithm1)
