import inspect
from random import random
from . import actors, orders_records, inventory, supply_chain as sc, logging_management as logs, transactions as tns
from . import database
import datetime, yaml, time, pandas as pd, simulation_configuration as sim_cfg, json

# from dashboard import dashboard_data as ds

# from simulation_configuration import *

logs.log(debug_msg="Started simulation.py")


## check if testes are configurated to run

class ClassSimulation:
    def __init__(self, stock_management_mode):
        self.stock_management_mode = stock_management_mode   # Modos | traditional = 1 | blockchain = 2  | Machine learnning = 3
        self.simulation_status = "0-Created"
        self.simulation_id=time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        self.time=1
        self.simulation_stats={
                    "orders_opened":0,
                    "orders_closed":0,
                    "transactions_opened":0,
                    "transactions_delivered":0,
                    "days_passed":0}
        
        self.simulation_stats_exported={}

        self.order_priority = "faster"  # prioridades: fifo, faster
        #create mongodb

        self.inventory_history = []

        # Lista que guarda todos os objectos atores
        self.actors_collection=[]

        self.global_inventory={}
        #DashBoard
        # self.dashboard = ds.dashboard_data(self)

        self.cookbook = {}

        if sim_cfg.DB_TYPE == 1:
            self.mongo_db = database.MongoDB(self, drop_history=True)
        elif sim_cfg.DB_TYPE == 2:
            self.mongo_db = database.local_db(self, drop_history=True)

        # self.blockchain= blockchian.blockchain(self)
        #create supply chain
        self.Object_supply_chain=sc.ClassSupplyChain(self)
        
        logs.new_log(file="simulation", function="construction", actor=0, debug_msg=" Supply Chain  "+str( self.Object_supply_chain.supply_chain_structure))
        self.ObejctTransationsRecords = tns.transactionsClass(self)


        self.mongo_db.create_db_stats_document(self.simulation_id)

        logs.log(debug_msg="| status           | Simulation created")

        self.sleep_time = 0



    #Import Configurations
    # Esta função vai buscar a lista dos atores ao ficheiro de configuração
    # trata-se apenas de uma lista dos atores presentes na configuração, sem ordem definida


    def update_inventory_history(self):
        for actor in self.actors_collection:
            record = {"day": self.time,
                      "actor"  : actor.id,
                      "data": actor.get_actor_inventory()}
            self.inventory_history.append(record)
        

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

    def create_actors(self, ACTORS_CONFIG_FILE):
        configs_dict=self.get_actors_configurations(ACTORS_CONFIG_FILE)

        #ADD  the final customer ###

        configs_dict[0] = {'id': 0, 'max_inventory': 9999999999999999999, 'name': 'Customer', 'products': [] ,  "time_average":0, "time_deviation":0, "safety_factor": 1, "reorder_history_size":0}
        actors_list=(configs_dict.keys())


        for actor_id in actors_list:
            logs.new_log(file="simulation", function="create_actors", actor=actor_id,day=0,  debug_msg= self.get_actor_parameters(configs_dict, actor_id))

            name, a_id, avg, var, max_inventory, products, safety_factor, reorder_history_size = self.get_actor_parameters(configs_dict, actor_id)

            #Cria o ator
            actor_object = actors.actor(self, name=name, id=a_id, avg=avg, var=var,
                                        max_inventory=max_inventory, products=products,
                                        safety_factor=safety_factor, reorder_history_size=reorder_history_size)

            #add to supply chain != da lista de atores
            self.Object_supply_chain.add_to_supply_chain(a_id)
            logs.new_log(state=" ", file="simulation", function="get_actors_configurations", actor=actor_id, debug_msg="Object_supply_chain add_to_supply_chain actor "+str(a_id)+" Added to supply chain   |SC:"+str(self.Object_supply_chain.get_supply_chain()))


            self.add_to_actors_collection(actor_object)
        self.mongo_db.add_actors_to_db_stats(tuple(actors_list))
        return actors_list

    def get_actor_delivery_stats(self, actor_id):
        # devolve os valres default
        for actor in self.actors_collection:
            if actor.id == int(actor_id):
                return {"average_time": actor.average_time, "deviation_time" : actor.deviation_time}
                
        
        return self.get_actor_by_id(actor_id).get_actor_default_parameters()


    def get_actor_parameters(self,configs_dict,actor):
        name                 = configs_dict[actor]["name"]
        id                   = configs_dict[actor]["id"]
        avg                  = configs_dict[actor]["time_average"]
        var                  = configs_dict[actor]["time_deviation"]
        max_inventory        = configs_dict[actor]["max_inventory"]
        products             = configs_dict[actor]["products"]
        safety_factor        = configs_dict[actor]["safety_factor"]
        reorder_history_size = configs_dict[actor]["reorder_history_size"]
        return name, id, avg, var, max_inventory, products, safety_factor, reorder_history_size

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


    def show_simulation_stats(self):
        print("           Simulation Stats")
        print(" ------------------------------------------------")
        for key, value in self.simulation_stats.items():
            print("          ",key,":",value)
        
        print(" ------------------------------------------------")
        for key, value in self.simulation_stats_exported.items():
            print("          ",key,":",value)
        print(" ------------------------------------------------")
        self.check_final_stats_integrity()

    def reset_all_actors_status(self):
        for actor in self.actors_collection:
            actor.actor_state = 0

    def speed(self):
        time.sleep(self.sleep_time)



    #---------------------------------------------------------------------------------------------------------------------Dashboard
    def update_global_inventory(self, actor_id, product, qty):
        logs.log()
        logs.new_log(state=" ", file="actors", function="update_global_inventory", actor=actor_id, debug_msg="| Refresh Inventory| Simulation    | Updating Global Inventory  actor {} product {} qty{} inventory:{}".format( actor_id, product, qty,self.global_inventory) )

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
                raise Exception("Erro no update global inventory")


            with open(sim_cfg.INVENTORY_FILE, 'w') as file:
                json.dump(inventory_dict, file)

            # print("inventory",inventory)
            self.global_inventory = inventory_dict


            return True
        except:
            raise Exception("Erro no update global inventory")

    def update_simulation_stats(self, stat):
        # esta função serve para validar os resultados finais da simulação. doble check dos numeros

        self.simulation_stats[stat] = int( self.simulation_stats[stat] ) + 1
        data=dict(self.simulation_stats)
        self.mongo_db.add_to_db_stats_log(stat_value= data)


    def check_final_stats_integrity(self):
        orders_integrity = self.simulation_stats_exported["orders_exported"] == self.simulation_stats["orders_opened"] + self.simulation_stats["orders_closed"]
        print("           orders_integrity:      ",orders_integrity,"Δ", self.simulation_stats_exported["orders_exported"] - self.simulation_stats["orders_opened"] - self.simulation_stats["orders_closed"] )

        transactions_integrity = self.simulation_stats_exported["transactions_exported"] == self.simulation_stats["transactions_opened"] + self.simulation_stats["transactions_delivered"]
        print("           transactions_integrity:",transactions_integrity, "Δ", self.simulation_stats["transactions_opened"] + self.simulation_stats["transactions_delivered"] - self.simulation_stats_exported["transactions_exported"]  )
        
        
    def save_simulation_stats(self):
        data=dict(self.simulation_stats)

        with open(sim_cfg.SIM_STATUS_FILE_PATH, 'w') as file:
            json.dump(data, file)

    def export_db(self,export_directory):
        self.mongo_db.export_db(export_directory)

    def validate_data_compatibilty(self, input_data, actors_config):
        #check if any order is bigger than safety stock
        max_input = max(input_data)

        configs = self.get_actors_configurations(actors_configuration=actors_config)


        for s in configs.values():
            for p in s["products"]:
                safety_stock = p["safety_stock"]
                if safety_stock < max_input:
                    print((f"Safety stock is smaller than order quantity \n -> increase safety stock \n -> max input: {max_input}  safety stock: {safety_stock}"))
                    # raise Exception(f"Safety stock is smaller than order quantity \n -> increase safety stock \n -> max input: {max_input}  safety stock: {safety_stock}")
        return True
