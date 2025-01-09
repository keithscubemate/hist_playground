from datetime import datetime
from random import random, seed
from power_set import PowerSet

def sim_anneal(iteration, max_iters, best_error, current_error):
    # weight temp the based on energy
    t_max = 2 * best_error
    t = t_max * (1 - (iteration / max_iters))

    energy = current_error - best_error

    p = (energy + t) / (best_error + t_max)
    r = random()

    return p >= r

def optimize(
        calculate_error,
        initial,
        step_size=1,
        search_width=1,
        max_iters=100,
        min_err=1e-6,
        min_step=1e-6
    ):
    # Initialize coefficients and other parameters
    params = initial
    best_error = float('inf')
    best_params = params

    # pregenerate our delta arrays
    steps = [i * step_size for i in range(-search_width, search_width + 1)]
    ps = PowerSet(len(params), len(steps))
    deltas = [
        (
            [steps[ps.set[idx]] for idx in range(len(params))],
            ps.inc()
        )[0]
        for _ in range(ps.total_iteration())
    ]
    
    # Optimization loop
    for iteration in range(max_iters):
        current_error = calculate_error(params)

        # Check if current error is the best we've seen
        if current_error < best_error:
            best_error = current_error
            best_params = params
        else:
            if sim_anneal(iteration, max_iters, best_error, current_error):
                best_error = current_error
                best_params = params
            step_size *= 0.95

        for delta in deltas:
            new_params = [params[i] + (delta[i] * step_size) for i in range(len(params))]

            new_error = calculate_error(new_params)
            
            # Update m and b if new error is better
            if new_error < current_error:
                params = new_params
                current_error = new_error

        if abs(step_size) < min_step or best_error < min_err:
            break
    
    return best_params
    
def test_basic_optimizer():
    f = lambda x: (x - 3.14) * (x - 1.5) * (x + 10.6897) * (x + 5)

    def err(arr):
        return sum((abs(f(x)) for x in arr))

    res = optimize(
        err,
        initial=[3, 1, -10, 5],
        step_size=0.1
    )

    print(err(res))
    [print(i, x,f(x)) for i, x in enumerate(res)]


if __name__ == '__main__':
    seed(datetime.now().timestamp())
    test_basic_optimizer()
