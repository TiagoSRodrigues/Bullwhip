import logging, time, os
from tqdm import tqdm
from simulation_configuration import * #logs_file_location , Logging_level 

# from os import listdir
# from os.path import isfile, join


##Logging level    log detail : 50 CRITICAL  >  40 ERROR  >  30 WARNING  >   20 INFO  >   10 DEBUG  >  0 NOTSET

''' Vou utilizar um sistema de 3 níveis de detalhe: baixo, médio e alto
    Baixo: level == WARNING == 50   Regista mínimo necessário de forma a retabilizar recursos
    médio: level == INFO    == 20   Regita os eventos principais para acompanhar os detalhes da simulação
    alto:  level == DEBUG   == 10   Regista todos os eventos da simulação 
'''



#create the log file
logging.basicConfig(filename=logs_file_location+'log_'+time.strftime("%Y%m%d_%H-%M-%S", time.localtime())+'.log', 
        level=Logging_level,
         format='%(asctime)s %(levelname)s %(message)s')
getattr(logging, Logging_level.lower() )("--->   Simulation Started   <----")

def log(critical_msg = None, error_msg = None):
    pass


def log(debug_msg = None, info_msg = None, message_warning = None):
    #Receive the logging level from envirement
    log_level = logging.root.level

    if debug_msg == None and info_msg != None:
        debug_msg=info_msg
        
    if debug_msg == None and info_msg == None and message_warning != None:
        debug_msg=message_warning

    #check veriable for printing
    if print_log_in_terminal == True:
        if Terminal_printting_level == "WARNING" and message_warning !=None:
            print(message_warning)        
        elif Terminal_printting_level == "INFO" and info_msg !=None:
            print(info_msg)        
        elif Terminal_printting_level == "DEBUG":
            print(debug_msg)
    
    #records log        
    if  log_level == 30 and message_warning != None:
        logging.warning(message_warning)
    elif log_level == 20 and info_msg != None:
        logging.info(info_msg)
    elif log_level == 10 and debug_msg != None :
        logging.debug(debug_msg)

#this funcion delete old logs, to avoid excessive trash        
def delete_old_logs(nr_of_files):
    arr = os.listdir(logs_file_location)
        
    if nr_of_files == all:
        return
    for el in range(0,len(arr)-nr_of_files):
        try:
            os.remove(logs_file_location+arr[el])
        except:
            pass

##Ainda n está implemnetado, a idea é fazer uma barra deprogresso
def simulation_time(x):
    steps = [1,2,3,4,5,6,7,8,9,10,11]
    for i in tqdm(steps):
        pass


delete_old_logs(nr_of_log_to_save)


    
    #chamar uma função de forma dinâmica
    # #getattr(logging, Logging_level.lower() )(debug_msg)
    # getattr(logging, Terminal_printting_level.lower() )(debug_msg)
    