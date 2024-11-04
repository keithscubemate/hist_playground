import base64
from random import random 
   
def bytes_to_arr(arr, so):
    return [int.from_bytes((j:=i*so, arr[j:j+so])[1]) for i in range(len(arr)//so)]

class Histogram:
    def __init__(self, bin_size):
        '''
        Init a histogram with a given bin size
        '''
        self.bin_size = bin_size
        self.hist = []

    @classmethod
    def from_measurements(cls, measurements, bin_size = 1):
        hist = Histogram(bin_size)

        hist.hist = [0] * (int(max(measurements) / bin_size) + 1)

        for v in measurements:
            hist.hist[int(v / bin_size)] += 1

        return hist

    @classmethod
    def from_array(cls, arr, bin_size = 1):
        hist = Histogram(bin_size)
        hist.hist = arr

        return hist

    def mean(self):
        h = self.hist
        return sum(i * v  * self.bin_size for i, v in enumerate(h)) / sum([v for v in h])

    def mutate(self, scale, offset):
        self.stretch(scale)
        self.shift(offset)

    def stretch_into(self, scale):
        new_h = [0] * (int(len(self.hist) * scale) + 1)
        new_h_idx = 0

        for i, val in enumerate(self.hist):
            new_h_idx = i * scale
            dist = self.__calc_distribution_array(new_h_idx, scale)

            j = int(new_h_idx)

            for k, weight in enumerate(dist):
                new_h[j+k] = self.hist[i] * weight

        return Histogram.from_array(new_h, self.bin_size)

    def stretch(self, scale):
        self.hist = self.stretch_into(scale).hist

    def shift_into(self, offset):
        new_h = [0] * (len(self.hist) + int(offset) + 1)

        for i, val in enumerate(self.hist):
            new_h[i + int(offset)] = val

        return Histogram.from_array(new_h, self.bin_size)

    def shift(self, offset):
        self.hist = self.shift_into(offset).hist

    def print(self, shrink = 1):
        for i in self.hist:
            exes = ["x" for _ in range(int(i)//shrink)]
            print("|", "".join(exes)) 

    def __calc_distribution_array(self, start, k):
        end = start + k
        curr = start

        rv = []

        complement = 1 - (start - int(start))

        if complement > 0:
            rv.append(complement)
            curr += complement

        while curr < end:
            val = 1 if end - curr > 1 else end - curr
            rv.append(val)
            curr += val

        return [v / k for v in rv]

if __name__ == '__main__':
    s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

    a = base64.b64decode(s)

    a_int = bytes_to_arr(a, 4) 

    hist = Histogram.from_array(a_int)

    hm = hist.mean()

    print(hm)
    print()

    # Test shifting on a range
    for i in range(1, 10):
        h1 = hist.shift_into(i)
        h1m = h1.mean()
        print(i, h1m, h1m-hm)

    print()

    prev = 0
    prev2 = 0
    # Test stretching on a range
    for i in range(1, 10):
        h1 = hist.stretch_into(i)
        h1m = h1.mean()
        print(i, h1m, h1m/hm)

    print()

    # Check that the scaling and stretching is accurate to reality
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

