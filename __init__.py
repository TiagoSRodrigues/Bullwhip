# Version 10

from time import perf_counter
from inspect import stack
import simulation_configuration as sim_cfg
from simulator import main as main, easter_eggs as ee, simulation, transactions, orders_records, actors, data_input, logging_management as logs, final_stats
from simulator import database

start_time = perf_counter()

# print the simulation start header 
if sim_cfg.PRINT_LOGS_IN_TERMINAL:
    ee.print_start(sim_cfg.LOGGING_LEVEL)


# Creates the simulation object

# Modos | traditional = 1 | Machine learnning = 2 | blockchain = 3  |
Object_Simulation=simulation.ClassSimulation(stock_management_mode = sim_cfg.SIMULATION_MODE) 
Object_Simulation.sleep_time=sim_cfg.TIME_SLOWDOWN
logs.log(info_msg= f"| CREATED OBJECT   | Simulation    {str(Object_Simulation.simulation_id)}")


#Create actors
ObjectActors = Object_Simulation.create_actors( ACTORS_CONFIG_FILE = sim_cfg.ACTORS_CONFIG_FILE)

Object_Simulation.mongo_db.add_to_db(colection_name="simulation_stats",
                                     data={"_id":"cookbook",
                                           "value":str(Object_Simulation.cookbook)})
# data input
input_data = data_input.get_input( input_type = sim_cfg.INPUT_DATA_TYPE,
                                  days=sim_cfg.DAYS_TO_SIMULATE,
                                  filename=sim_cfg.INPUPUT_FILE_NAME )


"""

RUN SIMULATION

"""
try:
    main.main(input_data=input_data,
              simulation=Object_Simulation)
except Exception as exc:
    if sim_cfg.PLAY_SOUND:
        ee.play_error_sound()
    raise Exception(stack()) from exc



# """
# AFTER SIMULATION
# """

Object_Simulation.change_simulation_status(status=80)
logs.log(info_msg="Simulation time = "+str(perf_counter()-start_time))

logs.log(info_msg="Calculating final stats")
simulation_stats=final_stats.calculate_simulations_stats(simulation=Object_Simulation)
simulation_stats.add_open_itens_to_db(Object_Simulation)
simulation_stats.add_delivered_transactions_to_td(Object_Simulation)
simulation_stats.db_connection.add_runtime_to_stats_db( round(perf_counter()-start_time, 2) )
simulation_stats.db_connection.add_simulation_stats_to_db(stat_value= Object_Simulation.simulation_stats)
simulation_stats.db_connection.save_stats( Object_Simulation.simulation_id)
simulation_stats.db_connection.export_db(sim_cfg.FINAL_EXPORT_FILES_PATH)
#termina simulação
Object_Simulation.change_simulation_status(status=99)

#registos de tempos e final
if sim_cfg.PRINT_LOGS_IN_TERMINAL:ee.final_prints(start_time)

logs.log(info_msg="--->   Simulation Ended   <----")

if sim_cfg.PLAY_SOUND:
    ee.play_final_sound()

