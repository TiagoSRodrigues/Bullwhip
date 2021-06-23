import  orders_records, inventory, simulation ,logging_management as logs
import numpy as np
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################
class actor:
    def __init__(self , simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int, reorder_history_size:int,
        products:dict, state=None):
        
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
        self.state="0"  #states 0 = idle  1=busy
        
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
        return self.state
    
    def get_actors_product_list(self):
        products_list=[]
        for product in self.products:
            products_list.append( self.products[0]["id"])
        return products_list

    def receive_order(self, quantity, product, client ):
        logs.log(debug_msg = "[Ordered recived] from:"+ str(self.id) + "received an order of "+ str(quantity) + "of the product" + str(product) )
        self.state = 1

        self.actor_stock_record.add_to_orders_record(self.simulation.time , product , quantity , client )

        self.state = 0
        self.manage_stock()
        #AQUI adicionar as variaveis para a order
 
    def manage_stock(self):
        day= self.simulation.time

        orders          =   self.actor_stock_record.OrdersRecord
        max_capacity    =   self.actor_inventory.max_capacity
        intentory    =   self.actor_inventory.main_inventory
        


        # verifica se tem encomendas para receber
        to_receive = self.simulation.ObejctTransationsRecords.get_todays_transactions(self)
        if len(to_receive)>0:
            pass
            # todo add to invendory
            
        # verifica se tem encomendas para enviar
        to_send = self.get_orders_pending()
        print(len(to_send), to_send)
        
        if len(to_send)>0:
            for order in to_send:
                product              = order[1]
                ordered_quantity     = order[2]
                stock_quantity       = self.get_product_inventory(product) # verifica stock
                if stock_quantity >ordered_quantity :
                    client       = order[3]
                    order_id     = order[-2]
                    order_status = order[-1]
            
                    #envia encomendas
                    self.simulation.ObejctTransationsRecords.add_transaction(self.id, client, ordered_quantity, product, day+ self.average_time, day)
                    # remove o enviado do inventário
                    self.actor_inventory.remove_from_inventory(product, ordered_quantity)
                    #changes status to sended
                    self.actor_stock_record.set_order_status( order_id, status = 1) 
        
        
        # Verifica se tem encomendas para encomendar
        for product in self.products_list:
            if self.get_product_inventory(product) <= self.get_product_safety_inventory(product):
                pass


            
    def place_order(self, actor, product, quantity):
        pass


    def get_orders_pending(self):
        pending=[]
        print(self.actor_stock_record.OrdersRecord)
        for record in self.actor_stock_record.OrdersRecord:
            if record[-1] == 0:
                pending.append(record)
        return pending

    def get_product_inventory(self,product):
        return self.actor_inventory.get_product_inventory(product)

    def get_product_safety_inventory(self,product):
        return self.actor_inventory.get_product_safety_inventory(product)




