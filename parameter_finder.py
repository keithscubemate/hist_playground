from random import random, seed
import time

from histogram import Histogram

if __name__ == '__main__':

    current_time_seconds = time.time()
    seed(current_time_seconds)

    m = []
    for i in range(100):
        for j in range(int(1000 * random())):
            m.append(i + (1 * random()))

    print(sum(v for v in m) / len(m), "<--- true mean")

    hist = Histogram.from_measurements(m)

    print(hist.mean(), "<--- original mean")

    scale = 0.5
    offset = 10

    
    rs = Histogram.from_measurements([(scale * v) + offset for v in m])
    print(rs.mean(), "<--- true scaling mean")

    fs = hist.stretch_into(scale).shift_into(offset)
    print(fs.mean())




