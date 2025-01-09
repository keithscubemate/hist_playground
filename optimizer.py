from random import random, seed
from power_set import PowerSet

def sim_anneal(iteration, max_iters):
    # weight temp the based on energy
    t_max = 2 * best_error
    t = t_max * (1 - (iteration / max_iters))

    energy = current_error - best_error

    p = (energy + t) / (best_error + t_max)
    r = random()

    return p >= r

def custom_optimizer(
        calculate_error,
        initial,
        step_size=1,
        search_width=1,
        max_iters=100
    ):
    # Initialize coefficients and other parameters
    params = initial
    best_error = float('inf')
    best_params = params

    # pregenerate our delta arrays
    steps = [i * step_size for i in range(-search_width, search_width + 1)][::-1]
    ps = PowerSet(2, len(steps))
    deltas = [
        (
            [steps[ps.set[idx]] for idx in range(len(params))],
            ps.inc()
        )[0]
        for _ in range(ps.total_iteration())
    ]
    
    # Optimization loop
    for iteration in range(max_iters):
        # Calculate error with current m and b
        current_error = calculate_error(params)

        print(iteration)
        print(params, best_error, step_size)
        
        # Check if current error is the best we've seen
        if current_error < best_error or sim_anneal(iteration, max_iters):
            best_error = current_error
            best_params = params

            if current_error >= best_error:
                step_size *= 0.95

        for delta in deltas:


            new_params = [params[i] + delta[i] for i in range(len(params))]

            new_error = calculate_error(new_params)
            
            # Update m and b if new error is better
            if new_error < current_error:
                params = new_params
                current_error = new_error

        if abs(step_size) < 1e-6 or best_error < 1e-6:
            break
    
    return best_params
    
def test_basic_optimizer():
    f = lambda x: (x - 3) * (x - 1)

    def err(arr):
        x0 = arr[0]
        x1 = arr[1]
        y0 = f(x0)
        y1 = f(x1)

        return abs(y0) + abs(y1)

    res = custom_optimizer(
        err,
        initial=[0, 10],
        step_size=0.5,
        max_iters=1000
    )
    x = res[0]
    y = res[1]

    print()
    print(res)
    print(x, y)
    print(f(x))
    print(f(y))


if __name__ == '__main__':
    test_basic_optimizer()
