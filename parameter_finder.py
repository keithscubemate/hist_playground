import base64
import time
from random import random, seed

from histogram import Histogram, bytes_to_arr

def finder(hist, desired, f):
    actual = f(hist)

    scale = desired / actual

    for i in range(10):
        new_hist = hist.stretch_into(scale)
        new_actual = f(new_hist)
        scale += 1 - (desired / new_actual)
        print(scale,desired, new_actual)

    print()
    return scale

def thing(hist, w = 1):
    return sum(v * (( i * w ) + (w / 2)) for i, v in enumerate(hist.hist)) / sum(v for v in hist.hist)


def make_test_hist():
    s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

    a = base64.b64decode(s)

    a_int = bytes_to_arr(a, 4) 

    return Histogram.from_array(a_int)


if __name__ == '__main__':

    # current_time_seconds = time.time()
    seed(0)

    hist = make_test_hist()

    # hist.print(100_000_000)
    # print()

    f = lambda h : thing(h, 2)

    print("initial:", f(hist))
    print()

    desired = 20
    scale = finder(hist, desired, f)

    print("desired:", desired)

    print("scaled: ", f(hist.stretch_into(scale)))

    # print("actual: ", f(Histogram.from_measurements([v * scale for v in m])))
