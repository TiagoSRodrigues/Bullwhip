import numpy as np
def empty_fill(n):
    a = np.empty(n, dtype=np.int64)
    a.fill(1)
    return a

print(empty_fill(10))


print(np.ones(4))