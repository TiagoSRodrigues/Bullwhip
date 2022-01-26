import pandas as pd
# from pandas import read_csv
import datetime
from matplotlib import pyplot
import os
import math
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt

data_file='N:\\TESE\\Bullwhip\\data\\input\\data_amplified.csv'

#https://www.statsmodels.org/dev/generated/statsmodels.tsa.arima.model.ARIMA.html


series = pd.read_csv(data_file)
# series.plot()



#autocorrelation_plot(series)

# series.index = series.index.to_period('M')

# # fit model
# model = ARIMA(series, order=(5,1,0))
# model_fit = model.fit()
# # summary of fit model
# print(model_fit.summary())
# # line plot of residuals
# residuals = pd.DataFrame(model_fit.resid)
# residuals.plot()
# pyplot.show()
# # density plot of residuals
# residuals.plot(kind='kde')
# pyplot.show()
# # summary stats of residuals
# print(residuals.describe())
# pyplot.show()

# evaluate an ARIMA model using a walk-forward validation

# series.index = series.index
# split into train and test sets
X = series.values
# print(X)
size = int(len(X) * 0.66)
train, test = X[0:size], X[size:len(X)]
# history = [x for x in train]
# predictions = list()

# o input é um array de arrays com os dias 
# print(type(train[0]))#, train)
# print(history)
l=len(test)
# walk-forward validation

# train=
#input
history = [x for x in train]
#treina
for t in range(l):
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit()
# prevê
output = model_fit.forecast()





# for t in range(l):



# 	model = ARIMA(history, order=(5,1,0))
# 	yhat = output[0]
# 	predictions.append(yhat)
# 	obs = test[t]
# 	history.append(obs)
 
 
 
	#print('predicted=%f, expected=%f' % (yhat, obs))
	print(t,"of",l)
# evaluate forecasts
# rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
# pyplot.plot(test)
# pyplot.plot(predictions, color='red')
# pyplot.show()

import csv
with open("results.csv","w") as f:
    write = csv.writer(f)
    write.writerow(predictions)

# import pickle    
# with open('learned_model.pkl','w') as f:
#   pickle.dump(results,f)

for i in range(100):
    print(model_fit.forecast())