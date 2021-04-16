import logging_management as log
import sys,  pandas as pd, numpy as np, time, os
os.system('cls' if os.name == 'nt' else 'clear')
start_time = time.perf_counter()
import easter_eggs as ee, simulation, transactions, orders_records, actors
from simulation_configuration import actors_configuration_file


ee.print_start(log.Logging_level)
# simulation_time(2)

#Cria simulação
Simulation=simulation.simulation()
supply_chain=Simulation.create_supply_chain()

#Cria atores
Simulation.create_actors(actors_configuration_file)







log.log(info_msg="Simulation time = "+str(time.perf_counter()-start_time))
ee.print_sucess()
log.log(info_msg="--->   Simulation Ended   <----")