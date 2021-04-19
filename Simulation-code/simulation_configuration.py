import  os

directory_path = r'%s' % os.getcwd().replace('\\','//')


#Files Directories
actors_configuration_file=directory_path + "//Simulation-code//actors_configuration.yaml"
logs_file_location = directory_path + '//Data//Logs//'
source_data =  directory_path + '//Data//input//input_data.csv'



#paramenters   ##LOGS: DEBUG,  INFO, WARNING                #not in use: ERROR, CRITICAL 
Logging_level="DEBUG"

#Max number of logs to save, if all = False 
nr_of_log_to_save= 10

#Define if the logs are printed in the terminal while running
print_log_in_terminal=True
Terminal_printting_level="INFO"


#Run tests before simulations
Run_tests=False



"C:\\Users\\Tiago\\Google Drive\\Tese\\GitHub\\BullwhipBu"

