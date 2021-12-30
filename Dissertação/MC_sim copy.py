import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#mu, sigma = 0, 0.1
#s = abs(np.random.normal(mu, sigma, 1))

iterations=100000
sc=["a","b","c","d"]


df_all_data = pd.DataFrame(columns=['Elemento','Tempo'])

def get_rand_time(element, calls):
    time=0
    for i in range(calls+1):
        time += np.round(abs(np.random.normal(5, 0.5, 1))[0],3,None)
    return time


    global df_all_data
    df_all_data = df_all_data.append(
        {"Elemento":str(element),
        "Tempo": str(time)},ignore_index=True)
    return time

def get_sc_time():
    for el in sc:
        index = sc.index(el)
        time=get_rand_time( el, index)
        global df_all_data
        df_all_data = df_all_data.append(
            {"Elemento":str(el),
            "Tempo": str(time)},ignore_index=True)
    return time


for i in range(iterations):
    get_sc_time()

df_all_data.to_csv("MC_Simulation_comulative.csv", index=False)

# print(df)
# sns.displot(df, x="value", hue="test", kind="kde", fill=True)


# plt.show()