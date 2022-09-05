import collections
import pymongo
import pandas as pd
import numpy as np

mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")
simulation_db = mongo_client["simulation"]

DIRECTORY_PATH = __file__[:-28].replace('\\','//')

FINAL_EXPORT_FILES_PATH = DIRECTORY_PATH + '//data//exports//'







a = {'1': {'1001': {'name': 'ProductA', 'id': 1001, 'initial_stock': 13648, 'safety_stock': 0, 'composition': {'2001': 1}, 'in_stock': 13648}}, '2': {'2001': {'name': 'ProductB', 'id': 2001, 'initial_stock': 13648, 'safety_stock': 0, 'composition': {'3001': 1}, 'in_stock': 13648}}, '3': {'3001': {'name': 'ProductC', 'id': 3001, 'initial_stock': 13648, 'safety_stock': 0, 'composition': {'4001': 1}, 'in_stock': 13648}}, '4': {'4001': {'name': 'ProductD', 'id': 4001, 'initial_stock': 13648, 'safety_stock': 0, 'composition': {'5001': 1}, 'in_stock': 13648}}, '5': {'5001': {'name': 'ProductE', 'id': 5001, 'initial_stock': 9999999999, 'safety_stock': 1, 'reorder_history_size': 7, 'in_stock': 9999999999}}, '0': {'0': {'name': 'Product_Null', 'id': 0, 'initial_stock': 0, 'safety_stock': 0, 'composition': {'0000': 0}, 'in_stock': 0}}}


for k, v in a.items():
    # print( v)
    
    for k2, v2 in v.items():
        print(k, v2["id"], v2["in_stock"])
    
