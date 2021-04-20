import actors, orders_records, inventory, supply_chain as sc, logging_management as logs
import datetime, yaml
from simulation_configuration import *
 
logs.log(debug_msg="Started simulation.py")

## check if testes are configurated to run

class ClassSimulation:
    def __init__(self):
        self.simulation_status = "0-Created"
        self.simulation_id=id(self)

        #"sim_"+str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))   #deve ser para apagar

        #create supply chain
        self.Object_supply_chain=sc.ClassSupplyChain()
        logs.log(debug_msg="[Created Object] Supply Chain  "+str( self.Object_supply_chain))


        logs.log(debug_msg="Simulation created")
        
        #Lista que guarda todos os objectos atores
        self.actors_collection=[]

    def get_sim_id(self):
        return ClassSimulation.simulation_id

    #Import Configurations
    def get_actors_configurations(self,actors_configuration):
        with open(actors_configuration) as file:
            actors_config = yaml.load(file, Loader=yaml.FullLoader)
        return actors_config

    def create_actors(self,actors_configuration_file):
        logs.log(debug_msg="create_actors function called")
        configs_dict=self.get_actors_configurations(actors_configuration_file)
        actors_list=(configs_dict['Actors'].keys())

        for actor_name in actors_list:
            
            logs.log(debug_msg= self.get_actor_parameters(configs_dict, actor_name))
            name, a_id, avg, var, safety_stock, initial_stock, max_inventory, reorder_history_size, precedence = self.get_actor_parameters(configs_dict, actor_name)
            
            #Cria o ator
            actor_name = actors.actor(self, name=name, id=a_id, avg=avg, var=var, safety_stock=safety_stock, initial_stock=initial_stock,
                                        max_inventory=max_inventory, reorder_history_size=reorder_history_size, precedence=precedence)
           



            #add to supply chain != da lista de atores
            self.Object_supply_chain.add_to_supply_chain(a_id)
            logs.log(debug_msg="actor "+str(a_id)+"Added to supply chain")


        logs.log(debug_msg="All Actors created")
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
        elif status == 2:
            self.simulation_status="2-Prepating Simulation"
        elif status == 3:
            self.simulation_status="3-Running Simulation"    
        elif status == 99:
            self.simulation_status="99-Simulation ended"            
        self.record_simulation_status(status)

    def record_simulation_status(self,simulation_status):
        logs.log(debug_msg="The simulation status changed to "+str(simulation_status))