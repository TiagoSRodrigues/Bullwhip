from.import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init
import time

def main(input_data, simulation):
    logs.log(info_msg="| FUNCTION         | main.main")
    
    first_element = get_first_active_actor(simulation)
    simulation.speed()  ## SPEED

    for quantity in input_data:
        if quantity == 0: 
            simulation.time += 1
            continue

        simulation.ObejctTransationsRecords.deliver_to_final_client()
        print("day ",simulation.time, "quantity ",quantity)

        logs.log(debug_msg=        logs.log(debug_msg="| global inventory | simulation    | global inventory {}".format( simulation.global_inventory)))
        


        simulation.reset_all_actors_status()
        logs.log(info_msg="day "+str(simulation.time) +"\n")

        first_element.receive_order(supplier=int(first_element.id), quantity = int(quantity), product=1001, client = 0  )

        for actor in simulation.actors_collection:
            logs.log(debug_msg=        logs.log(debug_msg="| Started actor    | - - - - - - - | actor: {}".format( actor.id)))

            simulation.speed() ## SPEED
            if not actor.is_customer:
                # print(actor.actor_inventory.show_present_composition())

                
                logs.log(debug_msg=        logs.log(debug_msg="| before mng orders| main          |  actor: {}".format(actor.id)))
                actor.manage_orders()

                logs.log(debug_msg=        logs.log(debug_msg="| before mng stock | main          |  actor: {}".format(actor.id)))
                actor.manage_stock()


        
        simulation.time += 1
        

    ########### Start orders
    simulation.record_simulation_status(simulation_status=3)
    

def get_first_active_actor(simulation):
    first_sc_element_id=simulation.Object_supply_chain.get_supply_chain()[0]
    
    print("suply chain",simulation.Object_supply_chain.get_supply_chain())   
    
    for actor in simulation.actors_collection:
        print(actor.name, actor.id)
        if actor.id == first_sc_element_id:
            # print("44 actor name",actor.actor_inventory.show_present_composition())
            return actor
   




# print(simulation.actors_collection[0].name)
"""    try: 
        logs.show_object_attributes(logs.show_object_attributes(simulation))
    except:
        print("Nop")
        logs.show_object_attributes(simulation)
        """