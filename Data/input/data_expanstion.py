from email import header
from statistics import harmonic_mean
import sys
import numpy as np
import scipy as sp
import scipy.interpolate
from scipy import stats

from pandas import read_csv
import pandas as pd
import matplotlib.pyplot  as plt

def save_to_csv(data, filename):
    data.to_csv(sys.path[0]+"\\"+filename, index= False , header=False)

#origianl data
# source: https://fred.stlouisfed.org/series/S4248SM144NCEN#  Merchant Wholesalers, Except Manufacturers' Sales Branches and Offices: Nondurable Goods: Beer, Wine, and Distilled Alcoholic Beverages Sale
#

file = sys.path[0]+'\\S4248SM144NCEN.csv'
dataframe = read_csv(file)
data = dataframe.values

#extract the y data
y = data[:, 1]

#define the x axis 
x = np.arange(len(data))

# multiplication factor to increase data
interpolation_factor = 10

# Interpolate the data using a cubic spline to "new_length" samples
new_length = len(y)*interpolation_factor
new_x = np.linspace(x.min(), x.max(), new_length)
new_y = sp.interpolate.interp1d(x, y, kind='nearest-up')(new_x)

# Plot the results
plt.figure()
plt.subplot(2,1,1)
plt.plot(x, y, 'bo-', ms=2)
plt.title('Using 1D Cubic Spline Interpolation')

plt.subplot(2,1,2)
plt.plot(new_x, new_y, 'ro-', ms=2)

# plt.show()
df_y_inicial = pd.DataFrame(y, dtype= float)
df_y_final = pd.DataFrame(new_y)

# print("\ninicial",df_y_inicial.describe().round())
# print("\nfinal",df_y_final.describe().round())


def compare_dataframes(df1,df2):
    
    initial_data = df1.describe()
    final_data = df2.describe()
    
    diference = ((final_data - initial_data) / initial_data )*100
    
    #harmonic_mean 
    h1 = stats.hmean(df1)
    h2 = stats.hmean(df2)
    
    h_diff = ((h2-h1 ) / h1 ) *100
    
    
    print(
        "Data Variation (%)  \n",
        round(diference,2),
        "\nharmonic mean: {}".format(round(float(h_diff), 2))
    )
compare_dataframes(df1=df_y_inicial, df2=df_y_final)
    
save_to_csv(df_y_final, "real_data_interpolated.csv" )


