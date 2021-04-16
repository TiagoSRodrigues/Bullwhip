#%%
import time
start_time = time.time()
import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt 

#sns.set_style('whitegrid')

casos=1000000

with open('MonteCarloConfiguration.json') as json_file:
    json_config = json.load(json_file)

actors=json_config.keys


##gets the stats of an actor
def get_Stats(letter):  
    mean=json_config["actors"][letter]["mean"]
    std=json_config["actors"][letter]["std"]
    distro=json_config["actors"][letter]["distribution"]
    return float(mean), float(std), distro

#gets the random time of a actor regarding normal distribution
def get_Step_Time(letter):  
    mean,std,distro=get_Stats(letter)
    return np.random.normal(mean, std, 1).round(3)


def route_time():
    total_time=0
    for actor in json_config["actors"]:
        step_time=get_Step_Time(actor)
        total_time=total_time+step_time
    return total_time

def run_simulation(casos):
    serie_tempos=pd.Series([])
    for i in range(0,casos,1):
        serie_route_time=pd.Series(route_time())
        serie_tempos=serie_tempos.append(serie_route_time)    

    return serie_tempos

serie_tempos=run_simulation(casos)
print(serie_tempos.describe())

sns.histplot(data=serie_tempos)
print("--- %s seconds ---" % (time.time() - start_time))

# %%
