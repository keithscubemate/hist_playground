import base64
import time
from random import random, seed
from pprint import pprint

from histogram import Histogram, bytes_to_arr
from optimizer import custom_optimizer

def single_finder_shift(hist, desired, f):
    actual = f(hist)
    shift = int(desired - actual)

    return shift

def single_finder_stretch(hist, desired, f):
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
            # print(h, l)
            h = h[0]
            l = l[0]

            scale = (h + l) / 2

            if scale in [g[0] for g in guesses]:
                n_h = hist.stretch_into(scale)
                n_a = f(new_hist)

                if desired - n_a > 0:
                    scale = (l + scale) / 2
                    # print("go low")
                else:
                    scale = (h + scale) / 2
                    # print("go high")

        # print(scale,desired, new_actual)
        # print()

    # print(i, scale, actual, new_actual)

    # for g in guesses:
    #     print(g)
    # print()

    return scale

def double_finder(hist, desired_f, f, desired_g, g):

    orig_count = sum(v for v in hist.hist)

    def error_function(m, b):
        trans = hist.stretch_into(m).shift_into(b)

        trans.hist = trans.hist[:32]

        trans_count = sum(v for v in trans.hist)

        error1 = 5 * abs((f(trans) - desired_f) / desired_f)
        error2 = 5 * abs((g(trans) - desired_g) / desired_g)

        lost_data = abs((orig_count - trans_count) / orig_count)

        return error1 + error2 + lost_data + abs(m / 100) + abs(b / 100)

    init_m=f(hist) / desired_f
    init_b=(g(hist) - desired_g) * init_m

    return custom_optimizer(
        error_function,
        initial_m=init_m,
        initial_b=init_b,
        step_size=2,
        search_width=10,
        max_iters=200
    )

def make_test_hist_from_data():
    s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

    a = base64.b64decode(s)

    a_int = bytes_to_arr(a, 4) 

    return Histogram.from_array(a_int, 2)

def make_test_hist_random(n, max_count, desired_mean = None):
    if desired_mean is None:
        desired_mean = n / 2

    m = []
    for i in range(n):
        weight = 1 - ((abs(desired_mean - i)) / desired_mean)
        for j in range(int(max_count * (0.5 + 0.5 * random()) * weight)):
            m.append(i + (1 * random()))

    return Histogram.from_measurements(m), m

def test_single_parameter():

    hist = make_test_hist_from_data()
    desired = 59

    f = lambda h : weighted_mean_value(h)

    print("initial:", f(hist))
    print()

    scale = single_finder_stretch(hist, desired, f)

    print("desired:", desired)
    print("scaled: ", f(hist.stretch_into(scale)))

def test_double_parameter():
    current_time_seconds = time.time()
    seed(current_time_seconds)

    hist = make_test_hist_from_data()

    f = lambda h : weighted_mean_value(h)
    g = lambda h : percent_below_value(h, 12.5)

    datum = {}

    desired_f = 33
    desired_g = 0.18

    scale, offset = double_finder(hist, desired_f, f, desired_g, g)

    datum["desired f:"] = desired_f
    datum["desired g:"] = desired_g

    datum["scale"] = scale
    datum["offset"] = offset

    fs = hist.stretch_into(scale).shift_into(offset)

    datum["modified f: "] = f(fs)
    datum["modified g: "] = g(fs)

    print()

    hist.print(100_000_000)

    print()

    fs.print(100_000_000)

    print()

    print("max(h)", len(hist.hist) * hist.bin_size)
    print("initial f(h):", f(hist))
    print("initial g(h):", g(hist))

    print()

    pprint(datum)

def weighted_mean_value(hist):
    w = hist.bin_size
    weighted_sum = sum(v * (( i * w ) + (w / 2)) for i, v in enumerate(hist.hist))
    total = sum(v for v in hist.hist)

    if total == 0:
        return 0

    return weighted_sum / total 

def percent_below_value(hist, val):
    below_count = sum(v for i, v in enumerate(hist.hist) if i * hist.bin_size < val)
    total = sum(v for v in hist.hist)

    if total == 0:
        return 0

    return below_count / total

if __name__ == '__main__':
    # test_single_parameter()
    test_double_parameter()
