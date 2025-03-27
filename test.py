from data import data
from histogram import Histogram, bytes_to_arr
import base64


val1 = data[0]["sa"][0]["Fineness"]
h1 = data[0]["sa"][0]["FinenessHistogram"]

h1 = base64.b64decode(h1)

a_int = bytes_to_arr(h1, 4)
h1 = Histogram.from_array(a_int, 25)



print(val1)
print(h1.mean())
