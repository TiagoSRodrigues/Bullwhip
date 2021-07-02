import  os

directory_path = __file__[:-28].replace('\\','//')

#Files Directories
actors_configuration_file=directory_path + "//simulator//actors_configuration.yaml"
logs_file_location = directory_path + '//data//logs//'
source_data =  directory_path + '//data//input//input_data.csv'
Configuration_backups= directory_path + '//data//Configuration backups//'

#paramenters   ##LOGS: DEBUG,  INFO, WARNING                #not in use: ERROR, CRITICAL 
Logging_level="DEBUG"

orders_record_file = directory_path + '//data//records//orders_record.csv'
orders_record_path = directory_path + '//data//records//'
transactions_record_file = directory_path + '//data//records//transactions_record_file.json'

inventory_file = directory_path + '//data//records//inventory_file.json'



#Max number of logs to save, if all = False 
nr_of_log_to_save= 10

#Define if the logs are printed in the terminal while running
print_log_in_terminal=True
Terminal_printting_level="INFO"

#Run tests before simulations
Run_tests=False


