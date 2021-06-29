from typing import Dict
from . import actors, orders_records, inventory, supply_chain as sc, logging_management as logs, transactions as tns
import datetime, yaml, time, pandas as pd
# from dashboard import dashboard_data as ds

# from simulation_configuration import *
 
logs.log(debug_msg="Started simulation.py")

## check if testes are configurated to run

class ClassSimulation:
    def __init__(self):
        self.simulation_status = "0-Created"
        self.simulation_id=id(self)
        self.time=1

        #create supply chain
        self.Object_supply_chain=sc.ClassSupplyChain()
        logs.log(debug_msg="[Created Object] Supply Chain  "+str( self.Object_supply_chain))

        self.ObejctTransationsRecords = tns.transactionsClass(self)
        
        #Lista que guarda todos os objectos atores
        self.actors_collection=[] 

        #DashBoard
        # self.dashboard = ds.dashboard_data(self)
        logs.log(debug_msg="Simulation created")

    def get_sim_id(self):
        return ClassSimulation.simulation_id

    #Import Configurations
    def get_actors_configurations(self,actors_configuration):

        with open(actors_configuration) as file:
            actors_config_yaml = yaml.load(file, Loader=yaml.FullLoader)



        #create the dict
        actors_config=dict()
        for actor in actors_config_yaml["Actors"]:
            actors_config[actor["Id"]]=actor

        return actors_config

    def create_actors(self,actors_configuration_file):
        logs.log(debug_msg="create_actors function called")
        configs_dict=self.get_actors_configurations(actors_configuration_file)

        ###############################
        #ADD  the final customer ###

        configs_dict["0"]= {'Id': 0, 'Max_inventory': 999999999, 'Name': 'Customer', 'Products': [], "Time_Average":0,"Time_variance":0, "Reorder_history_size":0}

        actors_list=(configs_dict.keys())



 
        for actor_id in actors_list:
            logs.log(debug_msg= self.get_actor_parameters(configs_dict, actor_id))
            name, a_id, avg, var, max_inventory, products, reorder_history_size = self.get_actor_parameters(configs_dict, actor_id)
            
            #Cria o ator
            actor_id = actors.actor(self, name=name, id=a_id, avg=avg, var=var, 
                                        max_inventory=max_inventory, reorder_history_size=reorder_history_size, products=products)
 
            #add to supply chain != da lista de atores
            self.Object_supply_chain.add_to_supply_chain(a_id)
            logs.log(debug_msg="actor "+str(a_id)+"Added to supply chain")


        logs.log(debug_msg="All Actors created")
    
        return actors_list

    def get_actor_parameters(self,configs_dict,actor):
        name                 = configs_dict[actor]["Name"]
        id                   = configs_dict[actor]["Id"]
        avg                  = configs_dict[actor]["Time_Average"]
        var                  = configs_dict[actor]["Time_variance"]
        max_inventory        = configs_dict[actor]["Max_inventory"]
        products          = configs_dict[actor]["Products"]
        reorder_history_size = configs_dict[actor]["Reorder_history_size"]


        return name, id, avg, var, max_inventory, products, reorder_history_size

    def change_simulation_status(self, status):
        if status == 1:
            self.simulation_status="1-Prepating Simulation"
        elif status == 2:
            self.simulation_status="2-Prepating Simulation"
        elif status == 3:
            self.simulation_status="3-Running Simulation"    
        elif status == 99:
            self.simulation_status="99-Simulation ended"            
        self.record_simulation_status(status)

    def record_simulation_status(self,simulation_status):
        logs.log(debug_msg="The simulation status changed to "+str(simulation_status))



