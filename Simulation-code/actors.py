import  orders_records, inventory, simulation ,logging_management as logs
import numpy as np
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################
class actor:
    def __init__(self , simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int, reorder_history_size:int,
        products:dict):
        
        ### Constants Properties  ###
        self.id                   = id
        self.name                 = name
        self.average_time         = avg
        self.variation_time       = var
        self.max_inventory        = max_inventory
        self.reorder_history_size = reorder_history_size # nr of days to consider to reeorder
        self.products             = products
        self.simulation           = simulation_object
         
        ### Variable Properties  ######
        self.actor_state="0"  #states 0 = idle  1=busy
        
        #Cria o Registo de encomendas
        self.actor_stock_record = orders_records.ClassOrdersRecord(self.id)
            
        #Cria os inventários                                   #   ↓ Produt is forced to 1   !  this is commented becouse is the crations
        self.actor_inventory = inventory.ClassInventory( actor = name , #product = 1,
                                                    max_capacity = max_inventory,
                                                    products=products)
        
        self.products_list = self.get_actors_product_list()


        logs.log(info_msg="[Created Object] Actor         id="+str(self.id)+" "+self.name)


        #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação
        simulation_object.actors_collection.append(self)

        #logs
        try:
            logs.log(debug_msg = "ACTORS    Created actor: "+str(self.id)+" " + str(self.name) + " AVG: "+ str(self.average_time) + " VAR: "+ str(self.variation_time) + 
                " max_inventory " + str(self.max_inventory) + " reorder_history_size " + str(self.reorder_history_size) +
                " Products " + str(self.products) )
        except:
            logs.log(debug_msg = "Error in Actors logging")


#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

    def get_state(self):
        return self.actor_state

    def set_actor_free(self):
        self.actor_state=0

    def set_actor_busy(self):
        self.actor_state=1

    def get_actors_product_list(self):
        logs.log(debug_msg="[Function] actors.get_actors_product_list"+str(self))

        products_list=[]
        for product in self.products:
            products_list.append( self.products[0]["id"])
        return products_list

    def receive_order(self, quantity, product, client ):
        logs.log(debug_msg = "[Ordered recived] from:"+ str(self.id) + "received an order of "+ str(quantity) + "of the product" + str(product) )
        self.actor_state = 1

        self.actor_stock_record.add_to_orders_record(self.simulation.time , product , quantity , client )

        self.actor_state = 0
        self.manage_stock()
        #AQUI adicionar as variaveis para a order
 
    def manage_stock(self):
        logs.log(debug_msg="[Function] actors.manage_stock"+str(self))

        self.actor_state = 1

        day= self.simulation.time

        orders          =   self.actor_stock_record.OrdersRecord
        max_capacity    =   self.actor_inventory.max_capacity
        intentory       =   self.actor_inventory.main_inventory
        


        # verifica se tem encomendas para receber
        to_receive = self.simulation.ObejctTransationsRecords.get_todays_transactions(self)
        if len(to_receive)>0:
            pass
            # todo add to invendory
            
        # verifica se tem encomendas para enviar
        to_send = self.get_orders_pending()
        return
        if len(to_send)>0:
            for order in to_send:
                print("Managing actor:",self.name)
                product              = order[1]
                ordered_quantity     = order[2]
                stock_quantity       = self.get_product_inventory(product) # verifica stock
                
                print("stock_quantity, ordered_quantity",stock_quantity, order )
                try:
                    if stock_quantity > ordered_quantity :
                        client       = order[3]
                        order_id     = order[-2]
                        order_status = order[-1]
                
                        # remove o enviado do inventário
                        if self.actor_inventory.remove_from_inventory(product, ordered_quantity) == False:
                            print ("error on remove_from_inventory, actors.py line 106")
                        
                        #envia encomendas
                        self.simulation.ObejctTransationsRecords.add_transaction(self.id, client, ordered_quantity, product, day+ self.average_time, day)
                        #changes status to sended
                        self.actor_stock_record.set_order_status( order_id, status = 1) 
                except:
                        print("----------------------------exeption:", type(stock_quantity),stock_quantity, type(ordered_quantity),ordered_quantity, order, "\n",self.actor_inventory.main_inventory)
                        raise Exception("cona")

        # Verifica se tem encomendas para encomendar
        for product in self.products_list:
            if self.get_product_inventory(product) <= self.get_product_safety_inventory(product):
                self.place_order(product=product, actor_id=2, quantity=100)
        
        self.actor_state = 0
    
    def place_order(self, actor_id, product, quantity):
        logs.log(debug_msg="[Function] actors.place_order"+str( self)+str(actor_id)+str(product) +str(quantity))

        for actor in self.simulation.actors_collection: 
            if actor.id == actor_id:
                actor.receive_order( quantity=quantity, product=product, client= self.id )


    def get_orders_pending(self):
        logs.log(debug_msg="[Function] actors.place_order"+str( self))
        pending=[]
        # print(self.actor_stock_record.OrdersRecord)
        for record in self.actor_stock_record.OrdersRecord:
            if record[-1] == 0:
                pending.append(record)
        return pending

    def get_product_inventory(self,product):
        logs.log(debug_msg="[Function] actors.get_product_inventory"+str( self)+str(product))

        return self.actor_inventory.get_product_inventory(product)

    def get_product_safety_inventory(self,product):
        logs.log(debug_msg="[Function] actors.get_product_safety_inventory"+str( self)+str(product))
        return self.actor_inventory.get_product_safety_inventory(product)




