from.import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init
import time
from . import final_stats
def main(input_data, simulation):
    logs.log(info_msg="| FUNCTION         | main.main")
    


    first_element = get_first_active_actor(simulation)
    simulation.speed()  ## SPEED

    for quantity in input_data:



        simulation.ObejctTransationsRecords.deliver_to_final_client()
        logs.print_day(simulation, quantity=quantity)
        

        logs.log(debug_msg=        logs.log(debug_msg="| global inventory | simulation    | global inventory {}".format( simulation.global_inventory)))
        


        simulation.reset_all_actors_status()
        logs.log(info_msg="day "+str(simulation.time) +"\n")

        first_element.receive_order(supplier=int(first_element.id), quantity = int(quantity), product=1001, client = 0  )

        for actor in simulation.actors_collection:
            
            #print("Ator ativo:", actor.id)
            logs.log(debug_msg=        logs.log(debug_msg="| Started actor    | - - - - - - - | actor: {}".format( actor.id)))
            
            simulation.speed() ## SPEED
            if not actor.is_customer:
                
                
                logs.log(debug_msg=        logs.log(debug_msg= "| before mng orders| main          |  actor: {}".format(actor.id)))
                actor.manage_orders()

                logs.log(debug_msg=        logs.log(debug_msg= "| before mng stock | main          |  actor: {}".format(actor.id)))
                actor.manage_stock()

            #print( actor.id, actor.actor_inventory.main_inventory, "yap")
        simulation.time += 1
        simulation.update_simulation_stats("days_passed")
    
        
        
        
        
        
    # print("<<< inventories >>>")
    # for actor in simulation.actors_collection:
    #     print( actor.id, actor.actor_inventory.main_inventory)
    
    # print("<<< open Orders >>>")
    # for actor in simulation.actors_collection:
    #     print( actor.id, actor.actor_orders_record.Open_Orders_Record)

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
    

def get_first_active_actor(simulation):
    first_sc_element_id=simulation.Object_supply_chain.get_supply_chain()[0]
    
    # print("suply chain",simulation.Object_supply_chain.get_supply_chain())
    
    for actor in simulation.actors_collection:
        if actor.id == first_sc_element_id:
            # print("44 actor name",actor.actor_inventory.show_present_composition())
            return actor
   

