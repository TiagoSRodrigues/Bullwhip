import inspect
from . import actors, orders_records, inventory, supply_chain as sc, logging_management as logs, transactions as tns
from . import database
import datetime, yaml, time, pandas as pd, simulation_configuration as sim_cfg, json

# from dashboard import dashboard_data as ds

# from simulation_configuration import *
 
logs.log(debug_msg="Started simulation.py")


## check if testes are configurated to run

class ClassSimulation:
    def __init__(self):
        self.simulation_status = "0-Created"
        self.simulation_id=time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        self.time=1
        self.simulation_stats={
                    "orders_opened":0,
                    "orders_closed":0,
                    "transactions_opened":0,
                    "transactions_delivered":0,
                    "days_passed":0}

        self.order_priority = "first"  # prioridades: fifo, first
        #create mongodb
        self.mongo_db = database.MongoDB(self)

        #create supply chain
        self.Object_supply_chain=sc.ClassSupplyChain(self)
        logs.log(debug_msg="| CREATED OBJECT   | Supply Chain  "+str( self.Object_supply_chain))

        self.ObejctTransationsRecords = tns.transactionsClass(self)

        # Lista que guarda todos os objectos atores 
        self.actors_collection=[]

        self.global_inventory={}
        #DashBoard
        # self.dashboard = ds.dashboard_data(self)

        self.cookbook = {}
        
        
        
        self.mongo_db.create_db_stats_document(self.simulation_id)

        logs.log(debug_msg="| status           | Simulation created")

        # try:
        #     self.sleep_time = float( input( " Insert delay time:") )
        # except:
        #     self.sleep_time = 0

        
    #Import Configurations
    # Esta função vai buscar a lista dos atores ao ficheiro de configuração
    # trata-se apenas de uma lista dos atores presentes na configuração, sem ordem definida
    #  
    def add_to_actors_collection(self, actor):
        self.actors_collection.append(actor)

    def get_actors_collection(self):
        return self.actors_collection


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
        
        configs_dict[0] = {'id': 0, 'max_inventory': 999999999, 'name': 'Customer', 'products': [] ,  "time_average":0, "time_variance":0}                   
        actors_list=(configs_dict.keys())


        for actor_id in actors_list:
            logs.log(debug_msg= self.get_actor_parameters(configs_dict, actor_id))
            name, a_id, avg, var, max_inventory, products = self.get_actor_parameters(configs_dict, actor_id)
            
            #Cria o ator
            actor_object = actors.actor(self, name=name, id=a_id, avg=avg, var=var, 
                                        max_inventory=max_inventory, products=products)
 
            #add to supply chain != da lista de atores
            self.Object_supply_chain.add_to_supply_chain(a_id)
            logs.log(debug_msg="| FUNCTION         | Object_supply_chain.add_to_supply_chain actor "+str(a_id)+" Added to supply chain   |SC:"+str(self.Object_supply_chain.get_supply_chain()))

            self.add_to_actors_collection(actor_object)
        self.mongo_db.add_actors_to_db_stats(tuple(actors_list))
        return actors_list

    def get_actor_parameters(self,configs_dict,actor):
        name                 = configs_dict[actor]["name"]
        id                   = configs_dict[actor]["id"]
        avg                  = configs_dict[actor]["time_average"]
        var                  = configs_dict[actor]["time_variance"]
        max_inventory        = configs_dict[actor]["max_inventory"]
        products             = configs_dict[actor]["products"]

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

    def get_actor_by_id(self, actor_id):
        for actor in self.actors_collection:
            if actor.id == actor_id:
                return actor
        return False

    def reset_all_actors_status(self):
        for actor in self.actors_collection:
            actor.actor_state = 0

    def speed(self):
        time.sleep(self.sleep_time)

    #---------------------------------------------------------------------------------------------------------------------Dashboard
    def update_global_inventory(self, actor_id, product, qty):
        logs.log(debug_msg="| Refresh Inventory| Simulation    | Updating Global Inventory  actor {} product {} qty{} inventory:{}".format( actor_id, product, qty,self.global_inventory))
        try:
            inventory_dict = self.global_inventory
            actor_id, product_id, quantity  = int(actor_id), int(product), int(qty)
            try:
                self.mongo_db.update_inventory_db(actor_id, product_id, quantity)
            except:
                raise Exception("Erro a atualizar inventário no mongodb")
            
            try:
                # print("STEP  1",actor_id, product_id, "|",inventory)
                # N existe ator nem produto
                if actor_id not in inventory_dict:
                    # print("STEP  2")
                    prd= [{product_id:quantity}]
                    inventory_dict[actor_id] = prd
                
                    
                #Existe ator mas n produto
                elif (actor_id in inventory_dict) and (product_id not in inventory_dict[actor_id]):
                    # print("STEP  3")
                    
                    # print("produtct {} not in enventoty {}".format(product_id,  inventory[actor_id] ))
                    inventory_dict[actor_id].append( {product_id:quantity} )
                    
                    
                #Existe ator e produto
                elif (actor_id in inventory_dict ) and (product_id in inventory_dict[actor_id]):
                    # print("STEP  4")
                    for prod in inventory_dict[actor_id]:
                    
                        if prod == product_id:
                            # print("\n\n\n CONA\n  ",inventory[actor_id][prod],"->",quantity)
                            inventory_dict[actor_id][prod] = quantity
            except:
                print("erro no update global inventory")        


            with open(sim_cfg.inventory_file, 'w') as file:
                json.dump(inventory_dict, file)

            # print("inventory",inventory)
            self.global_inventory = inventory_dict
            
            logs.log(debug_msg="| Refreshed Inventory| Simulation    | Updating Global Inventory :{}".format(inventory))
            return True
        except:
            raise Exception("Erro no update global inventory")
        
    def update_simulation_stats(self, stat):
     
        self.simulation_stats[stat] = int( self.simulation_stats[stat] ) + 1
        
        data=dict(self.simulation_stats)
        
        self.mongo_db.add_to_db_stats_log(stat_value= data)
        
            # with open(sim_cfg.simulation_status_file, 'a') as file:
            #     file.write("\n" +str(self.simulation_stats)+"," )
        