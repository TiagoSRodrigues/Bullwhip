#Analise plots

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("MC_Simulation_comulative.csv")
df2 = pd.read_csv("MC_Simulation_all_data.csv")

# print(df)

# sns.displot(df, x="Time", hue="Test", kind="kde")
# sns.displot(df, x="Time", hue="Test", kind="kde", fill=False)


# g=sns.displot(
# data=df,
# x="Tempo",
# kind="kde", height=6,
# # multiple="fill", clip=(0, None),
# palette="ch:rot=-.25,hue=1,light=.75",
# )


#g=sns.scatterplot(data=df, x="Elemento", y="Tempo")


#g.set_axis_labels( "Tempo total (d)", "Densidade")
# sns.set_theme(style="whitegrid")

# Load the example diamonds dataset

# Draw a scatter plot while assigning point colors and sizes to different
# variables in the dataset
# sns.lineplot(x="Elemento", y="Tempo",
#              hue="Teste", 
#              data=df2)

# import seaborn as sns
# import matplotlib.pyplot as plt

# sns.set_theme(style="ticks")

# # Initialize the figure with a logarithmic x axis
# f, ax = plt.subplots(figsize=(7, 6))

# # Load the example planets dataset

# # Plot the orbital period with horizontal boxes
# sns.boxplot(x="Elemento", y="Tempo", data=df,
#             whis=[0, 100], width=.6, palette="vlag")

# # Add in points to show each observation
# sns.stripplot(x="Elemento", y="Tempo", data=df,
#               size=4, color=".3", linewidth=0)

# # Tweak the visual presentation
# ax.xaxis.grid(True)
# ax.set(ylabel="")
# sns.despine(trim=True, left=True)

# ax = sns.boxplot(data=df, x="Tempo", y="Elemento", orient="h", palette="pastel")

dfx=df.groupby("Elemento").describe()
print(dfx)

# dfy=pd.DataFrame(dfx["Tempo"])
# dfy["Elemento"]=["A","B","C","D"]



# g=sns.catplot(
#     data=df, kind="bar", 
#     x="Elemento",
#     y="Tempo",
#     ci="sd",
#     palette="dark", alpha=0.6, height=6
# )



ax = sns.swarmplot(data=df, y="Elemento", x="Tempo", size=1, )#, hue="species")
ax.xaxis.grid(True, color='gray', linestyle='-', linewidth=0.1) # Show the vertical gridlines
ax.set(ylabel="Elemento da cadeia", xlabel="Tempo até à recepção")
# ay.set(ylabel="")

plt.show()
