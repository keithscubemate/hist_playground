import base64
import time
from random import random, seed
from pprint import pprint

from histogram import Histogram, bytes_to_arr
from optimizer import optimize

def single_finder_shift(hist, desired, f):
    actual = f(hist)
    shift = int(desired - actual)

    return shift

def single_finder_stretch(hist, desired, f):
    actual = f(hist)

    orig_count = sum(v for v in hist.hist)
    scale = (desired / actual)

    def error_function(arr):
        m = arr[0]

        if m < 0:
            return float('inf')

        trans = hist.stretch_into(m)

        trans.hist = trans.hist[:32]

        trans_count = sum(v for v in trans.hist)

        error1 = abs((f(trans) - desired) / desired)

        lost_data = abs((orig_count - trans_count) / orig_count)

        return error1 + lost_data

    return optimize(
        error_function,
        [scale]
    )

def double_finder(hist, desired_f, f, desired_g, g):

    orig_count = sum(v for v in hist.hist)

    def error_function(arr):
        m = arr[0]
        b = arr[1]
        if m < 0:
            return float('inf')

        trans = hist.stretch_into(m).shift_into(b)

        trans.hist = trans.hist[:32]

        trans_count = sum(v for v in trans.hist)

        error1 = abs((f(trans) - desired_f) / desired_f)
        error2 = abs((g(trans) - desired_g) / desired_g)

        lost_data = abs((orig_count - trans_count) / orig_count)

        return error1 + error2 + lost_data

    init_m=f(hist) / desired_f
    init_b=(g(hist) - desired_g) * init_m

    return optimize(
        error_function,
        [init_m, init_b]
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

def test_double_parameter():
    current_time_seconds = time.time()
    seed(current_time_seconds)

    hist = make_test_hist_from_data()

    f = lambda h : weighted_mean_value(h)
    g = lambda h : percent_below_value(h, 12.5)

    datum = {}

    desired_f = 32
    desired_g = 0.18

    scale, offset = double_finder(hist, desired_f, f, desired_g, g)

    datum["desired f:"] = desired_f
    datum["desired g:"] = desired_g

    datum["scale"] = scale
    datum["offset"] = offset

    fs = hist.stretch_into(scale).shift_into(offset)
    fs.hist = fs.hist[:32]

    datum["modified f: "] = f(fs)
    datum["modified g: "] = g(fs)

    print()

    print("max(h)", len(hist.hist) * hist.bin_size)
    print("initial f(h):", f(hist))
    print("initial g(h):", g(hist))

    print()

    pprint(datum)

def test_single_parameter():

    hist = make_test_hist_from_data()
    desired = 32

    f = lambda h : weighted_mean_value(h)

    print("max(h)", len(hist.hist) * hist.bin_size)
    print("initial:", f(hist))
    print()

    scale = single_finder_stretch(hist, desired, f)[0]

    fs = hist.stretch_into(scale)
    fs.hist = fs.hist[:32]

    print("desired:", desired)
    print("scaled: ", f(fs))

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
    print("# Single:")
    test_single_parameter()
    print()
    print("# Double:")
    test_double_parameter()
