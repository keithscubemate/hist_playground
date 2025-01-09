class PowerSet:
    def __init__(self, n, base):
        self.n = n
        self.base = base

        self.set = [0] * n

    def to_int(self):
        current_base = 1
        total = 0
        for place in self.set:
            total += place * current_base
            current_base *= self.base

        return total


    def inc(self):
        i = 0
        self.set[0] += 1

        while self.set[i] >= self.base:
            self.set[i] = 0

            i += 1
            if i >= self.n:
                self.set = [0] * self.n
                i = 0

            self.set[i] += 1

    def total_iteration(self):
        return self.base ** self.n


if __name__ == '__main__':
    ps = PowerSet(2, 5)
    ps1 = PowerSet(5, 2)

    for _ in range(ps.total_iteration()):
        print(ps.set, ps.to_int(), '---', ps1.set, ps1.to_int())
        ps.inc()
        ps1.inc()
