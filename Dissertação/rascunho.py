from pydoc import describe
from statistics import quantiles
import pandas as pd
import numpy as np

dados  = pd.read_csv("N:\TESE\Bullwhip\Dissertação\MC_Simulation_comulative.csv")
df=dados[["Elemento", "Tempo"]]

table= pd.pivot_table(df, values="Tempo",  index=['Elemento'], aggfunc= [min, max, np.mean, np.std, quantiles])

print(table)