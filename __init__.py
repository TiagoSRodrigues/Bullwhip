import sys,  pandas as pd, numpy as np, time, os, gc
os.system('cls' if os.name == 'nt' else 'clear')
gc.collect()

start_time = time.perf_counter()
from simulator import main as main, easter_eggs as ee, simulation, transactions, orders_records, actors, data_input, logging_management as logs
import simulation_configuration as sim_cfg


## VERSION 4 

## CONFIGS
sim_cfg.Run_tests=False
sim_cfg.print_log_in_terminal=False
sim_cfg.Terminal_printting_level="INFO"
sim_cfg.Logging_level="DEBUG"

ee.print_start(sim_cfg.Logging_level)


#Cria simulação 
Object_Simulation=simulation.ClassSimulation()
logs.log(info_msg="| CREATED OBJECT   | Simulation    "+str(Object_Simulation.simulation_id))


#Cria atores
ObjectActors = Object_Simulation.create_actors( actors_configuration_file = sim_cfg.actors_configuration_file)

#prepara input
input = data_input.get_input(days=30,min=1,max=8)



### RUN SIMULATION
main.main(input_data=input, simulation=Object_Simulation)



# logs.get_variables()

#termina simulação
Object_Simulation.change_simulation_status(status=99)
#registos de tempos e final 
logs.log(info_msg="Simulation time = "+str(time.perf_counter()-start_time))
ee.print_sucess()
logs.log(info_msg="--->   Simulation Ended   <----")