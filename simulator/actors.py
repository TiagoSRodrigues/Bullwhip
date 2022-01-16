import math
from shutil import ExecError
import numpy

from simulator import simulation
from . import  orders_records, inventory, logging_management as logs
import simulation_configuration  as sim_cfg
import numpy as np
import inspect
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################


class actor:

    def __init__(self, simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int,
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

        if self.id == 0: 
            self.is_customer = True
        else: self.is_customer = False
        
        self.orders_above_safety = False
        
        self.received_transactions=[]  #registo para histórico
        
        #para gestão de stock
        self.stock_scheduled_to_arrive={}
        self.stock_scheduled_to_send={}
        
        
        self.order_today={}
        # #VARIAVEL TEMPORARIA PARA PROVA DE CONCEITO:
        # self.reorder_quantity=25


        
        ### Variable Properties  ######
        #para prevenir loop infinito o estado vai avançando
        self.actor_state="0"  #states 0 = idle  1=busy

        #Cria o Registo de encomendas
        self.actor_orders_record = orders_records.ClassOrdersRecord(self)

        #Cria os inventários
        self.actor_inventory = inventory.ClassInventory( actor = self ,
                                                    max_capacity = max_inventory,
                                                    products=products)
        self.products_list = self.get_actor_product_list()

        logs.log(info_msg="| CREATED OBJECT   | Actor         id="+str(self.id)+" "+self.name+"called by"+inspect.stack()[1][3])

        # #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação #*foi apagado porque n fazia sensido estar aqui, passei para a simulations, durante a criação
        # self.simulation.add_to_actors_collection(self)
        self.simulation.mongo_db.add_to_db(colection_name="scheduled_stock",
                                           data={"_id":self.id,
                                                 "stock":{}})
        #logs
        try:
            logs.log(debug_msg = "| OBJECT CRIATED   | ACTORS    Created actor: "+str(self.id)+" " + str(self.name) + " AVG: "+ str(self.average_time) + " VAR: "+ str(self.variation_time) +
                " max_inventory " + str(self.max_inventory) + " Products " + str(self.products) )
        except:
            logs.log(debug_msg = "Error in Actors logging")


################################                                                 #############################
#                                           GETTERS
################################                                                 #############################

    def add_to_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.log(debug_msg="| scheduler        | actors        | add_to_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))

        try:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]+quantity
        except:
            self.stock_scheduled_to_arrive[product_id]=quantity
        
    def remove_from_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.log(debug_msg="| scheduler        | actors        |  remove_from_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))

        # print("(-> id ", self.id,"prd", product_id,"qty", quantity)
        if self.id != 0:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]-quantity
    
    def add_to_stock_scheduled_to_send(self,product_id, quantity):
        logs.log(debug_msg="| scheduler        | actors        | add_to_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))

        try:
            present=self.stock_scheduled_to_send[product_id]
            self.stock_scheduled_to_send[product_id]=present+quantity
        except:
            self.stock_scheduled_to_send[product_id]=quantity
            
    def remove_from_stock_scheduled_to_send(self,product_id, quantity):
        logs.log(debug_msg="| scheduler        | actors        | remove_from_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))

        if self.id != 0:
            self.stock_scheduled_to_send[product_id]=self.stock_scheduled_to_send[product_id]-quantity

    def add_to_received_transactions(self, transaction):
    
        self.received_transactions.append(transaction)
        logs.log(debug_msg="|received_transcs  | actors        | add_to_received_transactions {}".format(transaction))

    def get_actor_product_list(self):
        logs.log(debug_msg="| FUNCTION         | actors.get_actors_product_list"+str(self))

        products_list=[]
        for product in self.products:
            products_list.append( product["id"] )
        return products_list

    def get_product_composition(self, product_id):
        """Vai buscar a composição do produto ao seu registo interno dos produtos
        tem de ser ao registo interno, pois são os que o ator deve produzir, no inventário tem os que produz e a matéria prima (que deve ser comprada)

        Args:
            product_id ([
        Returns:
            dict :  compusição do producto, ex:{'2001': 1}
        """
        if str(product_id)[0] in  self.simulation.Object_supply_chain.get_end_of_chain_actors():
            logs.log(debug_msg="| FUNCTION         | actors        | get_product_composition tentativa de ver composição de produdo de fim de SC . product id:"+str(product_id))
            return False

        
        for product in self.products:
            logs.log(debug_msg="| FUNCTION         | actors        | get_product_composition tentativa de ver composição de produdo id:"+str(product_id))
            if int(product["id"]) == int(product_id):
                #print(product["composition"])
                return product["composition"]

    def add_to_order_today(self,  product=None, quantity=None):
        logs.log(debug_msg="| order_today      | actors        | add_to_order_today     from actor {}, product: {}, quantity: {}".format(self.id, product, quantity))
        
        if product in self.order_today:
            self.order_today[product] =     self.order_today[product] + quantity
        
        else:
            self.order_today[product] =     quantity
        
        return True


        # order_data["product_id_to_order"]
        # order_data["actor_to_order"] = in
        # order_data["quantity_to_order"] =






    def get_open_orders(self):
        "ordens abertas que ainda não foram enviadas"
        # logs.log(debug_msg="| FUNCTION         | actors        | get_open_orders       "+str( self.id))
       
        pending=[]

        for record in self.actor_orders_record.Open_Orders_Record:
            order_state= self.get_order_state(order= record)
            if order_state in [0,9]:
                pending.append(record)
                
        logs.log(debug_msg="| FUNCTION         | actors        | get_open_orders     from actor {}, pending: {}".format(self.id, pending))
        
        return pending

    def get_actor_present_capacity(self):
        return self.actor_inventory.present_capacity

    def get_product_inventory(self,product):
        logs.log(debug_msg="| FUNCTION         | actors        | get_product_inventory actor {} product {}, stock: {}".format(self.id, product, self.actor_inventory.get_product_inventory(product)))
        return self.actor_inventory.get_product_inventory(product_id =product)

    def get_product_safety_inventory(self,product):
        logs.log(debug_msg="| FUNCTION         | actors get_product_safety_inventory ")
        return self.actor_inventory.get_product_safety_inventory(product)

    # def get_product_reorder_history_size(self,product):
    #     # logs.log(debug_msg="| FUNCTION         | actors get_product_safety_inventory "+str( self)+str(product))
    #     return self.actor_inventory.get_product_reorder_history_size(product)

    def get_delivering_transactions(self):
        return self.simulation.ObejctTransationsRecords.get_delivering_transactions(self)

    def get_actor_info(self):
        actor_data= {"id", self.id,
        "name", self.name,
        "avg", self.average_time,
        "var", self.variation_time,
        "max_inventory", self.max_inventory,
        "products", self.products,
        "simulation_object", self.simulation,
        "stock_record", self.actor_orders_record,
        "actor_inventory",self.actor_inventory}

        return actor_data



#####################                                                 #######################
#                                SETERS
#####################                                                 #######################


    def set_actor_state(self, state:int, log_msg=None ):
        self.simulation.speed()
        if log_msg== None: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" |" )
        else: logs.log(debug_msg= "| STATE CHANGE     | a:"+ str(self.id)+" state: " + str(state)+" | "+str(log_msg) )

        self.actor_state = state

#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

    def receive_order(self, supplier, quantity, product, client, notes={} ):
        if quantity == 0:
            return
    
        if int(supplier) == int(client):
            raise ValueError("Erro nos clientes - receive order",self.id , client )
        logs.log(debug_msg = "| Ordered recived  | actors        | receive_order -  actor  "+str(self.id)+" received order from actor: "+ str(client) + " of "+ str(quantity) + " of the product " + str(product) )


        for el_actor in self.simulation.actors_collection:
            if int(el_actor.id) == int(supplier):
                el_actor.actor_orders_record.add_to_open_orders( product , quantity , client, notes )
                
                el_actor.add_to_stock_scheduled_to_send(product_id= product, quantity= quantity)
        
    def manage_orders(self):
        # print(self.id,self.actor_orders_record.orders_waiting_stock)
        """ gere as ordens de encomenda,
        tem um sistema de estados para evidar rotas incorrecta e para facilitar a analise dos logs

        
        Existem dois modos de gestão de encomendas, fifo e fist: fifo só envia as ecomentdas disponiveis,
        fist envia as encomendas por ordem, mas se uma não tiver stock suficiente para enviar passa à frente e tenta enviar as restasntes.
        ao mesmo tempo faz a encomenda do material para desolver a encomenda pendente.
        
        Returns:
            não retorna nada
        # Estados
        #     20    Verifica o que tem a receber
        #     30    Verifica o que tem a enviar e tenta enviar
        #     40
        #     50
        #     60
        #     70
        #     80 pronto
        """

        order_priority = self.simulation.order_priority #fifo or faster
        
        self.set_actor_state( state = 20, log_msg="Checking transctions to receive" )
        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders        actor id: "+str(self.id))#+" em stock:"+str(self.actor_inventory.main_inventory))

        # orders          =   self.actor_orders_record.Open_Orders_Record
        # max_capacity    =   self.actor_inventory.max_capacity
        # inventory       =   self.actor_inventory.main_inventory
        
        
        # verifica se tem encomendas para RECEBER       ######################################
       
        to_receive = self.get_delivering_transactions()
        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders        Encomendas para receber: "+str(to_receive))

        if len(to_receive)>0 :
            self.set_actor_state( state=21, log_msg=str(len(to_receive))+" Receiving orders " )

            for transaction_id in to_receive:
                self.receive_transaction( transaction_id )

        if  order_priority not in ["fifo","faster" ]:
            raise Exception("prioridades das encomendas mal configurada")
        
        # verifica se tem encomendas para ENVIAR    #########################################
        if order_priority == "fifo":
            self.set_actor_state( state = 30, log_msg="Checking transctions to send with mode: {}".format(order_priority) )
            while self.actor_orders_record.get_fist_open_order_id() is not False:
                
                order_id_to_send = self.actor_orders_record.get_fist_open_order_id()
                               
                if self.send_transaction(order_id = order_id_to_send) is False:
                    if order_id_to_send in self.actor_orders_record.get_orders_waiting_stock():
                        continue
                    
                    order = self.actor_orders_record.get_order_by_id(order_id_to_send)
                    ordered_product = self.get_ordered_product(order)
                    ordered_quantity = self.get_ordered_quantity(order)
                    
                    if self.manufacture_product(product=ordered_product, reference_quantity=ordered_quantity) :
                        self.send_transaction(order_id= order_id_to_send)
                        continue
                    self.actor_orders_record.add_to_orders_waiting_stock(order_id_to_send)
                    break
                
        if order_priority == "faster":
            self.set_actor_state( state = 30, log_msg="Checking transctions to send with mode: {}".format(order_priority) )
            def get_orders_to_send():
                """ devovler as encomendas pendentes ordenadas por id
                """
                def get_id(l):
                    return l[-2]
                to_send = self.get_open_orders()
                
                to_send.sort(key=get_id)
                return to_send
         
            orders_to_send = get_orders_to_send()
            
            if len(orders_to_send)>0:
                logs.log(debug_msg="| FUNCTION         | actors        | manage_orders    actor {} tem para enviar {} ".format(self.id,orders_to_send))

                for order in orders_to_send:
                    order_id = self.get_order_id(order)
                    ordered_quantity=self.get_ordered_quantity(order)
                    logs.log(debug_msg="| FUNCTION         | actors        | manage_orders    actor {} a tentar enviar a order {} ".format(self.id,order_id))
                    if self.send_transaction( order_id) :                                                       #tenta enviar
                        continue
                    
                    elif order_id in self.actor_orders_record.get_orders_waiting_stock():                       #se n enviou verifica se já estava à espera, significa que já foi encomendadad MP
                        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders    actor {} order{} - continue becouse is in waiting lit".format(self.id,order_id))        
                        continue
                        print("temp isto n devia imprimir")
                    else:
                        ordered_product= self.get_ordered_product(order)               
                        if self.manufacture_product(ordered_product, reference_quantity= ordered_quantity):
                            if self.send_transaction(order_id):        # tanta produzir, se conseguir envia logo
                                continue
                            else:
                                logs.log(debug_msg="| FUNCTION         | actors        | manage_orders       o actor"+str(self.id)+ "Erro na manufatura, está a produzir abaixo do suficiente para enviar"+str(order))
                        self.actor_orders_record.add_to_orders_waiting_stock(order_id= order_id)
                            #to_send = self.get_open_orders()     # actualiza to_send
                        
                        
                        
        logs.log(debug_msg="| FUNCTION         | actors        | manage_orders       o actor"+str(self.id)+ " tem para enviar as encomendas: "+str("to_send"))

        self.set_actor_state( state = 39, log_msg=str("len(to_send)")+" Orders sent from stock ")


    def manage_stock(self):
        """Executado depois da destão de encomendas
        verifica se algum dos productos está abaixo do stock minimo
        """
        self.set_actor_state( state = 40, log_msg=str( "| STATE          | actors        | manage_stock      Actor {} Started stock management".format(self.id)))
        #TODO na verificação de stock para repor verificar se já foi encomendado para n repetir encomendas.
        #ATENTION NÃO MUDAR O ESTADO OS OBJECTOS DENTRO DE UM LOOP

        if self.id in self.simulation.Object_supply_chain.get_end_of_chain_actors():
            self.set_actor_state( state = 80, log_msg=str( "o actor{} está no fim da cadeia, o estado vai alterar para terminado 80".format(self.id)))
            return False
            #todo talvez se possa implementar um set stock to max quando a função é chamada

        self.actor_orders_record.refresh_orders_waiting_stock()
        waiting_orders=self.actor_orders_record.get_orders_waiting_stock()
        
        if len(waiting_orders) >0:
            self.set_actor_state( state = 41, log_msg="processing waiting_orders ")

            """ encomenda MP para satisfazer o pedido """
            for order_id in waiting_orders:
                
                #prepare order:
                order_data= self.order_preparation(
                    product_id=self.get_ordered_product(order_id=order_id),
                    product_quantity= self.get_ordered_quantity(order_id=order_id)
                    )
                
                self.add_to_order_today(
                    product=order_data["product_id_to_order"],
                    quantity=order_data["quantity_to_order"]
                    )
                

        for product in self.products_list:
            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock actor {} product {} in product list {}".format(self.id, product, self.products_list))
            self.set_actor_state( state = 42, log_msg=" cheking inventary stocks")


            #aqui o foco muda das encomendas para a gestão de stock
            #verifica se precisa repor stock de algum produto
            
            #!nota: ele só pode produzir aquilo que lhe pertece, logo só gere o stock do que pode produzir
            
            product_stock        = int( self.get_product_inventory(product))
            product_safety_stock = int(self.get_product_safety_inventory(product))
            
            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock actor {} product {} stock {} stafety stock {}".format(self.id, product, product_stock, product_safety_stock))
            if  product_stock < product_safety_stock:
                self.set_actor_state( state = 43, log_msg="stock inferior ao safety ")

                logs.log(debug_msg="| FUNCTION         | actors        | product_inventory "+str(self.get_product_inventory(product ))+" <= get_product_safety_inventory "+str(self.get_product_safety_inventory(product ) ))

                #verifica se pode produzir, se poder produz:
                if not self.manufacture_product(product, reference_quantity= product_safety_stock-product_stock):
                    # não pode produzir, tem que encomendar
                    #se tiver de encomendar, prepara encomenda
                    logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF não consegiu manufacture_product {} sem stock, actor {}".format(str(product), self.id))

                    if str(product)[0] == str(self.id):  #afere se pode produzir, para encomendar MP
                          #prepare order:
                        order_data= self.order_preparation(
                            product_id=product,
                            product_quantity= product_safety_stock-product_stock
                            )
                        
                        if not self.add_to_order_today(
                            product=order_data["product_id_to_order"],
                            quantity=order_data["quantity_to_order"]
                            ):

                            # place_order( product_id = product, quantity= product_safety_stock):
                            raise("erro grave, não produz nem encomenda!!!!!")
                
                    
                    
                    logs.log(debug_msg="| FUNCTION         | actors        | str(product)[0] == str(self.id)  actor:{} the quantity {} of the product {}".format(self.id, product_safety_stock - product_stock, product))

        self.set_actor_state(state=49, log_msg="Manage stock finished")
        self.execute_todays_orders() #TODO verificar se isto funciona

        
    def execute_todays_orders(self):
        self.set_actor_state(state=60, log_msg="executing todays orders")

        # try:
        if len(self.order_today)>0:
            for key, value in self.order_today.items():
                
                #verificar se já foi encomendado
                
                
                
                # print("execute",key, value)
                self.place_order(product_id=key, quantity=value)
        # except:
        #     # print("\n",self.order_today,type() )
        #     for key, value in self.order_today.items():
        #             print("\n",type(key),key,type(value),value)

    def order_preparation(self, product_id, product_quantity):
        """ recebe um produto e uma quantidade objectivo, 
        devolve as encomendas necessárias para a sua preparação"""
        
        #vai buscar a composição
             
        composition =  self.simulation.cookbook[product_id]

        order_data={}
        #ver a qunatidade minima-
            #encomenda o necessário
        # print(product_id,composition)
        for key , value in composition.items():
            # print(key,value)
            key=str(key)
            if key[0] == str(self.id): continue

            order_data["product_id_to_order"] = int(key)
            order_data["actor_to_order"] = int(str(key)[0])
            order_data["quantity_to_order"] =int(value) * product_quantity

           # quantity_to_order = int(self.actor_inventory.get_product_reorder_history_size(product_id=product )) * value
        logs.log(debug_msg="| FUNCTION         | actors        | order preparation from actor {}  produto {}  composition {} order data {}".format(( self.id),str(product_id),str(composition),str(order_data)))

        return order_data
    
    def place_order(self, product_id, quantity):
        self.set_actor_state(state=65, log_msg="placing orders")

        logs.log(debug_msg="| FUNCTION         | actors        | place_order from actor "+str( self.id)+"  produto "+str(product_id))
        
        # order_data =self.order_preparation(product_id = product_id, product_quantity=quantity)
        
        
        # supplier_id =    order_data["actor_to_order"]
        # product  =    order_data["product_id_to_order"]
        # quantity =    order_data["quantity_to_order"]

        supplier_id = str(product_id)[0]
        product  =  product_id
        quantity =  quantity

  
  
  
  
  
  
        for actor_object in self.simulation.actors_collection:

            if int(actor_object.id) == int(supplier_id):
                actor_object.receive_order( supplier= supplier_id, quantity=quantity, product=product, client= self.id, notes={} )    #adiciona encomenda no ator destino
                actor_object.add_to_stock_scheduled_to_send(product_id=product_id, quantity= quantity)                                #adiciona À lista a enviar do ator destino
                self.add_to_stock_scheduled_to_arrive(product_id=product_id, quantity= quantity)                                      #adiciona À lista a recever do ator 
        return True
        
    def send_transaction(self, order_id =int):
        """cria uma transação
        Vai buscar a order ao registo pelo id
        verifica se a quantidade é legal (acima de zero e dentro do stock)
        remove produto do inventário 
        cria a transação
        remove das ordens abertas
        
        Args:
            order_id (int): id da ordem

        Raises:
            Exception: tenta encomendar zero
            Exception: erro ao remover do inventário

        Returns:
            True: correu tudo bem 
            False: não conseguiu enviar
        """
        
        logs.log(debug_msg="| FUNCTION         | actors        | send_transaction  order: "+str(order_id)+" self= "+str(self.name) )
        self.set_actor_state( state=31, log_msg="sending order "+str(order_id) )
        day= self.simulation.time

        order=self.actor_orders_record.get_order_by_id(order_id)
        
        time                 = order[0]
        product              = order[1]
        ordered_quantity     = order[2]
        client               = order[3]              #  ["Time", "Product", "Qty","Client","Order_id","Status", "notes"]
     

        if (ordered_quantity) ==0 : 
            for el in inspect.stack():
                print(el)
            raise Exception("\n\na tentar encomendar zero!!!!\n\n"+str(order))

        stock_quantity       = self.get_product_inventory(product) # verifica stock
        
        
        logs.log(debug_msg="| FUNCTION         | actors        | send_transaction ordered:"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )

        self.set_actor_state(state=32)

        if int(stock_quantity) >= int(ordered_quantity):
            self.set_actor_state(state=33, log_msg="Product with stock")

            logs.log(debug_msg="| FUNCTION         | actors        | manage_stock IF stock_quantity > ordered_quantity order "+str(order)+" pruduct "+str(product))

            self.set_actor_state(state= 34, log_msg="Removing from inventary")

            # remove o enviado do inventário
            try:
                if self.actor_inventory.remove_from_inventory(product=product, quantity= ordered_quantity) is False:
                    return False
            except:
                logs.log(debug_msg="| FUNCTION         | actors        | send_transaction erro ao remover o enviado do inventário  order id:"+str(order_id))
                raise Exception("Não conseguiu remover do inventário depois de verificar que tinha stock")

            self.set_actor_state(state= 35, log_msg="adding to transasctions")
            #envia encomendas
            logs.log(debug_msg="| FUNCTION         | actors        | send_transaction trying to send transaction order id:"+str(order_id))
            
            deliver_day = self.simulation.time + math.ceil( self.get_deliver_time())
            order_criation_day = self.get_order_criation_date(order_id=order_id)   
                                                       
            transaction_info={
                "deliver_day": deliver_day,
                "order_id": order_id,
                "order_criation_day":order_criation_day,
                "sending_day":day,
                "receiver":client,
                "sender":self.id,
                "product":product,
                "quantity": ordered_quantity,
                "transit_time":None,
                "lead_time": None,
                "theoretical_lead": deliver_day - order_criation_day
                    }

            transaction = self.simulation.ObejctTransationsRecords.add_transaction(transaction_info)
            
            
            
            
            if transaction is False:
                return False
                        
            self.set_actor_state(state=36, log_msg="removing from orders")
            #remove from open orders
            self.actor_orders_record.remove_from_open_orders(order_id )
            
            self.remove_from_stock_scheduled_to_send(product_id=product, quantity=ordered_quantity)
            
            logs.log(debug_msg="| FUNCTION         | actors        | send_transaction SUCECESSFULL SENDED order id:"+str(order_id))
            self.set_actor_state(state=37, log_msg="Orders sending complete")
            return True
        else:
            logs.log(debug_msg="| FUNCTION         | actors        | send_transaction NAO ENVIVOU PQ N TINHA STOCK  qty ORDERED: "+str(ordered_quantity)+" em stock: "+str(stock_quantity) )
            return False


    def receive_transaction(self, transaction_id):
        """Recebe os productos de uma encomendas
        verifica se tem capacidade no inventário total para receber a encomenda
            se não tiver capacidade no inventário não a recebe e ela fica suspensa
        adiciona ao inventário
        regista nas transações que a encomenda foi entregue 

        
        Args:
            transaction_id ([type]): [description]

        Raises:
            Exception: se não conseguir adicionar ao inventário depois de ter verificado que podia

        Returns:
            [type]: [description]
        """
        self.set_actor_state(state= 22, log_msg="Receiving transaction")
        transaction = self.get_transactions_by_id(transaction_id)

        product              = transaction["product"]
        ordered_quantity     = transaction["quantity"]
        inventory_capacity   = self.actor_inventory.refresh_inventory_capacity()

        #verifica capacidade
        if (int(inventory_capacity) + int(ordered_quantity)) > int(self.max_inventory):
            self.set_actor_state(state= 23, log_msg="sem espaço para receber encomendas")
            return False

        self.set_actor_state(state= 24, log_msg="recording transaction reception")

        #adiciona ao inventário
        if not self.actor_inventory.add_to_inventory( product, ordered_quantity):
            raise Exception("Error, could not add to inventory")

        # regista que recebeu
        self.simulation.ObejctTransationsRecords.record_delivered(transaction_id)
        
        self.add_to_received_transactions(transaction=transaction_id)
        
        self.remove_from_stock_scheduled_to_arrive(product_id=product, quantity= ordered_quantity)
        self.set_actor_state(state= 29, log_msg=" Finished transcaction reception")

        logs.log(debug_msg="| FUNCTION         | actors        | receive_transaction transasctions id: {}".format(transaction_id))



    def manufacture_product(self, product, reference_quantity=0): 
        """ produção de produtos
        vai ler a composição do produto ao cook book
        valida os stocks e calcula a quantidade máxima que consegue produzir

        
        
        Args:
            product ([type]): [description]

        Returns:
            True: se o ator de fim da cadeia ficar sem stock - adiciona 999999 produtos ao stock
            True: conseguiu produzir
            False: não conseguiu produzir
            False: se for o ator de fim de cadeia 
        """
        # if self.actor_state < 40 or self.actor_state > 60:
        #     raise Exception("Illigal entrace in manufacture_product")

        if not isinstance(product, int):
            print("\n erro no produto")
            for el in inspect.stack():
                print(el)
            print("\n\n\n")
        

        if str(product)[0] in [str(x) for x in self.simulation.Object_supply_chain.get_end_of_chain_actors()]:
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product ERRO actor: {}  product {} -  o ator de fim de cadeia deve ter sotock infinito".format(str(self.id) , str(product)))    
            self.actor_inventory.add_to_inventory( product=product, quantity = 999999)
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product ERRO 999999 produtos {} adicionados ao stock do ator {}".format( str(product), str(self.id)   )  )  
            return True        
            
                #raise Exception("tring to manufacture in the end of supply chain ")

        self.set_actor_state( state= 42 ,  log_msg=" trying to manufacture product {} ref quantity: {}".format(str(product), str(reference_quantity)))
        logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product actor:"+str( self.name) + " product " +str(product) )

        recepe = self.simulation.cookbook[product]
        present_inventory_capacity = self.actor_inventory.present_capacity
        max_max_inventory_capacity = self.max_inventory
            
        def get_max_production(product, recepe):
            self.set_actor_state( state= 43, log_msg=" Calculating max possible production")

            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - get_max_production actor:"+str( self.name) + " product " +str(product) + "composition: "+str(recepe) )

            production_matrix=[]
            
            for raw_material_id in recepe:
                
                in_stock =  self.get_product_inventory( raw_material_id )
                production_matrix.append(
                    # product id,                   #ratio
                    [raw_material_id ,  in_stock  // int(recepe[raw_material_id])    ])

                RL_id, min  = production_matrix[0]

            min_qty=production_matrix[0][-1]
            for el in production_matrix:
                if el[-1] < min_qty:
                    min_qty, RL_id =el[-1], el[0]

                if not isinstance(min_qty,int): raise "Manuracture_error on min_qty data type"
            logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - get_max_production max "+str(min_qty) +" RL "+ str(RL_id) )
            return min_qty , RL_id

        max_prod , Limiting_reagent = get_max_production(product= product, recepe=recepe)

        #teste para verificar que a produção n supera o inventários # para csasos em que 1u de mp origina mais de 1u de produto
        if (max_prod + present_inventory_capacity) > max_max_inventory_capacity:
            max_prod = max_max_inventory_capacity - present_inventory_capacity
            logs.log(debug_msg="| FUNCTION         | actors        | ERRO manufacture_product producao de {} limitada a {} por limitacoes de stock".format(str(product), str(max_prod)))

        elif max_prod == 0:
            self.set_actor_state( state= 44, log_msg="actor {} Witout raw material {}".format(self.id, Limiting_reagent))
            return False
        
        elif reference_quantity > max_prod:
            self.set_actor_state( state= 44, log_msg="actor {} Witout enough raw material for order {}".format(self.id, Limiting_reagent))
            return False

        elif self.production(product, quantity=max_prod, recepe = recepe):
            self.set_actor_state( state= 48, log_msg=" Manutacture finished with sucess")
            return True

        #!todo rever isto
        # raise Exception("Erro na manufatura, não returnou produção nem falta de stock")

    def production(self, product, quantity, recepe):
        #print( type(product), type(quantity), type(recepe))
        """ converte matéria prima em produto em stock
        Args:
            product ([type]): [description]
            quantity ([type]): [description]
            recepe ([type]): [description]

        Raises:
            Exception: [description]
            Exception: [description]
            Exception: [description]

        Returns:
            [type]: [description]
        """
        
        self.set_actor_state( state= 45, log_msg=" production order placed for {} units of {}".format(str(quantity), str(product) ) )
        logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product - in production - actor "+str(self.id) +" Pd "+ str(product)+" qty "+ str(quantity)+" recepe "+ str(recepe) )

        raw_material = []
        for ingredient in recepe:

            # verifica se tem stocks
            in_stock= self.get_product_inventory(ingredient)
            necessary_stock = recepe[ingredient] * quantity
            #print("temp"in_stock, necessary_stock)
            if in_stock >= necessary_stock:
                raw_material.append([ingredient, recepe[ingredient] * quantity ])
            else:
                raise Exception("ERRO NA PRODUÇÃO, SE EXISTE UM ERRO AQUI A QUANTIDADE MÁXIMA ESTÁ A SER MAL CALCULADA")

        #print("temp vai produzir {}  raw_mat {}  recepe {} ".format(product, len(raw_material), len(recepe)))
        
        if len(raw_material) == len(recepe) and len(raw_material)>0: #verifica que foi buscar todos os ingredientes!
            self.set_actor_state( state= 46, log_msg=" A converter ingredientes")

            # remove raw material from inventory
            for i  in raw_material:
                self.actor_inventory.remove_from_inventory(product=i[0] , quantity = i[1])
            # add new to inventory

                    #adiciona ao inventário
            if not self.actor_inventory.add_to_inventory( product=product, quantity = quantity):
                raise Exception("Error, could not add to inventory in production")

            self.set_actor_state( state= 48, log_msg=" Production Finished")
            return True
        else:
            raise Exception("ERRO NA PRODUÇÃO, SE EXISTE UM ERRO AQUI A QUANTIDADE MÁXIMA ESTÁ A SER MAL CALCULADA")


    def check_orders_above_safety(self):
        """Se o ator receber uma encomenda para o qual não tenha stock mas esta esteja acima do safety stock
        não vai enviar pq não tem stock mas não encomenda materia prima porque não atingio o safety stock
        ["Time", "Product", "Qty","Client","Order_id","Status"]
        """
        #history=self.simulation.mongo_db.get_actor_orders( self.id)
        open_orders = self.actor_orders_record.Open_Orders_Record
        
        orders_above_safety=[]
        for order in open_orders:
            #print(open_orders)
            order_quantity=order[2]
            product_id=order[1]
            safety_stock=self.actor_inventory.get_product_safety_stock(product_id=product_id)
            
            if order_quantity > safety_stock:
                orders_above_safety.append(order)
        if len(orders_above_safety)>0:
            return orders_above_safety
        return False
    
    def get_deliver_time(self):
        return numpy.random.normal(loc=self.average_time, scale=self.variation_time)
        
    def get_transactions_by_id(self, transactions_id):
        return self.simulation.ObejctTransationsRecords.get_transaction_by_id(transactions_id)

    def get_ordered_product(self,order = None ,order_id = None):
        if order:
            return order[1]
        elif order_id:
            return self.actor_orders_record.get_order_by_id(order_id)[1]

    def get_ordered_quantity(self,order = None ,order_id = None):
        if order:
            return order[2]
        elif order_id:
            return self.actor_orders_record.get_order_by_id(order_id)[2]
    
    def get_order_id(self, order=list ):
        return order[-3]

    def get_order_by_id(self, order_id ):
        return  self.actor_orders_record.get_order_by_id(order_id)
 
    def get_order_criation_date(self, order=None, order_id=None ):
        if order:
            return order[0]
        elif order_id:
            return self.actor_orders_record.get_order_by_id(order_id)[0]
        
    def get_order_state(self, order = None ,order_id = None):
        if order:
            return order[5]
        elif order_id:
            return self.actor_orders_record.get_order_by_id(order_id)[5]
        
        #   0                 1       2       3        4        5        6
        #[ creation Time,  Product , Qty , Client , Order_id, Status, notes]