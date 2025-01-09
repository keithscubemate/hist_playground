from random import random, seed
from power_set import PowerSet

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
        ps = PowerSet(2, len(steps))

        for _ in range(ps.total_iteration()):
            delta_m = steps[ps.set[0]]
            delta_b = steps[ps.set[1]]
            ps.inc()

            if delta_m == delta_b == 0:
                continue
            # Calculate new potential values for m and b
            new_m, new_b = m + delta_m, b + delta_b

            new_error = calculate_error(new_m, new_b)
            
            # Update m and b if new error is better
            if new_error < current_error:
                m, b = new_m, new_b
                current_error = new_error

        if abs(step_size) < 1e-6 or best_error < 1e-6:
            break
    
    return best_m, best_b
    
def test_basic_optimizer():
    f = lambda x: (x - 3) * (x - 1)

    def err(x0, x1):

        y0 = f(x0)
        y1 = f(x1)

        return abs(y0) + abs(y1)

    x, y = custom_optimizer(
        err,
        initial_m=0,
        initial_b=10,
        step_size=0.5,
        max_iters=1000
    )

    print()
    print(x, y)
    print(f(x))
    print(f(y))


if __name__ == '__main__':
    test_basic_optimizer()
