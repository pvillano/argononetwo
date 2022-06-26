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