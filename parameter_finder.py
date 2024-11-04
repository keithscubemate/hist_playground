import base64
import time
from random import random, seed
from pprint import pprint

from histogram import Histogram, bytes_to_arr

def finder(hist, desired, f):
    actual = f(hist)

    scale = (desired / actual)
    guesses = []

    i = 0
    new_actual = 0
    for i in range(10):
        new_hist = hist.stretch_into(scale)
        new_actual = f(new_hist)

        if abs(desired - new_actual) < 0.1:
            break

        guesses.append((scale, desired - new_actual))

        h = None
        if len(hs := [g for g in guesses if g[1] > 0]) > 0:
            h = min(hs, key=lambda g: g[1])

        l = None
        if len(ls := [g for g in guesses if g[1] < 0]) > 0:
            l = max(ls, key=lambda g: g[1])

        if h is None or l is None:
            scale += (desired / new_actual) - 1
        else:
            print(h, l)
            h = h[0]
            l = l[0]

            scale = (h + l) / 2

            if scale in [g[0] for g in guesses]:
                n_h = hist.stretch_into(scale)
                n_a = f(new_hist)

                if desired - n_a > 0:
                    scale = (l + scale) / 2
                    print("go low")
                else:
                    scale = (h + scale) / 2
                    print("go high")

        print(scale,desired, new_actual)
        print()

    print(i, scale, actual, new_actual)

    # for g in guesses:
    #     print(g)
    # print()

    return scale

def thing(hist, w = 1):
    return sum(v * (( i * w ) + (w / 2)) for i, v in enumerate(hist.hist)) / sum(v for v in hist.hist)


def make_test_hist_from_data():
    s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

    a = base64.b64decode(s)

    a_int = bytes_to_arr(a, 4) 

    return Histogram.from_array(a_int)

def make_test_hist_random(n, max_val):
    # Check that the scaling and stretching is accurate to reality
    m = []
    for i in range(n):
        for j in range(int(max_val * random())):
            m.append(i + (1 * random()))

    return Histogram.from_measurements(m), m


if __name__ == '__main__':

    # current_time_seconds = time.time()
    seed(0)

    # hist, m = make_test_hist_random(100, 1_000)
    hist = make_test_hist_from_data()

    # hist.print(100_000_000)
    # print()

    f = lambda h : thing(h, 1)

    print("initial:", f(hist))
    print()

    desired = 59

    scale = finder(hist, desired, f)

    print("desired:", desired)

    print("scaled: ", f(hist.stretch_into(scale)))

    # print("actual: ", f(Histogram.from_measurements([v * scale for v in m])))
