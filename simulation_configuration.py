""" This document contains the base configuration for the simulation

    This excludes the actors configurations
    that are in the actors_configurations.json file,
    inside the simulator folder
"""

import os
import gc


"""
    Directories 
    
"""


DIRECTORY_PATH = __file__[:-28].replace('\\','//')

#Files Directories
ACTORS_CONFIG_FILE=DIRECTORY_PATH + "//simulator//actors_configuration.json"
LOG_FILES_PATH = DIRECTORY_PATH + '//data//logs//'
SOURCE_DATA_PATH =  DIRECTORY_PATH + '//data//input//input_data.csv'
CONFIGS_BACKUP= DIRECTORY_PATH + '//data//Configuration backups//'

ORDERS_RECORDS_FILE = DIRECTORY_PATH + '//data//records//orders_record.csv'
ORDERS_RECORDS_FILE_PATH = DIRECTORY_PATH + '//data//records//'
FINAL_EXPORT_FILES_PATH = DIRECTORY_PATH + '//data//exports//'
TRANSCTIONS_RECORDS_FILE = DIRECTORY_PATH + '//data//records//TRANSCTIONS_RECORDS_FILE.json'

INVENTORY_FILE = DIRECTORY_PATH + '//data//records//INVENTORY_FILE.json'

""" 
    logging 
"""
#Max number of logs to save, if all = False
NUMBER_OF_HISTORY_LOGFILES= 30

#Define if the logs are printed in the terminal while running
LOGGING_LEVEL="DEBUG"
PRINT_LOGS_IN_TERMINAL=True
TERMINAL_PRINTTING_LOG_LEVEL="INFO"


if PRINT_LOGS_IN_TERMINAL:
    os.system('cls' if os.name == 'nt' else 'clear')
gc.collect()



""""

Simulation Configuration

"""



INPUT_DATA_TYPE = "file" #file or constant

# limits days to simulate,  to run all date use None
DAYS_TO_SIMULATE = 365

INPUPUT_FILE_NAME = "real_data_interpolated.csv"

# in order to see the evolutions of the simulation, increase the sleep time
TIME_SLOWDOWN = 0 #seconds

# Simulations modes:  | traditional = 1 | Machine learnning = 2 | blockchain = 3  |
SIMULATION_MODE = 3

PRODUCTION_METHOD = 1 # 1 = produces immediately when receive raw mat. | 2 = produces for delivery

#
PLAY_SOUND = False
