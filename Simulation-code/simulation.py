import actors, orders_records, inventory, supply_chain as sc
import datetime, yaml
from logging_management import *
from simulation_configuration import *

log(debug_msg="Started simulation.py")

## check if testes are configurated to run
if Run_tests: import tests

class ClassSimulation:
    def __init__(self):
        self.simulation_status = "0-Created"
        self.simulation_id="sim_"+str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))   

        #create supply chain
        self.Object_supply_chain=sc.ClassSupplyChain()
        log(debug_msg="[Created Object] Supply Chain  "+str( self.Object_supply_chain))


        log(debug_msg="Simulation created")
        
    def get_sim_id(self):
        return ClassSimulation.simulation_id

    #Import Configurations
    def get_actors_configurations(self,actors_configuration):
        with open(actors_configuration) as file:
            actors_config = yaml.load(file, Loader=yaml.FullLoader)
        return actors_config

    def create_actors(self,actors_configuration_file):
        log(debug_msg="create_actors function called")
        configs_dict=self.get_actors_configurations(actors_configuration_file)
        actors_list=(configs_dict['Actors'].keys())

        for actor_name in actors_list:
            
            log(debug_msg= self.get_actor_parameters(configs_dict, actor_name))
            name, a_id, avg, var, safety_stock, initial_stock, max_inventory, reorder_history_size, precedence = self.get_actor_parameters(configs_dict, actor_name)
            
            #Cria o ator
            actor_name = actors.actor( name=name, id=a_id, avg=avg, var=var, safety_stock=safety_stock, initial_stock=initial_stock,
                                        max_inventory=max_inventory, reorder_history_size=reorder_history_size, precedence=precedence)
           
            #Cria o Registo de encomendas
            actor_stock_record = orders_records.ClassOrdersRecord(actor_name)
            
            #Cria os inventários                                   #!   ↓ Produt is forced to 1   !
            actor_inventary=inventory.inventory(actor=actor_name,product=1, initial_stock=initial_stock,safety_stock=safety_stock,max_inventory=max_inventory)
            actor_name.get_actor_precedence()

            #add to supply chain
            self.Object_supply_chain.add_to_supply_chain(a_id)
            log(debug_msg="actor "+str(a_id)+"Added to supply chain")
# 

        log(debug_msg="All Actors created")
        return actors_list


    def get_actor_parameters(self,configs_dict,actor):
        name                 = configs_dict['Actors'][actor]["Name"]
        id                   = configs_dict['Actors'][actor]["Id"]
        avg                  = configs_dict['Actors'][actor]["Time_Average"]
        var                  = configs_dict['Actors'][actor]["Time_variance"]
        initial_stock        = configs_dict['Actors'][actor]["initial_stock"]
        safety_stock         = configs_dict['Actors'][actor]["safety_stock"]
        max_inventory        = configs_dict['Actors'][actor]["max_inventory"]
        reorder_history_size = configs_dict['Actors'][actor]["Reorder_history_days"]
        precedence           = configs_dict['Actors'][actor]["precedence"]

        return name, id, avg, var, safety_stock, initial_stock, max_inventory, reorder_history_size,precedence

    def change_simulation_status(self, status):
        if status == 1:
            self.simulation_status="1-Prepating Simulation"
        if status == 2:
            self.simulation_status="2-Prepating Simulation"
        if status == 3:
            self.simulation_status="3-Running Simulation"    
        if status == 99:
            self.simulation_status="99-Simulation ended"            
        self.record_simulation_status(status)

    def record_simulation_status(self,simulation_status):
        log(debug_msg="The simulation status changed to "+str(simulation_status))