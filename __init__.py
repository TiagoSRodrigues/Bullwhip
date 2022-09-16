# Version 10

import logging
import os
from time import perf_counter
from inspect import stack
import sys

from sklearn import config_context
import simulation_configuration as sim_cfg
from simulator import main as main
from simulator import easter_eggs as ee
from simulator import simulation
from simulator import transactions
from simulator import data_input
from simulator import logging_management as logs
from simulator import final_stats
from simulator import database

def run_simulation(simulation_mode, actors_configs):
    ''' inicial function for start simulation'''
    start_time = perf_counter()

    # print the simulation start header 
    if sim_cfg.PRINT_LOGS_IN_TERMINAL:
        ee.print_start(sim_cfg.LOGGING_LEVEL)

    logs.log(debug_msg="|day | actor | file | function | msg   <-- log format")

    # data input
    input_data = data_input.get_input( input_type = sim_cfg.INPUT_DATA_TYPE,
                                    days=sim_cfg.DAYS_TO_SIMULATE,
                                    filepath=sim_cfg.SOURCE_DATA_PATH,
                                    min=sim_cfg.MINIMUM_DAILY_ORDERS,
                                    max=sim_cfg.MAXIMUM_DAILY_ORDERS,)



    # Creates the simulation object

    # Modos | traditional = 1 | Machine learnning = 2 | blockchain = 3  |
    Object_Simulation=simulation.ClassSimulation(stock_management_mode = simulation_mode, actors_configs = actors_configs)

    # Valida que não existirão encomendar superiores ao stock de segurança
    Object_Simulation.validate_data_compatibilty(input_data=input_data, actors_config=actors_configs)


    Object_Simulation.mongo_db.add_to_db(colection_name="simulation_stats",
                                        data={"_id":"cookbook",
                                            "value":str(Object_Simulation.cookbook)})

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

    ee.print_after_simulation()

    Object_Simulation.change_simulation_status(status=80)
    Object_Simulation.save_simulation_stats()
    logs.log(info_msg="Simulation time = "+str(perf_counter()-start_time))

    logs.log(info_msg="Calculating final stats")

    simulation_stats=final_stats.calculate_simulations_stats(simulation=Object_Simulation)
    if sim_cfg.DB_TYPE == 1:
        simulation_stats.save_final_stats_on_db
    if sim_cfg.DB_TYPE == 2:
        simulation_stats.extract_results(file_name=f"{Object_Simulation.simulation_id}_{simulation_mode}_{actors_configs}")
        

    #termina simulação
    Object_Simulation.change_simulation_status(status=99)

    # Object_Simulation.show_simulation_stats()
    #registos de tempos e final
    if sim_cfg.PRINT_LOGS_IN_TERMINAL:ee.final_prints(start_time)

    logs.log(info_msg="--->   Simulation Ended   <----")


    logging.shutdown()
    print("\ntamnho do log file: ",os.path.getsize(sim_cfg.LOG_FILES_PATH))



    if sim_cfg.PLAY_SOUND:
        ee.play_final_sound()


config_files=["actors_configuration_a.json","actors_configuration_b.json","actors_configuration_c.json","actors_configuration_d.json",]

for file in config_files:
    config_path = f"{sim_cfg.DIRECTORY_PATH}//simulator//{file}"
    run_simulation( simulation_mode=1, actors_configs= config_path )
    run_simulation( simulation_mode=3, actors_configs= config_path )