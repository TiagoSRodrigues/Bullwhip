from.import logging_management as logs
# Funções para correr a simulação, o pré simulação fica no init
import time

def main(input_data, simulation):
    logs.log(info_msg="| FUNCTION         | main.main")
    
    first_element = get_first_active_actor(simulation)
    simulation.speed()  ## SPEED

    print("cookbook",simulation.cookbook)
    for quantity in input_data:
        print("day ",simulation.time, "quantity ",quantity)

        


        simulation.reset_all_actors_status()
        logs.log(info_msg="day "+str(simulation.time) +"\n")

        # print(            first_element.actor_inventory.show_present_composition() )
        first_element.receive_order(supplier=first_element.id, quantity = quantity, product=1001, client = 0  )

        for actor in simulation.actors_collection:
            time.sleep(.05) ## SPEED

            if not actor.is_customer:

                # print(actor.actor_inventory.show_present_composition())
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
            print("44 actor name",actor.actor_inventory.show_present_composition())
            return actor
   




# print(simulation.actors_collection[0].name)
"""    try: 
        logs.show_object_attributes(logs.show_object_attributes(simulation))
    except:
        print("Nop")
        logs.show_object_attributes(simulation)
        """