#Analise plots

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("MC_Simulation.csv")

# print(df)

# sns.displot(df, x="Time", hue="Test", kind="kde")
# sns.displot(df, x="Time", hue="Test", kind="kde", fill=False)


sns.displot(
    data=df,
    x="Time", hue="Test",
    kind="kde", height=6,
   # multiple="fill", clip=(0, None),
    palette="ch:rot=-.25,hue=1,light=.75",
)

plt.show()
