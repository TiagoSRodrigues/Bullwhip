import math

from pandas.io.formats.format import return_docstring


import math

def better_round(value):
    if value%1 *10 < 5:
        return math.floor(value)
    return math.ceil(value)

print("better_round ", better_round(12.5))
print("better_round ", better_round(12.4))
print("ceil ",math.ceil(12.5) )
print("ceil ",math.ceil(12.4) )