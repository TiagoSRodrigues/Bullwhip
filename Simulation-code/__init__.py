import logging_management as log
import sys,  pandas as pd, numpy as np, time, os, gc
os.system('cls' if os.name == 'nt' else 'clear')
start_time = time.perf_counter()
import main, easter_eggs as ee, simulation, transactions, orders_records, actors, data_input
from simulation_configuration import actors_configuration_file


ee.print_start(log.Logging_level)
# simulation_time(2)

#Cria simulação 
Object_Simulation=simulation.ClassSimulation()
log.log(info_msg="[Created Object] Simulation    "+Object_Simulation.simulation_id)


#Cria atores
ObjectActors=Object_Simulation.create_actors(actors_configuration_file=actors_configuration_file)

#prepara input
input = data_input.get_input(days=10,min=1,max=5)


########### Start orders
Object_Simulation.record_simulation_status(simulation_status=3)


# log.open_object(Object_Simulation)


# main.main(input,Object_Simulation )


# log.get_variables()

#termina simulação
Object_Simulation.change_simulation_status(status=99)
#registos de tempos e final 
log.log(info_msg="Simulation time = "+str(time.perf_counter()-start_time))
ee.print_sucess()
log.log(info_msg="--->   Simulation Ended   <----")