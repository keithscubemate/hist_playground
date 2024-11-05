import base64
import time
from random import random, seed
from pprint import pprint
from scipy import optimize

from histogram import Histogram, bytes_to_arr

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

def double_finder_scipy(hist, desired_f, f, desired_g, g):
    def error_function(m, b):
        m = float(m)
        b = float(b)
        trans = hist.stretch_into(m).shift_into(b)

        error1 = (f(trans) - desired_f) / desired_f
        error2 = (g(trans) - desired_g) / desired_g

        return abs(error1) + abs(error2)

    init_m=f(hist) / desired_f
    init_b=(g(hist) - desired_g) * init_m

    result = optimize.minimize(
            lambda params: error_function(params[0], params[1]),
            x0=[init_m, init_b],
            method='nelder-mead',
            bounds=[(1e-6, None), (None,None)]
    )

    return result.x

def double_finder(hist, desired_f, f, desired_g, g):
    orig_count = sum(v for v in hist.hist)
    def error_function(m, b):
        trans_stretch = hist.stretch_into(m)
        trans = trans_stretch.shift_into(b)

        stretch_count = sum(v for v in trans_stretch.hist)
        trans_count = sum(v for v in trans.hist)

        error1 = 3 * abs((f(trans) - desired_f) / desired_f)
        error2 = abs((g(trans) - desired_g) / desired_g)

        lost_data = 10 * ((orig_count - trans_count) / orig_count)

        if lost_data < 0: 
            lost_data = 0

        return error1 + error2 + lost_data

    init_m=f(hist) / desired_f
    init_b=(g(hist) - desired_g) * init_m

    return custom_optimizer(
        error_function,
        initial_m=init_m,
        initial_b=init_b,
        step_size=5,
        search_width=20,
        max_iters=300
    )

def custom_optimizer(
        calculate_error,
        initial_m=1,
        initial_b=0,
        step_size=1,
        search_width=1,
        max_iters=100
    ):
    # Initialize coefficients and other parameters
    m, b = initial_m, initial_b
    best_error = float('inf')
    best_m, best_b = m, b
    
    # Optimization loop
    for iteration in range(max_iters):
        # Calculate error with current m and b
        current_error = calculate_error(m, b)

        print(iteration)
        print(best_m, best_b, best_error, step_size)
        
        # Check if current error is the best we've seen
        if current_error < best_error:
            best_error = current_error
            best_m, best_b = m, b
        else:
            # weight temp the based on energy
            t_max = 2 * best_error
            t = t_max * (1 - (iteration / max_iters))

            energy = current_error - best_error

            p = (energy + t) / (best_error + t_max)
            r = random()

            print(">", p, r)
            print()

            if p >= r:
                best_error = current_error
                best_m, best_b = m, b

            step_size *= 0.95

        # Try adjusting 'm' and 'b' in both positive and negative directions
        steps = [i * step_size for i in range(-search_width, search_width + 1)][::-1]
        for delta_b in steps:
            for delta_m in steps:
                if delta_m == delta_b == 0:
                    continue
                # Calculate new potential values for m and b
                new_m, new_b = m + delta_m, b + delta_b

                if new_m <= 0:
                    continue

                new_error = calculate_error(new_m, new_b)
                
                # Update m and b if new error is better
                if new_error < current_error:
                    m, b = new_m, new_b
                    current_error = new_error

        # Optional: Stop if error is below m certain threshold
        if best_error < 1e-6:
            break
    
    return best_m, best_b
    

def make_test_hist_from_data():
    s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

    a = base64.b64decode(s)

    a_int = bytes_to_arr(a, 4) 

    return Histogram.from_array(a_int)

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
    current_time_seconds = 0 # time.time()
    seed(current_time_seconds)

    hist = make_test_hist_from_data()
    desired = 59

    f = lambda h : weighted_mean_value(h, 1)

    print("initial:", f(hist))
    print()

    scale = single_finder_stretch(hist, desired, f)

    print("desired:", desired)
    print("scaled: ", f(hist.stretch_into(scale)))

def weighted_mean_value(hist, w = 1):
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

    hist = make_test_hist_from_data()

    f = lambda h : weighted_mean_value(h, 2)
    g = lambda h : percent_below_value(h, 12)

    datum = {}

    desired_f = 30
    desired_g = 0.14

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

