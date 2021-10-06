import numpy as np
#mu, sigma = 0, 0.1
#s = abs(np.random.normal(mu, sigma, 1))

stats={
 "a":(5,0.5),
 "b":(5,0.5),
 "c":(5,0.5),
 "d":(5,0.5)
 }

stats_2={
 "a":(5,0.0001),
 "b":(5,0.5),
 "c":(5,0.5),
 "d":(5,0.5)
 }
sc=["a","b","c","d"]

def get_time(element):
    x, s = stats_2[element]
    return abs(np.random.normal(x, s, 1))

def get_sc_time():
    time=0
    for el in sc:
        time+=get_time(el)
    
    return time

results=np.array([])
for i in range(10000):
    results=np.append(results,get_sc_time())

# print(np.mean(results),
#       np.var(results))


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.violinplot(x='sex', data=results)
