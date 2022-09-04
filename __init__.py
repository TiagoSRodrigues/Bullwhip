# Version 10

import sys
import time
import inspect
import simulation_configuration as sim_cfg
from simulator import main as main, easter_eggs as ee, simulation, transactions, orders_records, actors, data_input, logging_management as logs, final_stats
from simulator import database

start_time = time.perf_counter()
argments=sys.argv

if len(argments)==3:
    days_simulated = sys.argv[1]
    TIME_SLOWDOWN = float(sys.argv[2])
    if days_simulated == "max":
        days_simulated = None
    else:
        days_simulated=int(days_simulated)


if len(argments)==2:
    days_simulated = sys.argv[1]
    TIME_SLOWDOWN = 0

    if days_simulated == "max":
        days_simulated = None
    else:
        days_simulated=int(days_simulated)

if len(argments)==1:
    days_simulated = 365
    TIME_SLOWDOWN = 0


## CONFIGS
#TODO CHECK THIS, SHOUD BE IN THE CONFIG FILE!!!!!
# sim_cfg.RUN_TESTS=False

# sim_cfg.TERMINAL_PRINTTING_LOG_LEVEL="INFO"
# sim_cfg.LOGGING_LEVEL="DEBUG"
# sim_cfg.PRINT_LOGS_IN_TERMINAL=True

if sim_cfg.PRINT_LOGS_IN_TERMINAL:
    ee.print_start(sim_cfg.LOGGING_LEVEL)


#Cria simulação
# Modos | traditional = 1 | Machine learnning = 2 | blockchain = 3  |
Object_Simulation=simulation.ClassSimulation(stock_management_mode = 3) 
Object_Simulation.sleep_time=TIME_SLOWDOWN
logs.log(info_msg="| CREATED OBJECT   | Simulation    "+str(Object_Simulation.simulation_id))

#create ligação à base de dados
# DataBase= database.DataBase()

#Cria atores
ObjectActors = Object_Simulation.create_actors( ACTORS_CONFIG_FILE = sim_cfg.ACTORS_CONFIG_FILE)


Object_Simulation.mongo_db.add_to_db(colection_name="simulation_stats",
                                     data={"_id":"cookbook",
                                           "value":str(Object_Simulation.cookbook)})
#prepara input
# input = data_input.get_input(days=days_simulated,min=1,max=10)

# input = data_input.get_input( input_type = "constant" , days=days_simulated, min=1)
# input_data = data_input.get_input( input_type = "file" ,
#                              days=days_simulated,
#                              filename="real_data_interpolated.csv" )


input_data = data_input.get_input( input_type = sim_cfg.INPUT_DATA_TYPE,
                                  days=sim_cfg.DAYS_TO_SIMULATE,
                                  filename=sim_cfg.INPUPUT_FILE_NAME )



"""

RUN SIMULATION

"""
try:
    main.main(input_data=input_data, simulation=Object_Simulation)
except:
    ee.play_error_sound()
    raise Exception(inspect.stack())


# """
# AFTER SIMULATION
# """
Object_Simulation.change_simulation_status(status=80)
logs.log(info_msg="Simulation time = "+str(time.perf_counter()-start_time))
logs.log(info_msg="Calculating final stats")

simulation_stats=final_stats.calculate_simulations_stats(simulation=Object_Simulation)


# open_transactions=Object_Simulation.ObejctTransationsRecords.open_transactions

simulation_stats.add_open_itens_to_db(Object_Simulation)

simulation_stats.add_delivered_transactions_to_td(Object_Simulation)

simulation_stats.db_connection.add_runtime_to_stats_db( round(time.perf_counter()-start_time, 2) )
simulation_stats.db_connection.add_simulation_stats_to_db(stat_value= Object_Simulation.simulation_stats)





simulation_stats.db_connection.save_stats( Object_Simulation.simulation_id)

#termina simulação
Object_Simulation.change_simulation_status(status=99)
#registos de tempos e final



if sim_cfg.PRINT_LOGS_IN_TERMINAL:ee.final_prints(start_time)

logs.log(info_msg="--->   Simulation Ended   <----")
# ee.play_final_sound()

