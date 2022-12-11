# from simulation_configuration import SOURCE_DATA_PATH
import csv
import numpy as np
import pandas as pd
from sys import path
from math  import ceil
from math import floor
from random import randint
from . import logging_management as logs
def get_input(input_type,  days=None, min=None, max=None, filepath=None):

    if input_type == "file":
        values=get_raw_data(filepath)
        if days == "all":
            return values
        return values[-days:]

    if input_type == "file_old":
        good_values, errors, values = check_input_datafile()

        if errors >0:
            logs.new_log(file="data_input", function="get_input", actor=" ", debug_msg= f"erros no input: {errors}")

        if days == "all":
            return values
        return values[-days:]

    if input_type == "constant":
        a = np.empty(days, dtype=np.int64)
        a.fill(min)
        return a

    if input_type == "sequencial":
        np.linspace(min,max, num=max-min, endpoint=False,  dtype=int, axis=0)

    if input_type == "triangular":
        values = []
        slope  = 1
        x = min
        while len(values) < days:
            values.append(x)
            x = x + 1 * slope

            if x == max:
                slope = -1
            elif x == min:
                slope = 1
        return values

    values = []
    for i in range(days):
        values.append(randint(min, max))
    return values


def get_raw_data(filepath):
    # from numpy import genfromtxt

    with open(filepath, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        values = []
        not_values =[]
        for row in csv_reader:
            try:
                val=int(row[0])
                values.append(val)
            except:
                not_values.append(row)

    if not_values:
        logs.log(debug_msg = f"values not included: {not_values}")
    return values




def check_input_datafile():
    def better_round(value):
        if value%1 *10 < 5:
            return floor(value)
        return ceil(value)
    errors=-1 #(menos um porque os headers vão dar erro)
    good_values=0
    values=[]

    scale_fator=100 #multiplica o valor da cotação por dez

    data=open(cambio_data)
    for line in data:
        try:
            date, val, *_ = [item.strip() for item in line.split(';')]
            #date_check=datetime.datetime.strptime(date, '%Y-%m-%d')
            values.append(better_round(float(val)*scale_fator))
            good_values+=1
            # print(val)
        except:
            errors+=1


        # logs.log(debug_msg = "DATA_INPUT  input file checked good values: "+str(good_values)+"  errors: "+str(errors))
    data.close()
    return good_values, errors, values

