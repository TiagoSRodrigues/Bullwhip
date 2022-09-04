""" LOGGING MANAGEMENT stuff
  Logging level    log detail : 50 CRITICAL  >  40 ERROR  >  30 WARNING  >   20 INFO  >   10 DEBUG  >  0 NOTSET

  Vou utilizar um sistema de 3 níveis de detalhe: baixo, médio e alto
  Baixo: level == WARNING == 50 Regista mínimo necessário de forma a retabilizar recursos
  médio: level == INFO    == 20 Regita os eventos principais para acompanhar detalhes da simulação
  alto:  level == DEBUG   == 10 Regista todos os eventos da simulação
"""

import os
import gc
import time
import logging
import inspect
from pprint import pprint
import simulation_configuration  as sim_cfg


#create the log file



logging.basicConfig(filename=sim_cfg.LOG_FILES_PATH+'log_'+time.strftime("%Y%m%d_%H-%M-%S",
                                                                             time.localtime())+'.log',
        level=sim_cfg.LOGGING_LEVEL,
         format='%(asctime)s %(levelname)s %(message)s')

#TODO  #!APAGAR se n der problemas
# getattr(logging, sim_cfg.LOGGING_LEVEL.lower() )("--->   Simulation Started   <----") 

# def new_log(action, args="", notes=""):
#     """Automaticamente cria um registo de log com a seguinte estrutura:
#     |                    |                              |                                       |                                 |                       |
#     |<-------20--------->|<------------30-------------->|<------------- variável -------------->|<--------    variável  --------->|                       |
#     |    file name       |      called_function         |         calling_funcion               |               args              |        notes          |

#     """
#     log_level = logging.root.level
#     print("\n\n\n\n\n")
#     for el in inspect.stack():
#         print(el)


#     """
#     called_function=inspect.stack()[0][3]
#     calling_funcion=inspect.stack()[1][3]
#     frame = inspect.stack()[1]
#     module = inspect.getmodule(frame[0])
#     file_name = module.__file__.split("\\")[-1]

#     colummn_size=30
#     #string sizes
#     file_size, action_size, args_size, notes_size = len(file_name),len(action),len(args),len(notes)
#     if (file_size or action_size) > colummn_size:
#         print("WARNNING! log size is too big", file_size, action_size)

#     record_str="| {}{}| {}{}| {}{}| {} | {}|".format(file_name, (20-file_size)*" ",
#                                                 called_function, (colummn_size-action_size)*" ",
#                                                 calling_funcion, (colummn_size-action_size)*" ",
#                                                 args, notes )

#     logging.debug(record_str)
#     print(record_str)
#     """
def show_function_tree():
    """ DEBUG FUNCTION
        prints the stack of instructions that rise to the error """

    function_tree=[]
    for i in inspect.stack():
        function_tree.append([ i[1].split("\\")[-1],i[3] ])

    print(function_tree)



def log(debug_msg = None, info_msg = None, warning_msg = None):
    """writes the log strings to files

    """
    # Depriciated
    
    # if sim_cfg.LOG_TO_BD:
    #     sim_cfg.log_id+=1
    #     mongo_client = pymongo.MongoClient("mongodb://localhost:2021/")
    #     simulation_db = mongo_client["simulation"]["simulation_log"].insert_one(
    #         {"_id":sim_cfg.log_id,
    #          "log":debug_msg})


    #Receive the logging level from envirement
    log_level = logging.root.level

    if debug_msg == None and info_msg != None:
        debug_msg , info_msg = info_msg, debug_msg

    if debug_msg == None and info_msg == None and warning_msg != None:
        debug_msg=warning_msg
        print(warning_msg)

    #check veriable for printing
    if sim_cfg.PRINT_LOGS_IN_TERMINAL == True:
        if sim_cfg.TERMINAL_PRINTTING_LOG_LEVEL == "WARNING" and warning_msg !=None:
            print(warning_msg)
        elif sim_cfg.TERMINAL_PRINTTING_LOG_LEVEL == "INFO" and info_msg !=None:
            print(info_msg)
        elif sim_cfg.TERMINAL_PRINTTING_LOG_LEVEL == "DEBUG":
            print(debug_msg)

    #records log
    if  log_level == 30 and warning_msg != None:
        logging.warning(str(warning_msg))


    elif log_level == 20 and info_msg != None:
        logging.info(str(info_msg))
        if warning_msg != None:
            logging.warning(str(warning_msg))


    elif log_level == 10 and debug_msg != None :
        logging.debug(str(debug_msg))
        if warning_msg != None:
            logging.warning(str(warning_msg))
        if info_msg != None:
            logging.info(str(info_msg))




#this funcion delete old logs, to avoid excessive trash
def delete_old_logs(folder=None, file=None,  NUMBER_OF_HISTORY_LOGFILES=None):
    try:
        if folder != None:
            arr = os.listdir(sim_cfg.LOG_FILES_PATH)

            if NUMBER_OF_HISTORY_LOGFILES == all:
                os.remove(sim_cfg.LOG_FILES_PATH)

            for el in range(0,len(arr)-NUMBER_OF_HISTORY_LOGFILES):
                os.remove(sim_cfg.LOG_FILES_PATH+arr[el])

        elif file != None:
            os.remove(file)
    except FileNotFoundError:
        log(debug_msg = "No files to delete")
        # if sim_cfg.PRINT_LOGS_IN_TERMINAL:
        #     print("No files to delete")


##Ainda n está implemnetado, a idea é fazer uma barra deprogresso
# def simulation_time(x):
#     steps = [1,2,3,4,5,6,7,8,9,10,11]
#     for i in tqdm(steps):
#         pass



def print_day(simulation, quantity):
    if sim_cfg.PRINT_LOGS_IN_TERMINAL:
        print("day {}  customer order {}".format(simulation.time, quantity), end="\r")

def show_object_attributes(object):


    print( 3*"\n","Attributes of",object,"\n" )
    pprint( vars(object) )
    print( 3*"\n" )

def open_object(object):
    print(10*"======","\n\n DIR:")
    print( type(object), "\n" )
    for el in dir(object):
        print(el)
    print(10*"======","\n\n VARS")
    for el in vars(object):
        print(el)

    print(10*"======","\n\n\n")

def get_variables(var=None):
    if var == "globals":
        for el in globals():
            print(el)
    if var == "locals":
        for el in locals():
            print(el)

    else:
        print("\n GLOBALS \n")
        for el in globals():
            print(el)

        print("\n LOCALS \n")
        for el in locals():
            print(el)


def save_all_objects():
    filename="All_objects_"+time.strftime("%Y%m%d_%H-%M-%S", time.localtime())+".txt"
    with open(filename, 'w') as filehandle:
        errors=0
        for el in gc.get_objects():
            try:
                filehandle.write( str(el)+'\n')
            except:
                errors+=1
        filehandle.write( '\n and more '+str(errors)+" Errors")


def pretty(d, indent=0):
    import emoji
    for key, value in d.items():
        print(' ' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print( emoji.emojize('  :shell: ' , use_aliases=True ) * (indent+1) + str(value))


    #https://www.webfx.com/tools/emoji-cheat-sheet/

delete_old_logs( folder = sim_cfg.LOG_FILES_PATH, NUMBER_OF_HISTORY_LOGFILES = sim_cfg.NUMBER_OF_HISTORY_LOGFILES)
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_1.csv"           )
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_2.csv"           )
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_3.csv"           )
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_4.csv"           )
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_5.csv"           )
# delete_old_logs( file = sim_cfg.ORDERS_RECORDS_FILE_PATH+   "orders_record_6.csv"           )
# delete_old_logs( file = sim_cfg.SIM_STATUS_FILE_PATH  )
# delete_old_logs( file = sim_cfg.INVENTORY_FILE          )



delete_old_logs( file = sim_cfg.TRANSCTIONS_RECORDS_FILE)