from . import  orders_records, inventory, logging_management as logs
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
        
        if self.id == 0: self.is_customer = True
        else: self.is_customer = False
         
        #VARIAVEL TEMPORARIA PARA PROVA DE CONCEITO:
        self.reorder_quantity=25


        ### Variable Properties  ######
        self.actor_state="0"  #states 0 = idle  1=busy
        
        #Cria o Registo de encomendas
        self.actor_stock_record = orders_records.ClassOrdersRecord(self)
            
        #Cria os inventários                                  
        self.actor_inventory = inventory.ClassInventory( actor = self ,
                                                    max_capacity = max_inventory,
                                                    products=products)
        
        self.products_list = self.get_actor_product_list()

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

    def get_actor_product_list(self):
        logs.log(debug_msg="[Function] actors.get_actors_product_list"+str(self))

        products_list=[]
        for product in self.products:
            products_list.append( product["id"] )
        return products_list

    def receive_order(self, quantity, product, client ):
        logs.log(debug_msg = "[Ordered recived] actor "+str(self.id)+" received order from actor: "+ str(client) + " of "+ str(quantity) + " of the product " + str(product) )
        self.actor_state = 1

        self.actor_stock_record.add_to_open_orders( product , quantity , client )

        self.actor_state = 0
        self.manage_stock()
        #AQUI adicionar as variaveis para a order
 
    def manage_stock(self):
        # logs.log(debug_msg="[Function] actors.manage_stock  actor id: "+str(self.id))
        logs.log(debug_msg="[Function] actors.manage_stock  actor id: "+str(self.id)+"em stock:"+str(self.actor_inventory.main_inventory))



        orders          =   self.actor_stock_record.Open_Orders_Record
        max_capacity    =   self.actor_inventory.max_capacity
        intentory       =   self.actor_inventory.main_inventory
        
        # print(self.name," ",self.actor_inventory.main_inventory)
        # verifica se tem encomendas para receber
        to_receive = self.simulation.ObejctTransationsRecords.get_todays_transactions(self)

        logs.log(debug_msg="[Function] actors.manage_stock  Encomendas para receber: "+str(to_receive))
       
        #recebe encomendas
        if len(to_receive)>0:
            for transaction_id in to_receive:
                self.receive_transaction( transaction_id)


            
        # verifica se tem encomendas para enviar
        to_send = self.get_orders_pending()
        logs.log(debug_msg="[Function] actors.manage_stock  Encomendas para enviar: "+str(to_send))

        if len(to_send)>0:
            logs.log(debug_msg="[FUNCION] actores.manage_stock IF has "+ str(len(to_send))+" orders to send: " +str(to_send) )
            for order in to_send:
                self.send_transactions(order)
                

        # Verifica se tem stock para repor
        for product in self.products_list:
            logs.log(debug_msg="[FUNCION] actores.manage_stock for product , "+str(product)+" ,in products list")
            # print("debugging product",product)
           
            if int( self.get_product_inventory(product ) ) <= int(self.get_product_safety_inventory(product ) ):
                
                #verifica se pode produzir:
                print("debugging product pode produzir?",product)

                if self.manufacture_product( product):
                    print("BAHJHHHAAAAAAAAAAAAAAAAAAAA")
                else: 
                
                    #se tiver prepara encomenda
                    logs.log(debug_msg="[FUNCION] actores.manage_stock IF, produto" +str(product)+ "sem stock")
                    
                    #vai buscar a composição
                    composition =  self.get_product_composition( product )

                    #encomenda o necessário
                    
                    for key , value in composition.items():
                        if  key[0] == self.id:
                            break   
                        print("\n\n debugging",composition)
                        product_id_to_order=key
                        actor_to_order = key[0]
                        print("XXXXX actor_to_order=",key[0])
                        quantity_to_order = self.reorder_quantity * value

                        #todo
                        #ISTO N ESTA A FUNCIONAR
                        self.place_order(actor_id = actor_to_order, product=product_id_to_order,quantity=quantity_to_order)
        
        self.actor_state = 0
        return True

    def send_transactions(self, order):
        logs.log(debug_msg="[FUNCION] actores.send_transactions  order: "+str(order)+" self= "+str(self.name) )

        day= self.simulation.time

        product              = order[1]
        ordered_quantity     = order[2]
        stock_quantity       = self.get_product_inventory(product) # verifica stock
        try:
            if int(stock_quantity) > int(ordered_quantity) :
                logs.log(debug_msg="[FUNCION] actores.manage_stock IF stock_quantity > ordered_quantity")
            
                
                client       = order[3]
                order_id     = order[-2]
                order_status = order[-1]
        
            
                # remove o enviado do inventário  
                self.actor_inventory.remove_from_inventory(product, ordered_quantity)

                #envia encomendas 
                self.simulation.ObejctTransationsRecords.add_transaction( sender= self.id, receiver = client, quantity = ordered_quantity, product = product, deliver_date = day + self.average_time, sending_date = day)

                #changes status to sended
                order[-1] = 1    #   SE N FUNCIONAR USAR ISTO -> self.actor_stock_record.set_order_status( order_id, status = 1) 

                #remove from open orders
                self.actor_stock_record.remove_from_open_orders(order_id )

                logs.log(debug_msg="[FUNCION] actors.send_transactions order id:"+str(order_id))

        except:
            logs.log(debug_msg="[FUNCION] Error on actores.manage_stock IF stock_quantity > ordered_quantity    actor:"+ str(self.id)+' order:'+str(order)+'   stock_quantity'+str(stock_quantity)+'  ordered_quantity:'+str(ordered_quantity))
            raise     

    def receive_transaction(self, transaction_id):
        transaction = self.simulation.ObejctTransationsRecords.get_transaction_by_id(transaction_id)
               
        product              = transaction["product"]
        ordered_quantity     = transaction["quantity"]
        inventory_capacity   = self.actor_inventory.refresh_inventory_capacity()
        
        print( inventory_capacity , ordered_quantity)

        #verifica capacidade
        if int(inventory_capacity) + int(ordered_quantity) >= int(self.max_inventory): 
            print("Invendory overcapacity of actor ",self.name)
            return False

        #adiciona ao inventário
        self.add_to_inventory(self, product, ordered_quantity)

        # regista que recebeu
        self.ObejctTransationsRecords.record_delivered(transaction_id)
        
        #verifica se tem de produzir algo:
        
        #todo verifica se pode produzir algo
        
        
        logs.log(debug_msg="[FUNCION] actores.manage_stock IF stock_quantity > ordered_quantity")



    def get_product_composition(self, product_id):
        for product in self.products:
            if product["id"]==product_id:
                return product["Composition"]

    def place_order(self, actor_id, product, quantity):
      
        logs.log(debug_msg="[Function] actors.place_order"+str( self)+str(actor_id)+str(product) +str(quantity))

        for actor_to_order in self.simulation.actors_collection: 
         
            if actor_to_order.id == int(actor_id):
                actor_to_order.receive_order( quantity=quantity, product=product, client= self.id )


    def get_orders_pending(self):
        logs.log(debug_msg="[Function] actors.get_orders_pending"+str( self))
        pending=[]

        for record in self.actor_stock_record.Open_Orders_Record:
            if record[-1] == 0:
                pending.append(record)
        return pending

    def get_product_inventory(self,product):
        # logs.log(debug_msg="[Function] actors.get_product_inventory"+str( self)+str(product))
        return self.actor_inventory.get_product_inventory(product)

    def get_product_safety_inventory(self,product):
        # logs.log(debug_msg="[Function] actors.get_product_safety_inventory "+str( self)+str(product))
        return self.actor_inventory.get_product_safety_inventory(product)



    def manufacture_product(self, product):
        logs.log(debug_msg="[Function] manufacture_product actor:"+str( self.name) + " product " +str(product) )
        
        def get_max_production(matrix):
            min = matrix[0][-1]
            id=0

            for el in matrix:
                if el[-1] < min:
                    min=el[-1]
                    id=el[0]
            return min , id

        composition =  self.get_product_composition( product )
        production_matrix=[]

        logs.log(debug_msg="[Function] manufacture_product actor:"+str( self.name) + " product " +str(product) + "composition: "+str(composition) )

        for raw_material_id in composition:
            print("raw_material_id",raw_material_id)
            
            in_stock = int(self.get_product_inventory(raw_material_id))
            
            production_matrix.append(
                # product id,                   #ratio
                [raw_material_id ,  in_stock  // int(composition[raw_material_id])    ])
        logs.log(debug_msg="[Function] actors.manufacture_product production_matrix "+str( production_matrix))


        max_prod=get_max_production(production_matrix)[0]

        if not isinstance(max_prod,int): raise "Manuracture_error"
        if max_prod == 0: return False

        self.production(product, quantity=max_prod)
    
        return True

        print("temos de produzir",max_prod," o reagente limitante é ",get_max_production(production_matrix)[0])
        
    def production(self, product, quantity, composition):
        print("in production:",self.id,  product, quantity, composition)
        
        #get recepe
        
        # remove raw material from inventory
        pass
        # self.actor_inventory.remove_from_inventory(product, quantity)

        # add new to inventory

        # raise "NICE"



