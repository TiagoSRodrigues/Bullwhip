import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import models, layers, utils, backend as K
import matplotlib.pyplot as plt
import shap


# series=np.asarray(df,dtype=np.int32)
data_file='N:\\TESE\\Bullwhip\\data\\input\\data_amplified.csv'

dataset = pd.read_csv(data_file,  engine='python')

print(dataset)


