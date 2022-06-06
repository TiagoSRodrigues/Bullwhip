from fileinput import filename
import sys,  pandas as pd, numpy as np, time, os, gc

import inspect
import simulation_configuration as sim_cfg
if sim_cfg.print_log_in_terminal: os.system('cls' if os.name == 'nt' else 'clear')
gc.collect()

start_time = time.perf_counter()
from simulator import main as main, easter_eggs as ee, simulation, transactions, orders_records, actors, data_input, logging_management as logs, final_stats
from simulator import database

argments=sys.argv

if len(argments)==3:
    days_simulated = sys.argv[1]
    sleep_time = float(sys.argv[2])
    if days_simulated == "max":
        days_simulated = None
    else:
        days_simulated=int(days_simulated)


if len(argments)==2:
    days_simulated = sys.argv[1]
    sleep_time = 0
    
    if days_simulated == "max":
        days_simulated = None
    else:
        days_simulated=int(days_simulated)    
    
if len(argments)==1:
    days_simulated = 365
    sleep_time = 0

## VERSION 10

## CONFIGS
sim_cfg.Run_tests=False

sim_cfg.Terminal_printting_level="INFO"
sim_cfg.Logging_level="DEBUG"
sim_cfg.print_log_in_terminal=True

if sim_cfg.print_log_in_terminal: ee.print_start(sim_cfg.Logging_level)


#Cria simulação
Object_Simulation=simulation.ClassSimulation(stock_management_mode = 1) # Modos | traditional = 1 | Machine learnning = 2 | blockchain = 3  |
Object_Simulation.sleep_time=sleep_time
logs.log(info_msg="| CREATED OBJECT   | Simulation    "+str(Object_Simulation.simulation_id))

#create ligação à base de dados
# DataBase= database.DataBase()

#Cria atores
ObjectActors = Object_Simulation.create_actors( actors_configuration_file = sim_cfg.actors_configuration_file)


Object_Simulation.mongo_db.add_to_db(colection_name="simulation_stats", data={"_id":"cookbook","value":str(Object_Simulation.cookbook)})
#prepara input
# input = data_input.get_input(days=days_simulated,min=1,max=10)

# input = data_input.get_input( input_type = "constant" , days=days_simulated, min=1)
input = data_input.get_input( input_type = "file" , days=days_simulated, filename="real_data_interpolated.csv" )

"""

RUN SIMULATION

"""
try:
    main.main(input_data=input, simulation=Object_Simulation)
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



if sim_cfg.print_log_in_terminal:ee.final_prints(start_time)

logs.log(info_msg="--->   Simulation Ended   <----")
# ee.play_final_sound()
 
 