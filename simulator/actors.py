from . import  orders_records, inventory, logging_management as logs
import numpy as np
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################
class actor:
    def __init__(self , simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int, 
        products:dict):
        
        ### Constants Properties  ###
        self.id                   = id
        self.name                 = name
        self.average_time         = avg
        self.variation_time       = var
        self.max_inventory        = max_inventory
        #                                                                  foi colocado no produto # self.reorder_history_size = reorder_history_size # nr of days to consider to reeorder
        self.products             = products
        self.simulation           = simulation_object
        
        if self.id == 0: self.is_customer = True
        else: self.is_customer = False
         
        # #VARIAVEL TEMPORARIA PARA PROVA DE CONCEITO:
        # self.reorder_quantity=25


        ### Variable Properties  ######
        #para prevenir loop infinito o estado vai avançando 
        self.actor_state="0"  #states 0 = idle  1=busy
        
        #Cria o Registo de encomendas
        self.actor_stock_record = orders_records.ClassOrdersRecord(self)
            
        #Cria os inventários                                  
        self.actor_inventory = inventory.ClassInventory( actor = self ,
                                                    max_capacity = max_inventory,
                                                    products=products)
        
        self.products_list = self.get_actor_product_list()

        logs.log(info_msg="| CREATED OBJECT   | Actor         id="+str(self.id)+" "+self.name)


        #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação
        simulation_object.actors_collection.append(self)

        #logs
        try:
            logs.log(debug_msg = "| OBJECT CRIATED   | ACTORS    Created actor: "+str(self.id)+" " + str(self.name) + " AVG: "+ str(self.average_time) + " VAR: "+ str(self.variation_time) + 
                " max_inventory " + str(self.max_inventory) + " Products " + str(self.products) )
        except:
            logs.log(debug_msg = "Error in Actors logging")


#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

    def get_actor_product_list(self):
        logs.log(debug_msg="| FUNCTION         | actors.get_actors_product_list"+str(self))

        products_list=[]
        for product in self.products:
            products_list.append( product["id"] )
        return products_list
    
    def set_actor_state(self, state:int, log_msg=None ):
        self.simulation.speed()
        if log_msg== None: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" |" )
        else: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" | "+str(log_msg) )
        
        self.actor_state = state

    def receive_order(self, supplier, quantity, product, client ):
        
        if int(supplier) == int(client):
            raise ValueError("Erro nos clientes - receive order",self.id , client )
        logs.log(debug_msg = "| Ordered recived  | actors        | receive_order -  actor  "+str(self.id)+" received order from actor: "+ str(client) + " of "+ str(quantity) + " of the product " + str(product) )
        

        for el_actor in self.simulation.actors_collection:
            if int(el_actor.id) == int(supplier):
                el_actor.actor_stock_record.add_to_open_orders( product , quantity , client )

        
        if self.actor_state < 20:
            self.manage_stock()
        #AQUI adicionar as variaveis para a order
 
    def manage_stock(self):

        self.set_actor_state( state = 20, log_msg="Enter Maganer Mode" )

        # logs.log(debug_msg="| FUNCTION         | actors        | manage_stock        actor id: "+str(self.id))
        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock        actor id: "+str(self.id)+" em stock:"+str(self.actor_inventory.main_inventory))

        orders          =   self.actor_stock_record.Open_Orders_Record
        max_capacity    =   self.actor_inventory.max_capacity
        intentory       =   self.actor_inventory.main_inventory
        
        # print(self.name," ",self.actor_inventory.main_inventory)
        # verifica se tem encomendas para receber
        to_receive = self.simulation.ObejctTransationsRecords.get_todays_transactions(self)

        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock        Encomendas para receber: "+str(to_receive))
       
        #recebe encomendas
        if self.actor_state == 20 and len(to_receive)>0 :
            self.set_actor_state( state=30, log_msg=str(len(to_receive))+" orders to receive" )

            for transaction_id in to_receive:
                self.receive_transaction( transaction_id)


            
        # verifica se tem encomendas para enviar
        to_send = self.get_orders_pending()
        
        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock       o actor"+str(self.id)+ " tem para enviar as encomendas: "+str(to_send))

        if self.actor_state < 40 and len(to_send) >0 :
            self.set_actor_state( state = 40, log_msg=str(len(to_send))+" orders to send")
            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock actor "+str(self.id)+" IF has "+ str(len(to_send))+" orders to send: " +str(to_send) )
            
            for order in to_send:
                self.send_transactions(order)
        
        # Verifica se tem stock para repor
        if self.actor_state < 50:
            for product in self.products_list:
                logs.log(debug_msg="| FUNCTION         | actors        | manage_stock for product , "+str(product)+" ,in products list: "+str(self.products_list))
            
                #precisa de report stock
                if int( self.get_product_inventory(product ) ) <= int(self.get_product_safety_inventory(product ) and self.actor_state < 50):
                    self.set_actor_state( state=50 )
                    logs.log(debug_msg="| FUNCTION         | actors        | product_inventory "+str(self.get_product_inventory(product ))+" <= i  get_product_safety_inventory "+str(self.get_product_safety_inventory(product ) ))

                    #verifica se pode produzir, se poder produz:
                    print("debugging product pode produzir?",product)

                    if self.manufacture_product(product):
                        self.set_actor_state( state=60)
                        print("BAHJHHHAAAAAAAAAAAAAAAAAAAA")
                    else: 
                        #se tiver de encomendar, prepara encomenda
                        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF, produto" +str(product)+ "sem stock")
                        self.set_actor_state( state=70)

                        #vai buscar a composição
                        composition =  self.get_product_composition( product )

                        #minimal_order = #
                        #encomenda o necessário
                        for key , value in composition.items():

                            self.set_actor_state( state=7*10 +  int(key[0]) )
                            if int(key[0]) == int(self.id): continue
                            # print(key, value)
                                   
                            print("\n\n debugging",composition)
                            product_id_to_order = key
                            actor_to_order = key[0]
                            
                            
                            quantity_to_order = int(self.actor_inventory.get_product_reorder_history_size(product_id=product )) * value

                            #todo
                            #ISTO N ESTA A FUNCIONAR
                            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock for key , value in composition.items, actor_to_order " +str(actor_to_order)+ " prd "+str(product_id_to_order)+" qdd "+str(quantity_to_order))

                            self.place_order(actor_supplier_id = actor_to_order, product=product_id_to_order, quantity=quantity_to_order)
        
        
    def send_transactions(self, order):
        logs.log(debug_msg="| FUNCTION         | actors        | send_transactions  order: "+str(order)+" self= "+str(self.name) )
        self.set_actor_state( state=41, log_msg="sending order "+str(order) )
        day= self.simulation.time

        product              = order[1]
        ordered_quantity     = order[2]
        stock_quantity       = self.get_product_inventory(product) # verifica stock
        logs.log(debug_msg="| FUNCTION         | actors        | send_transactions ordered:"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )
        try:
            self.set_actor_state(state=42)
            # print("p ",product , " OQ ",ordered_quantity, " SQ ",stock_quantity      )
            if int(stock_quantity) > int(ordered_quantity) :
                self.set_actor_state(state=43, log_msg="Product with stock")

                logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF stock_quantity > ordered_quantity order"+str(order)+" pruduct "+str(product))
            
                
                client       = order[3]
                order_id     = order[-2]
                order_status = order[-1]
        
                self.set_actor_state(state=44, log_msg="Removing from inventary")
                # remove o enviado do inventário  
                self.actor_inventory.remove_from_inventory(product, ordered_quantity)

                self.set_actor_state(state=45, log_msg="addint to transasctions")
                #envia encomendas 
                self.simulation.ObejctTransationsRecords.add_transaction( sender= self.id, receiver = client, quantity = ordered_quantity, product = product, deliver_date = day + self.average_time, sending_date = day)

                #send_transactions
                order[-1] = 1    #   SE N FUNCIONAR USAR ISTO -> self.actor_stock_record.set_order_status( order_id, status = 1) 
                logs.log(debug_msg="| FUNCTION         | actors        | send_transactions    >>> NÃO ESTÁ PROVADO QUE ISTO FUNCIONE<<<<")
                
                self.set_actor_state(state=46, log_msg="removing from orders")
                #remove from open orders
                self.actor_stock_record.remove_from_open_orders(order_id )

                logs.log(debug_msg="| FUNCTION         | actors        | send_transactions order id:"+str(order_id))
                self.set_actor_state(state=47, log_msg="Orders sending complete")

            else:
                logs.log(debug_msg="| FUNCTION         | actors        | send_transactions NÃO ENVIVOU PQ N TINHA STOCK  ORDERED"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )
        except:
            logs.log(debug_msg="| FUNCTION         | Error on actores.manage_stock IF stock_quantity > ordered_quantity    actor:"+ str(self.id)+' order:'+str(order)+'   stock_quantity'+str(stock_quantity)+'  ordered_quantity:'+str(ordered_quantity))
            self.set_actor_state(state=49, log_msg="Falhou a tentativa de enviou de encomendas")
            raise Exception("Falhou o envio de encomendas")    

    def receive_transaction(self, transaction_id):
        self.set_actor_state(state= 31, log_msg="Receiving transaction")
        transaction = self.simulation.ObejctTransationsRecords.get_transaction_by_id(transaction_id)
               
        product              = transaction["product"]
        ordered_quantity     = transaction["quantity"]
        inventory_capacity   = self.actor_inventory.refresh_inventory_capacity()
        
        # print( inventory_capacity , ordered_quantity)


        #verifica capacidade
        if int(inventory_capacity) + int(ordered_quantity) >= int(self.max_inventory): 
            print("Invendory overcapacity of actor ",self.name)
            self.set_actor_state(state= 33, log_msg="sem espaço para receber encomendas")

            return False

        #adiciona ao inventário
        self.add_to_inventory(self, product, ordered_quantity)

        # regista que recebeu
        self.ObejctTransationsRecords.record_delivered(transaction_id)
        
        #verifica se tem de produzir algo:
        
        #todo verifica se pode produzir algo
        
        
        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF stock_quantity > ordered_quantity")



    def get_product_composition(self, product_id):
        if product_id in  self.simulation.Object_supply_chain.get_end_of_chain_actors():
            logs.log(debug_msg="| FUNCTION         | actors.get_product_composition tentativa de ver composição de produdo de fim de SC ")
            return

        for product in self.products:
            if product["id"]==product_id:
                print("XXXXXXXXXXXXXXXXXXXXXXX COMPOSITON",product)
                return product["composition"]

    def place_order(self, actor_supplier_id, product, quantity):
      
        logs.log(debug_msg="| FUNCTION         | actors        | place_order from actor "+str( self.id)+" suplier "+str(actor_supplier_id)+"  prd "+str(product)+"  qdd " +str(quantity))

        for actor_to_order in self.simulation.actors_collection: 
         
            if int(actor_to_order.id) == int(actor_supplier_id):
                self.receive_order( supplier= actor_supplier_id, quantity=quantity, product=product, client= self.id )


    def get_orders_pending(self):
        logs.log(debug_msg="| FUNCTION         | actors        | get_orders_pending       "+str( self))
        pending=[]

        for record in self.actor_stock_record.Open_Orders_Record:
            if record[-1] == 0:
                pending.append(record)
        return pending

    def get_product_inventory(self,product):
        logs.log(debug_msg="| FUNCTION         | actors        | get_product_inventory"+str( self)+str(product))
        return self.actor_inventory.get_product_inventory(product)

    def get_product_safety_inventory(self,product):
        # logs.log(debug_msg="| FUNCTION         | actors.get_product_safety_inventory "+str( self)+str(product))
        return self.actor_inventory.get_product_safety_inventory(product)

    def get_product_reorder_history_size(self,product):
        # logs.log(debug_msg="| FUNCTION         | actors.get_product_safety_inventory "+str( self)+str(product))
        return self.actor_inventory.get_product_reorder_history_size(product)



    def manufacture_product(self, product):
        if self.actor_state< 60:
            self.set_actor_state( state= 60)
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product actor:"+str( self.name) + " product " +str(product) )
            
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

            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product actor:"+str( self.name) + " product " +str(product) + "composition: "+str(composition) )

            for raw_material_id in composition:
                print("raw_material_id",raw_material_id)
                
                in_stock = int(self.get_product_inventory(raw_material_id))
                
                production_matrix.append(
                    # product id,                   #ratio
                    [raw_material_id ,  in_stock  // int(composition[raw_material_id])    ])
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product production_matrix "+str( production_matrix))


            max_prod=get_max_production(production_matrix)[0]

            if not isinstance(max_prod,int): raise "Manuracture_error"
            
            if max_prod == 0: return False

            elif self.production(product, quantity=max_prod):    
                return True
            
            return False
        else: raise Exception("Erro na manufatura")

            # print("temos de produzir",max_prod," o reagente limitante é ",get_max_production(production_matrix)[0])
            
    def production(self, product, quantity):
        print("~~~~in production:",self.id,  product, quantity)
        
        try: recepe = self.simulation.cookbook[int(product)]
        except:       logs.log(debug_msg="| FUNCTION         | actors.production product without recepe "+str( product))

        row_material=[]

        for ingredient in recepe:
            # verifica se tem stocks 
            if self.get_product_inventory(ingredient) > recepe[ingredient] * quantity:
                row_material.append([ingredient, recepe[ingredient] * quantity ])
        if len(row_material) == len(recepe) and len(row_material>0):
            # remove raw material from inventory
            for i  in row_material:
                self.actor_inventory.remove_from_inventory(product=i[0] , quantity = i[1])
            # add new to inventory
            self.actor_inventory.add_to_inventory( product=product, quantity=quantity)
            return True
        return False
    

    

    