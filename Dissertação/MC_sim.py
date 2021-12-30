import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#mu, sigma = 0, 0.1
#s = abs(np.random.normal(mu, sigma, 1))

iterations=10000
sc=["a","b","c","d"]
tests_dict = {
"A":{
 "a":(5,0.5),
 "b":(5,0.5),
 "c":(5,0.5),
 "d":(5,0.5)
#  }
# ,
# "B":{
#  "a":(5,0),
#  "b":(5,0.5),
#  "c":(5,0.5),
#  "d":(5,0.5)
#  },
# "C":{
#  "a":(5,0.5),
#  "b":(5,0.5),
#  "c":(5,0),
#  "d":(5,0.5)
#  },
# "D":{
#  "a":(5,0.5),
#  "b":(5,0.45),
#  "c":(5,0.405),
#  "d":(5,0.3645)
#  },
# "E":{
#  "a":(5,0.45),
#  "b":(5,0.45),
#  "c":(5,0.45),
#  "d":(5,0.45)
#  },
# "F":{
#  "a":(5,0),
#  "b":(5,0.1),
#  "c":(5,0.2),
#  "d":(5,0.3)
 }
}
sc=["a","b","c","d"]
tests_list=[*tests_dict]

df = pd.DataFrame(columns=['Tempo','Teste',])
df_all_data = pd.DataFrame(columns=['Teste','Elemento','Tempo'])

def get_time(test,  element):
    x, s = tests_dict[test][element]
    time = np.round(abs(np.random.normal(x, s, 1))[0],3,None)
    global df_all_data
    df_all_data = df_all_data.append(
        {'Teste': str(test),
        "Elemento":str(element),
        "Tempo": str(time)},ignore_index=True)
    return time

def get_sc_time(test):
    time=0
    for el in sc:
        time+=get_time(test, el)
    return time

for test in tests_list:
    for i in range(iterations):
        df = df.append({'Tempo':
        str(get_sc_time(test)), "Teste":str(test)}, ignore_index=True)

df.to_csv("MC_Simulation.csv", index=False)
df_all_data.to_csv("MC_Simulation_all_data.csv", index=False)

# print(df)
# sns.displot(df, x="value", hue="test", kind="kde", fill=True)


# plt.show()