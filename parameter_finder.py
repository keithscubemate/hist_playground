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

def double_finder(hist, desired_f, f, desired_g, g):
    def error_function(m, b):
        trans = hist.stretch_into(m).shift_into(b)

        error1 = (f(trans) - desired_f) / desired_f
        error2 = (g(trans) - desired_g) / desired_g

        return abs(error1) + abs(error2)


    return custom_optimizer(error_function)

def custom_optimizer(
        calculate_error,
        initial_a=1,
        initial_b=0,
        step_size=0.5,
        max_iters=100
    ):
    # Initialize coefficients and other parameters
    a, b = initial_a, initial_b
    best_error = float('inf')
    best_a, best_b = a, b
    
    # Optimization loop
    for iteration in range(max_iters):
        # Calculate error with current a and b
        current_error = calculate_error(a, b)
        
        # Check if current error is the best we've seen
        if current_error < best_error:
            best_error = current_error
            best_a, best_b = a, b
        else:
            # If no improvement, stop adjusting (or try smaller step size)
            step_size /= 2  # Reduce step size if error doesn't improve

        # Try adjusting 'a' and 'b' in both positive and negative directions
        for delta_a in [-step_size, step_size]:
            for delta_b in [-step_size, step_size]:
                # Calculate new potential values for a and b
                new_a, new_b = a + delta_a, b + delta_b
                new_error = calculate_error(new_a, new_b)
                
                # Update a and b if new error is better
                if new_error < current_error:
                    a, b = new_a, new_b
                    current_error = new_error

        # Optional: Stop if error is below a certain threshold
        if best_error < 1e-6:
            break

    print(step_size)
    print(best_error)
    print()
    
    return best_a, best_b
    

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
    return sum(v * (( i * w ) + (w / 2)) for i, v in enumerate(hist.hist)) / sum(v for v in hist.hist)

def percent_below_value(hist, val):
    return \
        sum(v for i, v in enumerate(hist.hist) if i * hist.bin_size < val) \
        / \
        sum(v for v in hist.hist)


if __name__ == '__main__':

    hist = make_test_hist_from_data()

    f = lambda h : weighted_mean_value(h, 1)
    g = lambda h : percent_below_value(h, 7)

    print("max(h)", len(hist.hist) * hist.bin_size)
    print("initial f(h):", f(hist))
    print("initial g(h):", g(hist))
    print()

    desired_f = 20
    desired_g = 0.20

    scale, offset = double_finder(hist, desired_f, f, desired_g, g)

    print("desired f:", desired_f)
    print("desired g:", desired_g)
    print()

    print("scale", scale)
    print("offset", offset)
    print()

    fs = hist.stretch_into(scale).shift_into(offset)

    print("modified f: ", f(fs))
    print("modified g: ", g(fs))
