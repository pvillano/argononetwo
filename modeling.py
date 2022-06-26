from typing import *
from lib import *

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


def algorithm1(pi, step=.1, setpoint=65, ):
    """works on accident"""
    fan_speed = .9
    yield fan_speed
    next(pi)
    yield fan_speed
    for temperature in pi:
        power = temperature * fan_speed
        fan_speed = power / setpoint
        yield clamp01(fan_speed)


def algorithm2(pi, step=.1, setpoint=65, multiplier=1.5):
    """requires tuning"""
    fan_speed = .9
    yield fan_speed
    next(pi)
    yield fan_speed
    for temperature in pi:
        power = (temperature - ROOM_TEMPERATURE) * fan_speed * multiplier
        fan_speed = power / setpoint
        yield clamp01(fan_speed)


def algorithm3(pi, step=.1, lerp_range=((20, 0), (65, 1))):
    """settles, i think"""
    fan_speed = .9
    yield fan_speed
    next(pi)
    yield fan_speed
    for temperature in pi:
        fan_speed = interpolate(temperature, lerp_range)
        yield fan_speed


def algorithm4(pi, step=.1, mintemp=20, maxtemp=65, curvature=.7):
    """also settles"""
    assert 0 < curvature
    fan_speed = .9
    yield fan_speed
    next(pi)
    yield fan_speed
    for temperature in pi:
        base = unlerp(mintemp, maxtemp, temperature)
        fan_speed = clamp01(base ** curvature)
        yield fan_speed

def algorithm5(pi, step=.1, single_speed=.5):
    yield single_speed
    for temperature in pi:
        yield single_speed

def run_sim(pi, algorithm, alg_args={}, steps=99999):
    temperature_list = []
    fan_speed_list = []
    my_pi = pi(iter(fan_speed_list))
    my_algorithm = algorithm(iter(temperature_list), **alg_args)
    for i in range(steps):
        next_temperature = next(my_pi)
        next_speed = next(my_algorithm)
        assert 0 <= next_speed <= 1
        temperature_list.append(next_temperature)
        fan_speed_list.append(next_speed)
        yield i, next_temperature, next_speed


def print_sim(pi, algorithm, alg_args={}, steps=99999):
    for i, next_temperature, next_speed in run_sim(pi, algorithm, alg_args=alg_args, steps=steps):
        print(f"{i: 9d} {next_temperature: 9.1f} {next_speed: 9.1f}")


def conclude_sim(pi, algorithm, alg_args={}, steps=99999):
    for i, next_temperature, next_speed in run_sim(pi, algorithm, alg_args=alg_args, steps=steps):
        pass
    # print(f"{i: 9d} {next_temperature: 9.1f} {next_speed: 9.1f}")
    print(f"{next_speed:f}\t{next_temperature:f}")

if __name__ == '__main__':
    n=100
    for i in range(0,n):
        conclude_sim(pi2, algorithm5, alg_args={"single_speed": i/n})
