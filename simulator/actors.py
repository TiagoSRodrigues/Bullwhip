import simulation_configuration
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


################################                                                 #############################
#                                           GETTERS 
################################                                                 #############################

    def get_actor_product_list(self):
        logs.log(debug_msg="| FUNCTION         | actors.get_actors_product_list"+str(self))

        products_list=[]
        for product in self.products:
            products_list.append( product["id"] )
        return products_list
    
    def get_product_composition(self, product_id):
        if product_id in  self.simulation.Object_supply_chain.get_end_of_chain_actors():
            logs.log(debug_msg="| FUNCTION         | actors.get_product_composition tentativa de ver composição de produdo de fim de SC . product id:"+str(product_id))
            return False

        for product in self.products:
            logs.log(debug_msg="| FUNCTION         | actors.get_product_composition tentativa de ver composição de produdo id:"+str(product_id))
            if product["id"]==product_id:
                return product["composition"]

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

    def get_todays_transactions(self):
        return self.simulation.ObejctTransationsRecords.get_todays_transactions(self)

################################                                                 #############################
#                                           SETERS 
################################                                                 #############################
 
  
    def set_actor_state(self, state:int, log_msg=None ):
        self.simulation.speed()
        if log_msg== None: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" |" )
        else: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" | "+str(log_msg) )
        
        self.actor_state = state

#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

    def receive_order(self, supplier, quantity, product, client ):
        
        if int(supplier) == int(client):
            raise ValueError("Erro nos clientes - receive order",self.id , client )
        logs.log(debug_msg = "| Ordered recived  | actors        | receive_order -  actor  "+str(self.id)+" received order from actor: "+ str(client) + " of "+ str(quantity) + " of the product " + str(product) )
        

        for el_actor in self.simulation.actors_collection:
            if int(el_actor.id) == int(supplier):
                el_actor.actor_stock_record.add_to_open_orders( product , quantity , client )


    def manage_orders(self):
        
        # Estados
        #     20    Verifica o que tem a receber
        #     30    Verifica o que tem a enviar e tenta enviar
        #     40   
        #     50   
        #     60   
        #     70   
        #     80 pronto       
        self.set_actor_state( state = 20, log_msg="Checking transctions to receive" )



        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders        actor id: "+str(self.id)+" em stock:"+str(self.actor_inventory.main_inventory))

        orders          =   self.actor_stock_record.Open_Orders_Record
        max_capacity    =   self.actor_inventory.max_capacity
        inventory       =   self.actor_inventory.main_inventory
        
        
        # verifica se tem encomendas para RECEBER

        to_receive = self.get_todays_transactions()
        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders        Encomendas para receber: "+str(to_receive))
        if self.actor_state == 20 and len(to_receive)>0 :
            self.set_actor_state( state=21, log_msg=str(len(to_receive))+" Receiving orders " )

            for transaction_id in to_receive:
                self.receive_transaction( transaction_id )

        self.set_actor_state( state = 30, log_msg="Checking transctions to send" )
        
        # verifica se tem encomendas para ENVIAR
        to_send = self.get_orders_pending()
        
        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders       o actor"+str(self.id)+ " tem para enviar as encomendas: "+str(to_send))

        if self.actor_state == 30 and len(to_send) >0 :
            self.set_actor_state( state = 31, log_msg=str(len(to_send))+" Sending orders from stock")
        
            logs.log(debug_msg="| FUNCTION         | actors        | manage_orders actor "+str(self.id)+" IF has "+ str(len(to_send))+" orders to send: " +str(to_send) )
            
            for order in to_send:
                if self.send_transaction(order) :     # verifica se tem stock para enviar ["Time", "Product", "Qty","Client","Order_id","Status"]
                    to_send = self.get_orders_pending()  #Refresh to_send list
                else:
                    if self.manufacture_product(order[1]): 
                        self.send_transaction(order)    #tanta produzir, se conseguir envia logo
                        to_send = self.get_orders_pending()  #actualiza to_send

            
            self.set_actor_state( state = 40, log_msg=str(len(to_send))+" trying to produce")

            logs.log(debug_msg="| FUNCTION         | actors        | manage_orders       o actor"+str(self.id)+ " não tem stock para enviar nem produzir para enviar "+str(order))
      
        self.set_actor_state( state = 40, log_msg=str(len(to_send))+" Orders trated with stock ")


    def manage_stock(self):
        #TODO na verificação de stock para repor verificar se já foi encomendado para n repetir encomendas.
        #todo NÃO MUDAR O ESTADO OS OBJECTOS DENTRO DE UM LOOP 

        # Verifica se tem stock para repor
        if self.actor_state < 50:

            for product in self.products_list:
                logs.log(debug_msg="| FUNCTION         | actors        | manage_stock for product , "+str(product)+" ,in products list: "+str(self.products_list))
            

                #aqui o foco muda das encomendas para a gestão de stock
                #verifica se precisa repor stock de algum produto
                
                if int( self.get_product_inventory(product ) ) <= int(self.get_product_safety_inventory(product ) ):
                    logs.log(debug_msg="| FUNCTION         | actors        | product_inventory "+str(self.get_product_inventory(product ))+" <= i  get_product_safety_inventory "+str(self.get_product_safety_inventory(product ) ))

                    #verifica se pode produzir, se poder produz:
                    if not self.manufacture_product(product):
                        # não pode produzir, tem que encomendar
                        #se tiver de encomendar, prepara encomenda
                        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF, produto" +str(product)+ "sem stock")

                        #vai buscar a composição
                        composition =  self.get_product_composition( product )

                            #encomenda o necessário
                        for key , value in composition.items():
                            if int(key[0]) == int(self.id): continue
                                
                            product_id_to_order = key
                            actor_to_order = key[0]
                            #todo HARD CODED PARA PROVA DE CONCEITO                                                       
                            quantity_to_order = 10 * value
                            # quantity_to_order = int(self.actor_inventory.get_product_reorder_history_size(product_id=product )) * value

                            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock for key , value in composition.items, actor_to_order " +str(actor_to_order)+ " prd "+str(product_id_to_order)+" qdd "+str(quantity_to_order))

                            self.place_order(actor_supplier_id = actor_to_order, product=product_id_to_order, quantity=quantity_to_order)
            self.set_actor_state(state=60, log_msg="Manage stock finished")
            
        
    def send_transaction(self, order):
        logs.log(debug_msg="| FUNCTION         | actors        | send_transaction  order: "+str(order)+" self= "+str(self.name) )
        self.set_actor_state( state=31, log_msg="sending order "+str(order) )
        day= self.simulation.time

        product              = order[1]
        ordered_quantity     = order[2]
        stock_quantity       = self.get_product_inventory(product) # verifica stock
        logs.log(debug_msg="| FUNCTION         | actors        | send_transaction ordered:"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )
        try:
            self.set_actor_state(state=32)
            if int(stock_quantity) > int(ordered_quantity) :          
                self.set_actor_state(state=33, log_msg="Product with stock")

                logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF stock_quantity > ordered_quantity order"+str(order)+" pruduct "+str(product))
            
                
                client       = order[3]             #  ["Time", "Product", "Qty","Client","Order_id","Status"]
                order_id     = order[-2]
                order_status = order[-1]
        
                self.set_actor_state(state= 34, log_msg="Removing from inventary")
                
                # remove o enviado do inventário  
                self.actor_inventory.remove_from_inventory(product, ordered_quantity)

                self.set_actor_state(state= 38, log_msg="addint to transasctions")
                #envia encomendas 
                self.simulation.ObejctTransationsRecords.add_transaction( sender          = self.id,
                                                                          receiver        = client,
                                                                          quantity        = ordered_quantity,
                                                                          product         = product,
                                                                          deliver_date    = day + self.average_time,
                                                                          sending_date    = day)

                                
                self.set_actor_state(state=36, log_msg="removing from orders")
                #remove from open orders
                self.actor_stock_record.remove_from_open_orders(order_id )

                logs.log(debug_msg="| FUNCTION         | actors        | send_transaction order id:"+str(order_id))
                self.set_actor_state(state=37, log_msg="Orders sending complete")
                return True
            else:
                logs.log(debug_msg="| FUNCTION         | actors        | send_transaction NÃO ENVIVOU PQ N TINHA STOCK  ORDERED"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )
        except:
            logs.log(debug_msg="| FUNCTION         | Error on actores.manage_stock IF stock_quantity > ordered_quantity    actor:"+ str(self.id)+' order:'+str(order)+'   stock_quantity'+str(stock_quantity)+'  ordered_quantity:'+str(ordered_quantity))
            # self.set_actor_state(state=39, log_msg="Falhou a tentativa de enviou de encomendas")
            return False
            raise Exception("Falhou o envio de encomendas")    

    def receive_transaction(self, transaction_id):
        self.set_actor_state(state= 22, log_msg="Receiving transaction")
        transaction = self.simulation.ObejctTransationsRecords.get_transaction_by_id(transaction_id)
               
        product              = transaction["product"]               
        ordered_quantity     = transaction["quantity"]
        inventory_capacity   = self.actor_inventory.refresh_inventory_capacity()
        
        # print( inventory_capacity , ordered_quantity)


        #verifica capacidade
        if int(inventory_capacity) + int(ordered_quantity) >= int(self.max_inventory): 
            print("Invendory overcapacity of actor ",self.name)
            self.set_actor_state(state= 23, log_msg="sem espaço para receber encomendas")

            return False

        self.set_actor_state(state= 24, log_msg="recording transaction reception")
        
        #adiciona ao inventário
        self.add_to_inventory(self, product, ordered_quantity)
        
        # regista que recebeu
        self.ObejctTransationsRecords.record_delivered(transaction_id)
              
        self.set_actor_state(state= 39, log_msg=" Finished transcaction reception")

        logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF stock_quantity > ordered_quantity")




    def place_order(self, actor_supplier_id, product, quantity):
      
        logs.log(debug_msg="| FUNCTION         | actors        | place_order from actor "+str( self.id)+" suplier "+str(actor_supplier_id)+"  prd "+str(product)+"  qdd " +str(quantity))

        for actor_to_order in self.simulation.actors_collection: 
         
            if int(actor_to_order.id) == int(actor_supplier_id):
                self.receive_order( supplier= actor_supplier_id, quantity=quantity, product=product, client= self.id )




    def manufacture_product(self, product):
            self.set_actor_state( state= 41 ,  log_msg=" trying to manufacture")
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product actor:"+str( self.name) + " product " +str(product) )
            
            recepe = self.simulation.cookbook[int( product )]

            def get_max_production(product, recepe):      
                self.set_actor_state( state= 42, log_msg=" Calculating max possible production")
         
                logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - get_max_production actor:"+str( self.name) + " product " +str(product) + "composition: "+str(recepe) )

                production_matrix=[]
                min_qty=0
                for raw_material_id in recepe:
                   
                    in_stock = int( self.get_product_inventory( raw_material_id ) )
                    
                    production_matrix.append(
                        # product id,                   #ratio
                        [raw_material_id ,  in_stock  // int(recepe[raw_material_id])    ])
                                                                                                        # logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product production_matrix "+str( production_matrix))

                    
                    RL_id, min  = production_matrix[0]
                    logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - get_max_production min "+str(min) +" RL "+ str(RL_id) )

                    #reagente limitante  
                    for el in production_matrix:
                        if el[-1] < min:  min_qty, RL_id =el[-1], el[0]

                    if not isinstance(min_qty,int): raise "Manuracture_error on min_qty data type"
                return min_qty , RL_id


            max_prod , Limiting_reagent = get_max_production(product= product, recepe=recepe)

            if max_prod == 0: 
                self.set_actor_state( state= 43, log_msg=" Witout raw material")
                return False  #todo daqui o estado 43 deve ser apaganho para fazer encomendas

            elif self.production(product, quantity=max_prod, recepe = recepe):  
                self.set_actor_state( state= 49, log_msg=" Manutacture finished with sucess")
                return True
            
            return False

            # print("temos de produzir",max_prod," o reagente limitante é ",get_max_production(production_matrix)[0])
            
    def production(self, product, quantity, recepe):
        self.set_actor_state( state= 44, log_msg=" Calculating max possible production")
        logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - in production - actor "+str(self.id) +" Pd "+ str(product)+" qty "+ str(quantity)+" recepe "+ str(recepe) )

        row_material = []
        for ingredient in recepe:

            # verifica se tem stocks 
            if self.get_product_inventory(ingredient) > recepe[ingredient] * quantity:
                row_material.append([ingredient, recepe[ingredient] * quantity ])
            else:
                raise Exception("ERRO NA PRODUÇÃO, SE EXISTE UM ERRO AQUI A QUANTIDADE MÁXIMA ESTÁ A SER MAL CALCULADA")    
        if len(row_material) == len(recepe) and len(row_material>0): #verifica que foi buscar todos os ingredientes!
            self.set_actor_state( state= 45, log_msg=" A converter ingredientes")

            # remove raw material from inventory
            for i  in row_material:
                self.actor_inventory.remove_from_inventory(product=i[0] , quantity = i[1])
            # add new to inventory
            self.actor_inventory.add_to_inventory( product=product, quantity=quantity)
            self.set_actor_state( state= 46, log_msg=" Production Finished")
            return True
        else:
            raise Exception("ERRO NA PRODUÇÃO, SE EXISTE UM ERRO AQUI A QUANTIDADE MÁXIMA ESTÁ A SER MAL CALCULADA")    
    

    

    