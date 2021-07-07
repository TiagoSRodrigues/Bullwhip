from typing import Dict
from . import actors, orders_records, inventory, supply_chain as sc, logging_management as logs, transactions as tns
import datetime, yaml, time, pandas as pd, simulation_configuration as sim_cfg, json
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
        self.Object_supply_chain=sc.ClassSupplyChain(self)
        logs.log(debug_msg="| CREATED OBJECT   | Supply Chain  "+str( self.Object_supply_chain))

        self.ObejctTransationsRecords = tns.transactionsClass(self)
        #Lista que guarda todos os objectos atores
        self.actors_collection=[] 


        self.global_inventory={}
        #DashBoard
        # self.dashboard = ds.dashboard_data(self)

        self.cookbook = {}

        logs.log(debug_msg="| status           | Simulation created")

        try:
            self.sleep_time = float( input( " Insert delay time:") )
        except: 
            self.sleep_time = 0

        
    #Import Configurations
    def get_actors_configurations(self,actors_configuration):

        with open(actors_configuration) as file:
            actors_config_json = json.load(file)

        #create the dict and populate
        actors_config=dict()
        for actor in actors_config_json["actors"]:
            actors_config[actor["id"]]=actor
        return actors_config

    def create_actors(self,actors_configuration_file):
        configs_dict=self.get_actors_configurations(actors_configuration_file)

        #ADD  the final customer ###
        
        configs_dict["0"]= {'id': 0, 'max_inventory': 999999999, 'name': 'Customer', 'products': [ ] ,  "time_average":0,"time_variance":0}                   
        actors_list=(configs_dict.keys())



 
        for actor_id in actors_list:
            logs.log(debug_msg= self.get_actor_parameters(configs_dict, actor_id))
            name, a_id, avg, var, max_inventory, products = self.get_actor_parameters(configs_dict, actor_id)
            
            #Cria o ator
            actor_id = actors.actor(self, name=name, id=a_id, avg=avg, var=var, 
                                        max_inventory=max_inventory, products=products)
 
            #add to supply chain != da lista de atores
            self.Object_supply_chain.add_to_supply_chain(a_id)
            logs.log(debug_msg="| FUNCTION         | Object_supply_chain.add_to_supply_chain actor "+str(a_id)+" Added to supply chain")


    
        return actors_list

    def get_actor_parameters(self,configs_dict,actor):
        name                 = configs_dict[actor]["name"]
        id                   = configs_dict[actor]["id"]
        avg                  = configs_dict[actor]["time_average"]
        var                  = configs_dict[actor]["time_variance"]
        max_inventory        = configs_dict[actor]["max_inventory"]
        products          = configs_dict[actor]["products"]


        return name, id, avg, var, max_inventory, products

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

    def get_actor_by_id(self, id):
        for actor in self.actors_collection:
            if int(actor.id) == id: 
                return actor 
        return False    

    def reset_all_actors_status(self):
        for actor in self.actors_collection:
            actor.actor_state = 0

    def speed(self):
        time.sleep(self.sleep_time)

    #---------------------------------------------------------------------------------------------------------------------Dashboard
    def update_global_inventory(self, actor_id, product_id, quantity):

        inventory = self.global_inventory 

        actor_id, product_id, quantity  = int(actor_id), int(product_id), int(quantity)
        try:
            ator = inventory[actor_id]
            ator[product_id] = ator[product_id]+quantity 
        except:
            inventory[actor_id]= {product_id : quantity}

        with open(sim_cfg.inventory_file, 'w') as file:
            json.dump(inventory, file)

        logs.log(debug_msg="| Refresh Inventory| Simulation    | Updating Global Inventory :{}".format(inventory))
