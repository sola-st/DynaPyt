import numpy as np
a = []
a.append((6*60 + 59, 2188, 176173))
a.append((14*60 + 7, 3603, 318602))
a.append((5*60 + 41, 678, 155407))
a.append((12*60 + 32, 2727, 358195))
a.append((16, 54, 6370))
a.append((57, 178, 24362))
a.append((6*60 + 52, 1419, 180185))
a.append((60 + 49, 505, 37181))
a.append((60 + 21, 620, 12070))

d = [x[0] for x in a]
f = [x[1] for x in a]
l = [x[2] for x in a]
print(d)
print(f)
print(l)
print(np.corrcoef(d, f))
print(np.corrcoef(d, l))