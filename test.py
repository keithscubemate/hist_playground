import base64
from random import random 
   
def bytes_to_arr(arr, so):
    return [int.from_bytes((j:=i*so, a[j:j+so])[1]) for i in range(len(arr)//so)]

def hist_print(h, shrink = 1):
    for i in h:
        exes = ["x" for _ in range(int(i)//shrink)]
        print("|", "".join(exes)) 

def hist_mean(h,bin_size = 1):
    return sum(i * v  * bin_size for i, v in enumerate(h)) / sum([v for v in h])

def hist_stretch(h, scal):
    new_h = [0] * (int(len(h) * scal) + 1)
    new_h_idx = 0

    for i, val in enumerate(h):
        dist = calc_distribution_array(new_h_idx, scal)

        j = int(new_h_idx)

        for k, weight in enumerate(dist):
            new_h[j+k] = h[i] * weight

        new_h_idx += scal

    return new_h

def hist_shift(h, b):
    new_h = [0] * (len(h) + b)

    for i, val in enumerate(h):
        new_h[i + b] = val

    return new_h

def calc_distribution_array(start, k):
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

s = "AAAAAAAAAAAMAAAAYgAAAKEAAACYAAAAhQAAAHoAAACPAAAAeAAAAGcAAABrAAAAcwAAAGoAAABLAAAAXwAAAEQAAABPAAAAXgAAAEsAAABRAAAARQAAAEgAAABPAAAAUQAAAEEAAABIAAAARwAAAEMAAABHAAAANgAAADUAAAA="

a = base64.b64decode(s)

h = bytes_to_arr(a, 4) 

hm = hist_mean(h)

print(hm)
print()

for i in range(1, 10):
    h1 = hist_shift(h, i)
    h1m = hist_mean(h1)
    print(i, h1m, h1m-hm)

print()

for i in range(1, 10):
    i = 4 - (i / 5)
    h1 = hist_stretch(h, i)
    h1m = hist_mean(h1)
    print(i, h1m, h1m/hm)

print()

m = []

for i in range(100):
    for j in range(int(1000 * random())):
        m.append(i + (1 * random()))

print(sum(v for v in m) / len(m))

h = [0] * (int(max(m)) + 1)

for v in m:
    h[int(v)] += 1

print(hist_mean(h))#,h)

scale = 0.5
offset = 10

fs = hist_stretch(h, scale)
fs = hist_shift(fs, offset)
print(hist_mean(fs))#,fs)

h = [0] * (int(max(m)) + 1)

rs = [0] * len(fs)
for v in m:
    v = (scale * v) + offset

    rs[int(v)] += 10

print(hist_mean(rs))#, rs)
