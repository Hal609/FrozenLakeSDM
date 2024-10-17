import numpy as np

bad_spots = ((1,1), (2, 1))
pos = (0, 1)

b = [[True, False], [False, False]]
a = [[False], [True]]
print(np.any(b, where=a))

print(pos)
print(bad_spots)
print(pos in bad_spots)