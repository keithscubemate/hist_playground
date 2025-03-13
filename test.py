from data import data
from histogram import Histogram, bytes_to_arr 
import base64


h1 = data[1]["TrashHistogram"]

h1 = base64.b64decode(h1)

a_int = bytes_to_arr(h1, 4)
h1 = Histogram.from_array(a_int, 45)


h1.print()
