import json
from simulator import data_input
from.import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init
import time
from . import final_stats
from . import easter_eggs  as ee

def get_first_active_actor(simulation):
    first_sc_element_id=simulation.Object_supply_chain.get_supply_chain()[0]


    for actor in simulation.actors_collection:
        if actor.id == first_sc_element_id:
            return actor

def main(input_data, simulation):
    logs.new_log(day=simulation.time, actor=" ", function="main", file="main", 
                 debug_msg= "simulation started <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>") 

    first_element = get_first_active_actor(simulation)
    ee.print_days(len(input_data))

    simulation.speed()  ## SPEED

    for quantity in input_data:
        logs.new_log(day=simulation.time, actor=" ", function="main", file="main", 
                    debug_msg= "new day <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>") 


        logs.new_log(day=simulation.time, actor=" ", function="main", file="main", debug_msg= f"global inventory | simulation    | global inventory{simulation.global_inventory}")
        logs.new_log(day=simulation.time, actor=" ", function="main", file="main", debug_msg= f"global inventory | simulation    | open transctions{simulation.ObejctTransationsRecords.open_transactions}")


        simulation.update_inventory_history()
        if simulation.time == 100:
            with open("inventary_log.json", "w") as file:
                json.dump(simulation.inventory_history, file, indent=4)    
                
                #file.write(str(simulation.inventory_history).replace("'", '"'))
            # print(simulation.inventory_history)
        
        simulation.reset_all_actors_status()
        # simulation.mongo_db.add_to_inventory_snapshot()

        simulation.ObejctTransationsRecords.check_transactions_integrity()
        simulation.ObejctTransationsRecords.deliver_to_final_client()
        logs.print_day(simulation, quantity=quantity)

        #apagar logs.new_log(day=simulation.time, actor=" ", function="main", file="main",info_msg="|")
        #apagar logs.new_log(day=simulation.time, actor=" ", function="main", file="main",info_msg="|      Day "+str(simulation.time) )
        #apagar logs.new_log(day=simulation.time, actor=" ", function="main", file="main",info_msg="|")

        first_element.receive_order(supplier=int(first_element.id), quantity = int(quantity), product=1001, client = 0  )

        for actor in simulation.actors_collection:
            #apagar logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main",  info_msg = f"|      Actor  {actor}" )
            #apagar logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", info_msg="|")


            logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= f"open orders{actor.actor_orders_record.open_orders_record[0:]} < open ")
            logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= f"closed orders{actor.actor_orders_record.closed_orders_record} < closed ")
            logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= f"orders_history{actor.actor_orders_record.orders_history} < hist")
            logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= f"orders_waiting_stock{actor.actor_orders_record.orders_waiting_stock} wait")

            simulation.speed() ## SPEED
            if not actor.id==0:

                    logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= f"present stock {actor.actor_inventory.main_inventory} ")
                    
                    simulation.mongo_db.add_to_inventory_history(actor_id=actor.id, inventory=actor.actor_inventory.main_inventory, day=simulation.time)


                    logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= "starting management ")
                    if not actor.manage_orders():
                        raise Exception("Error in actor orders management")

                    logs.new_log(actor=actor.id, day=simulation.time, function="main", file="main", debug_msg= "starting sock management ")
                    if not actor.manage_stock():
                        raise Exception("Error in actor stock management")
                        
            #apagar print( actor.id, actor.actor_inventory.main_inventory, "yap")

        simulation.time += 1
        simulation.update_simulation_stats("days_passed")
  


    simulation.mongo_db.add_maney_to_db(colection_name="final_open_transactions", data=  simulation.ObejctTransationsRecords.open_transactions)
    simulation.mongo_db.add_maney_to_db(colection_name="final_closed_transactions", data=  simulation.ObejctTransationsRecords.delivered_transactions)
    # print("<<< inventories >>>")
    # for actor in simulation.actors_collection:
    #     print( actor.id, actor.actor_inventory.main_inventory)

    # print("<<< open Orders >>>")
    # for actor in simulation.actors_collection:
    #     print( actor.id, actor.actor_orders_record.open_orders_record)

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
