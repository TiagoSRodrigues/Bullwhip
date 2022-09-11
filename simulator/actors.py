import math
import numpy as np
from simulator import simulation, transactions
from . import  orders_records, inventory, logging_management as logs, easter_eggs as ee
import simulation_configuration  as sim_cfg
import numpy as np
from inspect import stack
logs.log(debug_msg="Started actors.py")

############################################################################################
#       Classe das funções de gestão interna do actor da cadeia de valor                   #
############################################################################################


class actor:
    def __init__(self, simulation_object , id:int , name:str , avg:int , var:int,
                 max_inventory:int, safety_factor:float, reorder_history_size:int,  products:dict):

        ### Constants Properties  ###
        self.id                   = id
        self.name                 = name
        self.average_time         = avg
        self.deviation_time       = var
        self.max_inventory        = max_inventory
        self.safety_factor        = safety_factor
        self.reorder_history_size = reorder_history_size
        self.products             = products
        self.simulation           = simulation_object


        ee.print_actor(self.id,self.reorder_history_size)
        # if self.id == 0:
        #     self.is_customer = True
        # else: self.is_customer = False

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

        logs.new_log(actor=self.id, file="actors", function="constructor",  info_msg=f"Actor created           id={str(self.id)} name: {self.name} called by "+stack()[1][3])

        # #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação #*foi apagado porque n fazia sensido estar aqui, passei para a simulations, durante a criação
        # self.simulation.add_to_actors_collection(self)
        self.simulation.mongo_db.add_to_db(colection_name="scheduled_stock",
                                           data={"_id":self.id,
                                                 "stock":{}})
        #logs
        try:
            logs.new_log(actor=self.id, file="actors", function="constructor",  info_msg=f"Actor data : AVG: {str(self.average_time)} var: {str(self.deviation_time)} max_inventory: {str(self.max_inventory)}  Products: {str(self.products)}")
        except:
            logs.log(debug_msg = "Error in Actors logging")


        """  
        doh




                                                        tttt                                                                   
                                                    ttt:::t                                                                   
                                                    t:::::t                                                                   
                                                    t:::::t            
        ggggggggg   ggggg    eeeeeeeeeeee    ttttttt:::::tttttttttttttt
        g:::::::::ggg::::g  ee::::::::::::ee  t:::::::::::::::::tt:::::
        g:::::::::::::::::g e::::::eeeee:::::eet:::::::::::::::::tt::::
        g::::::ggggg::::::gge::::::e     e:::::etttttt:::::::tttttttttt
        g:::::g     g:::::g e:::::::eeeee::::::e      t:::::t          
        g:::::g     g:::::g e:::::::::::::::::e       t:::::t          
        g:::::g     g:::::g e::::::eeeeeeeeeee        t:::::t          
        g::::::g    g:::::g e:::::::e                 t:::::t    tttttt
        g:::::::ggggg:::::g e::::::::e                t::::::tttt:::::t
        g::::::::::::::::g  e::::::::eeeeeeee        tt::::::::::::::t 
        gg::::::::::::::g   ee:::::::::::::e          tt:::::::::::tt  
            gggggggg::::::g     eeeeeeeeeeeeee            ttttttttttt  
                    g:::::g                                                               
        gggggg      g:::::g                                                               
        g:::::gg   gg:::::g                                                                                                                        
        g::::::ggg:::::::g                                                                                                                        
        gg:::::::::::::g                                                                                                                                                             

        """
    def get_actor_product_list(self):
        logs.new_log(file="actors",function="get_actor_product_list", actor=self.id, debug_msg=f"actor {self.id} products: {self.products}")

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
            logs.new_log(file="actors",function="get_product_composition", actor=self.id, debug_msg=f"get_product_composition tentativa de ver composição de produdo de fim de SC . product id:{str(product_id)}")

            return False


        for product in self.products:
            logs.new_log(file="actors",function="get_actor_product_list", actor=self.id, debug_msg="get_product_composition tentativa de ver composição de produdo id:"+str(product_id))
            if int(product["id"]) == int(product_id):
                #print(product["composition"])
                return product["composition"]

    def get_open_orders(self):
        "ordens abertas que ainda não foram enviadas"
        # logs.new_log(file="actors",function="get_open_orders", actor=self.id, debug_msg="get_open_orders       "+str( self.id))

        pending=[]

        for record in self.actor_orders_record.open_orders_record:
            order_state= self.get_order_state(order= record)
            if order_state in [0]:#,9]:
                pending.append(record)

        logs.new_log(file="actors",function="get_actor_product_list", actor=self.id, debug_msg="get_open_orders     from actor {}, pending: {}".format(self.id, pending))

        return pending

    # def get_actor_present_capacity(self):
    #     return self.actor_inventory.present_capacity

    def get_product_stock(self,product):
        inventory = self.actor_inventory.get_product_stock(product_id = product)
        logs.new_log(day=self.simulation.time, actor=self.id, function="get_product_stock", file="actors", debug_msg=f"actor {self.id} inventory  {inventory}" )
        return inventory


    def get_product_safety_inventory(self,product):
        return self.actor_inventory.get_product_safety_inventory(product)


    def get_delivering_transactions(self):
        return self.simulation.ObejctTransationsRecords.get_delivering_transactions(self)

    # def get_actor_info(self):
    #     actor_data= {"id", self.id,
    #     "name", self.name,
    #     "avg", self.average_time,
    #     "var", self.deviation_time,
    #     "max_inventory", self.max_inventory,
    #     "products", self.products,
    #     "simulation_object", self.simulation,
    #     "stock_record", self.actor_orders_record,
    #     "actor_inventory",self.actor_inventory}

    #     return actor_data

    def get_orders_to_send(self):
        """ devovler as encomendas pendentes ordenadas por id
        """
        #! analisar, à 1ª vista , parece bem
        def get_id(l):
            return l[-3]

        to_send = self.get_open_orders()
        to_send.sort(key=get_id)

        return to_send




    def get_deliver_time(self):
        return np.random.normal(loc=self.average_time, scale=self.deviation_time)

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

    def set_order_processed(self, order_id ):
        return  self.actor_orders_record.set_order_processed(order_id=order_id)

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
        #  [ creation Time,  Product , Qty , Client , Order_id, Status, notes]
        #       -7            -6     -5      -4        -3      - 2    -1

        #! TOD Validar este history hard limit a zero
    def get_orders_history(self, history_cut=0):
        #retorna a média e o std
        return self.actor_orders_record.get_orders_history(history_cut)

    def get_orders_stats(self,product, reorder_history_size=0):
        #retorna a média e o std
        return self.actor_orders_record.get_orders_stats(product= product,history_days= reorder_history_size)

    def get_transactions_stats(self, actor_id, product, history_size=1000000):
        #retorna a média e o std
        return self.simulation.ObejctTransationsRecords.get_transactions_stats(actor_id, product, history_size)

    def get_delivery_stats(self, product_id):
        """calcula a media e o desvio padrão do tempo de entrega de um produto
            indo buscar a composição do produto e calculando as estatisticas de cada um dos componentes
            devolve o tempo maior        
        """
        avg, std = 0, 0
        composition = self.get_product_composition(product_id)
        for product in composition.keys():
            try:
                p_avg, p_std = self.get_transactions_stats(actor_id= self.id,product=product, history_size= self.reorder_history_size)
                if p_avg > avg:
                    avg = p_avg
                    std = p_std
            except:
                continue        
        logs.new_log(actor=self.id, file="actors", function="get_delivery_stats", day=self.simulation.time, debug_msg=f"product_id: {product_id} avg: {avg} std: {std}")

        return avg, std


    def get_order_quantity(self, avg_demand, deviation_demand, avg_delivery_time, deviation_delivery_time, safety_factor = 1):
        """ Calulates the order quantity based on: 
        the average demand,
        the deviation of the demand, 
        the average delivery time, 
        the deviation of the delivery time and 
        the safety factor, if none, sets to 1

        """
        if avg_delivery_time == 0:
            avg_delivery_time = 1

        order_point_base = avg_demand * avg_delivery_time 


        safety_component = safety_factor * (  math.sqrt( 
                                        (avg_delivery_time * deviation_demand**2  ) + ((avg_demand**2) * (deviation_delivery_time **2) )
                                        )
                                            )
        order_quantity = order_point_base + safety_component
        logs.new_log(day=self.simulation.time, actor=self.id, function="get_order_quantity", file="actors", debug_msg= f"| stock_otimization| calculate_order order_point_base: {order_point_base} safety_component: {safety_component} order_quantity: {order_quantity}")              
        return  order_quantity




        """                                         tttt          
                                                  ttt:::t          
                                                  t:::::t          
                                                  t:::::t          
           ssssssssss       eeeeeeeeeeee    ttttttt:::::ttttttt    
         ss::::::::::s    ee::::::::::::ee  t:::::::::::::::::t    
       ss:::::::::::::s  e::::::eeeee:::::eet:::::::::::::::::t    
       s::::::ssss:::::se::::::e     e:::::etttttt:::::::tttttt    
        s:::::s  ssssss e:::::::eeeee::::::e      t:::::t          
          s::::::s      e:::::::::::::::::e       t:::::t          
             s::::::s   e::::::eeeeeeeeeee        t:::::t          
       ssssss   s:::::s e:::::::e                 t:::::t    tttttt
       s:::::ssss::::::se::::::::e                t::::::tttt:::::t
       s::::::::::::::s  e::::::::eeeeeeee        tt::::::::::::::t
        s:::::::::::ss    ee:::::::::::::e          tt:::::::::::tt
         sssssssssss        eeeeeeeeeeeeee            ttttttttttt  

        """

    def add_to_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.new_log(day=self.simulation.time, actor=self.id, function="add_to_stock_scheduled_to_arrive", file="actors", debug_msg= "add_to_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))              

        try:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]+quantity
        except:
            self.stock_scheduled_to_arrive[product_id]=quantity

    def remove_from_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.new_log(day=self.simulation.time, actor=self.id, function="remove_from_stock_scheduled_to_arrive", file="actors", debug_msg= " remove_from_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))            

        # print("(-> id ", self.id,"prd", product_id,"qty", quantity)0
        if self.id != 0:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]-quantity

    def add_to_stock_scheduled_to_send(self,product_id, quantity):
        logs.new_log(day=self.simulation.time, actor=self.id, function="add_to_stock_scheduled_to_send", file="actors", debug_msg= "add_to_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))            

        try:
            present=self.stock_scheduled_to_send[product_id]
            self.stock_scheduled_to_send[product_id] = present + quantity
        except:
            self.stock_scheduled_to_send[product_id] = quantity

    def remove_from_stock_scheduled_to_send(self,product_id, quantity):
        logs.new_log(day=self.simulation.time, actor=self.id, function="remove_from_stock_scheduled_to_send", file="actors", debug_msg= "remove_from_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))            

        if self.id != 0:
            self.stock_scheduled_to_send[product_id]=self.stock_scheduled_to_send[product_id]-quantity

    def add_to_received_transactions(self, transaction):

        self.received_transactions.append(transaction)
        logs.new_log(day=self.simulation.time, actor=self.id, function="add_to_received_transactions", file="actors", debug_msg= "add_to_received_transactions {}".format(transaction))            


    def add_to_order_today(self,  product=None, quantity=None):
        logs.new_log(day=self.simulation.time, actor=self.id, function="add_to_order_today", file="actors", debug_msg= "from actor {}, product: {}, quantity: {}".format(self.id, product, quantity))            

        if product in self.order_today:
            self.order_today[product] =     self.order_today[product] + quantity
            # print( self.id, self.order_today[product] , quantity)
        else:
            self.order_today[product] =     quantity

        return True

    def set_actor_state(self, state:int, log_msg=None ):
        self.simulation.speed()
        # if log_msg== None: 
        #     logs.new_log(day=self.simulation, actor=self.id, file="actors", function="set_actor_state",  debug_msg= f"| STATE CHANGE     | a:{str(self.id)} state: {str(state)} |" )
        # else: 
        logs.new_log(day=self.simulation.time, actor=self.id, file="actors", function="set_actor_state",  debug_msg= f"| STATE CHANGE     | a:{str(self.id)} state: {str(state)} | {str(log_msg)}" )

        self.actor_state = state


    def get_order_preparation(self, product_id, product_quantity):
        """ recebe um produto e uma quantidade objectivo,
        devolve as encomendas necessárias para a sua preparação"""

        #vai buscar a composição
        # a composição diz quanto tem de encomendar para 1 unidade do produto
        composition =  self.simulation.cookbook[product_id]

        order_data=[]
        #ver a qunatidade minima-
            #encomenda o necessário
        # print(product_id,composition)
        for key , value in composition.items():
            product_order = {}
            # print(key,value)
            key=str(key)
            if key[0] == str(self.id): continue

            product_order["product_id_to_order"] = int(key)
            product_order["actor_to_order"] = int(str(key)[0])
            product_order["quantity_to_order"] =int(value) * int(product_quantity)
            order_data.append(product_order)

           # quantity_to_order = int(self.actor_inventory.get_product_reorder_history_size(product_id=product )) * value
        logs.new_log(day=self.simulation.time, actor=self.id, function="get_order_preparation", file="actors", debug_msg= "order preparation from actor {}  produto {}  composition {} order data {}".format(( self.id),str(product_id),str(composition),str(order_data)))            

        return order_data

    def get_product_safety_stock(self, product_id):
        """recebe um produto e devolve a quantidade de stock de segurança"""
        safety_stock =  self.actor_inventory.get_product_safety_stock(product_id=product_id)
        logs.new_log(day=self.simulation.time, actor=self.id, function="get_product_safety_stock", file="actors", debug_msg= f"get_product_safety_stock produto {product_id}  safety stock {safety_stock}")            
        return safety_stock



#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

        """ 



                                                    tttt          
                                                ttt:::t          
                                                t:::::t          
                                                t:::::t          
        aaaaaaaaaaaaa      ccccccccccccccccttttttt:::::ttttttt    
        a::::::::::::a   cc:::::::::::::::ct:::::::::::::::::t    
        aaaaaaaaa:::::a c:::::::::::::::::ct:::::::::::::::::t    
                a::::ac:::::::cccccc:::::ctttttt:::::::tttttt    
            aaaaaaa:::::ac::::::c     ccccccc      t:::::t          
        aa::::::::::::ac:::::c                   t:::::t          
        a::::aaaa::::::ac:::::c                   t:::::t          
        a::::a    a:::::ac::::::c     ccccccc      t:::::t    tttttt
        a::::a    a:::::ac:::::::cccccc:::::c      t::::::tttt:::::t
        a:::::aaaa::::::a c:::::::::::::::::c      tt::::::::::::::t
        a::::::::::aa:::a cc:::::::::::::::c        tt:::::::::::tt
        aaaaaaaaaa  aaaa   cccccccccccccccc          ttttttttttt  


        """
    def place_order(self, product_id, quantity, client= None):

        if client is None:
            client= self.id
        self.set_actor_state(state=65, log_msg="placing orders")

        logs.new_log(day=self.simulation.time, actor=self.id, function="place_order", file="actors", debug_msg= "place_order from actor {} producto {} quantity {}".format( self.id,product_id, quantity))         
        supplier_id = str(product_id)[0]
        product  =  product_id
        quantity =  quantity


        for actor_object in self.simulation.actors_collection:

            if int(actor_object.id) == int(supplier_id):
                actor_object.receive_order( supplier= supplier_id, quantity=quantity, product=product, client= client, notes={} )    #adiciona encomenda no ator destino
                actor_object.add_to_stock_scheduled_to_send(product_id=product_id, quantity= quantity)                                #adiciona À lista a enviar do ator destino
                self.add_to_stock_scheduled_to_arrive(product_id=product_id, quantity= quantity)                                      #adiciona À lista a recever do ator

        logs.new_log(day=self.simulation.time, actor=self.id, function="place_order", file="actors", debug_msg= f"placing order of producto {product_id} quantity {quantity} to supplier {supplier_id} ")              
        return True

    def receive_order(self, supplier, quantity, product, client, notes={} ):

        if quantity == 0:
            raise ValueError("quantity can't be 0")

        if int(supplier) == int(client):
            raise ValueError("Erro nos clientes - receive order   suplpyer {self.i} == client {client}")
        logs.new_log(file="actors", function="receive_order", day=self.simulation.time, actor=self.id, debug_msg= f" receiver actor: {str(self.id)} received from : {str(client)} of qty {str(quantity)} of the product {product}" )

        for el_actor in self.simulation.actors_collection:
            if int(el_actor.id) == int(supplier):
                el_actor.actor_orders_record.add_to_open_orders( product , quantity , client, notes )

                el_actor.add_to_stock_scheduled_to_send(product_id= product, quantity= quantity)

    def receive_orders(self, orders_to_receive):
        self.set_actor_state( state=21, log_msg=str(len(orders_to_receive))+" Receiving orders " )

        for transaction_id in orders_to_receive:
            if not self.receive_transaction( transaction_id ):
                return False
        return True



    def manage_orders(self):
        # print(self.id,self.actor_orders_record.orders_waiting_stock)
        """ gere as ordens de encomenda,
        tem um sistema de estados para evidar rotas incorrecta e para facilitar a analise dos logs


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

        self.order_today={}

        self.set_actor_state( state = 20, log_msg="Checking transctions to receive" )
        logs.new_log(actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"actor id: {self.id}" )

        # orders          =   self.actor_orders_record.open_orders_record
        # max_capacity    =   self.actor_inventory.max_capacity
        # inventory       =   self.actor_inventory.main_inventory


        # verifica se tem encomendas para RECEBER       ######################################

        to_receive = self.get_delivering_transactions()

        logs.new_log(actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg=f"Encomendas para receber: {str(to_receive)}")

        if len(to_receive)>0 :
            self.receive_orders(to_receive)



        # verifica se tem encomendas para Enviar       ######################################
        self.set_actor_state( state = 30, log_msg="Checking transctions to send with mode: ")

        orders_to_send = self.get_orders_to_send()


        if orders_to_send:
            logs.new_log(actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"encomendas para enviar: { str(orders_to_send)}" )
            self.send_orders(orders_to_send)

        else:
            logs.new_log(actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"sem ncomendas para enviar: { str(orders_to_send)}" )

        self.set_actor_state( state = 39, log_msg=str(len(orders_to_send))+" Orders sent from stock n sei se está certo")
        return True

    def send_orders(self, orders_to_send):
        """ envia as encomendas pendentes
        """
        for order in orders_to_send:
            order_id = self.get_order_id(order)
            ordered_quantity=self.get_ordered_quantity(order)
            logs.new_log(actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f" a tentar enviar a order {order_id}")


            # se não existirem produtos suficientes para enviar a encomenda
            transaction_id = self.send_transaction( order_id )
            if transaction_id:
                logs.new_log(actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f" order {order_id} enviada com sucesso na transaction {transaction_id}" )
            
            if not transaction_id :                                                       #tenta enviar
                logs.new_log(actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f"ERRO falhou o envio da order {order_id}" )
                continue #isto devia ser um return false - 
            #!analisar
            elif order_id in self.actor_orders_record.get_orders_waiting_stock():                       #se n enviou verifica se já estava à espera, significa que já foi encomendadad MP
                logs.new_log(actor=self.id, file="actors", function="send_orders", debug_msg= f"ERROR (se aparecer no log é possivel erro) order {order_id} - continue becouse is in waiting stock" )
                continue

            else:
                ordered_product= self.get_ordered_product(order)
                if self.manufacture_product(ordered_product, reference_quantity= ordered_quantity):
                    if self.send_transaction(order_id):        # tanta produzir, se conseguir envia logo
                        continue
                    else:
                        logs.new_log(actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f"  o actor {str(self.id)} Erro na manufatura, está a produzir abaixo do suficiente para enviar {str(order)}")

                self.actor_orders_record.add_to_orders_waiting_stock(order_id= order_id)
                    #to_send = self.get_open_orders()     # actualiza to_send
        return True


    def manage_stock(self):
        """
        Executado depois da destão de encomendas
        verifica se algum dos productos está abaixo do stock minimo
        """


        if self.id in [x for x in self.simulation.Object_supply_chain.get_end_of_chain_actors()]:
            self.set_actor_state( state = 80, log_msg=str( "o actor{} está no fim da cadeia, o estado vai alterar para terminado 80".format(self.id)))
            #get inventory        
            logs.new_log(actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= f"actor: {self.id} detected, state chenged to 80" )
            if self.actor_inventory.get_product_stock(product_id = 5001) < 100000:
                #if inventory is below min_stock, order MP
                self.actor_inventory.set_product_inventory(product_id = 5001, new_quantity= 1000000000)
            return False

        self.stock_otimization()

        self.set_actor_state( state = 40, log_msg=str( "| STATE          | actors        | manage_stock      Actor {} Started stock management".format(self.id)))
        #TODO na verificação de stock para repor verificar se já foi encomendado para n repetir encomendas.
        #ATENTION NÃO MUDAR O ESTADO OS OBJECTOS DENTRO DE UM LOOP



        #todo talvez se possa implementar um set stock to max quando a função é chamada


        # ORDERS WAINTING TO BE SENT

        # waiting_orders = self.actor_orders_record.get_orders_waiting_stock()

        # if len(waiting_orders) >0:
        #     self.set_actor_state( state = 41, log_msg="processing waiting_orders {}".format(waiting_orders))

        #     #encomenda MP para satisfazer o pedido 
        #     for order_id in waiting_orders:

        #         #prepare order:
        #         order_data= self.get_order_preparation(
        #             product_id=self.get_ordered_product(order_id=order_id),
        #             product_quantity= self.get_ordered_quantity(order_id=order_id)
        #             )
        #         #!apagar
        #         # self.add_to_order_today(
        #         #     product=order_data["product_id_to_order"],
        #         #     quantity=order_data["quantity_to_order"]
        #         #     )

        #         self.set_order_processed(order_id=order_id)

        for product in self.products_list:
            logs.new_log(actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= "product {} in product list {}".format(self.id, product, self.products_list) )

            self.set_actor_state( state = 42, log_msg=" cheking inventary stocks")


            #aqui o foco muda das encomendas para a gestão de stock
            #verifica se precisa repor stock de algum produto

            #!nota: ele só pode produzir aquilo que lhe pertece, logo só gere o stock do que pode produzir

            product_stock        = int( self.get_product_stock(product))
            product_safety_stock = int(self.get_product_safety_inventory(product))

            logs.new_log(actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= "product {} stock {} stafety stock {}".format(self.id, product, product_stock, product_safety_stock) )

            if  product_stock <= product_safety_stock:
                self.set_actor_state( state = 43, log_msg="stock inferior ao safety ")

                logs.new_log(actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= f"product_inventory {str(self.get_product_stock(product ))} <= get_product_safety_inventory {str(self.get_product_safety_inventory(product))}")

                #verifica se pode produzir, se poder, produz:
                if not self.manufacture_product(product, reference_quantity = product_safety_stock-product_stock):
                    # não pode produzir, tem que encomendar
                    #se tiver de encomendar, prepara encomenda
                    logs.new_log(actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= "IF não consegiu manufacture_product {} sem stock, actor {}".format(str(product), self.id) )

                    if str(product)[0] == str(self.id):  #afere se pode produzir, para encomendar MP
                          #prepare order:

                        order_data= self.get_order_preparation(
                            product_id=product,
                            product_quantity= product_safety_stock-product_stock
                            )
                        for product_order in order_data:         

                            if not self.place_order( product_order["product_id_to_order"], quantity = product_order["quantity_to_order"]):
                                logs.new_log(day=self.simulation.time, actor=self.id, function="manage_stock", file="actors", debug_msg="ERROR, order not placed!!!")


                                # place_order( product_id = product, quantity= product_safety_stock):
                                raise("erro grave, não produz nem encomenda!!!!!")



        self.set_actor_state(state=49, log_msg="Manage stock finished")
        self.execute_todays_orders() #TODO verificar se isto funciona


    def execute_todays_orders(self):
        self.set_actor_state(state=60, log_msg="executing todays orders")

        # try:
        if len(self.order_today)>0:
            order_data={}
            for key, value in self.order_today.items():
                # print(key,value)
                if key in order_data:
                    order_data[key]=order_data[key]+value
                if key not in order_data:
                    order_data[key]=value
                #verificar se já foi encomendado

            for prd, qty in order_data.items():
                # print(prd, qty)
                self.place_order(product_id=prd, quantity=qty)


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

        logs.new_log(day=self.simulation.time, actor= self.id, file="actors", function="send_transaction",   debug_msg= f"tryng to send order: {order_id}" )

        self.set_actor_state( state=31, log_msg="sending order "+str(order_id) )
        day= self.simulation.time

        order=self.actor_orders_record.get_order_by_id(order_id)

        #time                 = order[0]
        product              = order[1]
        ordered_quantity     = order[2]
        client               = order[3]              #  ["Time", "Product", "Qty","Client","Order_id","Status", "notes"]


        if (ordered_quantity) ==0 :
            logs.new_log(day=self.simulation.time, file="actors", actor=self.id, function="send_transaction",   debug_msg="ERROR, trying to order 0")
            raise Exception("\n\na tentar encomendar zero!!!!\n\n"+str(order))

        stock_quantity       = self.get_product_stock(product) # verifica stock


        logs.new_log(day=self.simulation.time, file="actors", actor=self.id, function="send_transaction",   debug_msg=" ordered qty:"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )

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

            logs.new_log(file="actors", function="send_transaction", actor=self.id, debug_msg= f"Transaction SUCECESSFULLY SENDED !!!  transaction id:{str(transaction)} order id:{str(order_id)}")
            self.set_actor_state(state=37, log_msg="Orders sending complete")
            return transaction
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

        #apagar logs.log(debug_msg="| FUNCTION         | actors        | receive_transaction transasctions id: {}".format(transaction_id))
        logs.new_log(file="actors", function="receive_transaction", day=self.simulation.time, actor=self.id, debug_msg= f"  Transaction SUCECESSFULLY received id: {transaction_id}" )




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

        if not isinstance(product, int):
            raise Exception("product must be an int")


        if str(product)[0] in [str(x) for x in self.simulation.Object_supply_chain.get_end_of_chain_actors()]:
            logs.new_log(file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= f"  " )
            # self.actor_inventory.add_to_inventory( product=product, quantity = 999999)
            # logs.log(debug_msg="| FUNCTION         | actors        | manufacture_product ERRO 999999 produtos {} adicionados ao stock do ator {}".format( str(product), str(self.id)   )  )
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

                in_stock =  self.get_product_stock( raw_material_id )
                production_matrix.append(
                    # product id,                   #ratio
                    [raw_material_id ,  in_stock  // int(recepe[raw_material_id])    ])

                RL_id, min  = production_matrix[0]

            min_qty = math.floor(production_matrix[0][-1])

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
            in_stock= self.get_product_stock(ingredient)
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
        open_orders = self.actor_orders_record.open_orders_record

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







    """                                                                                                                            


            mmmmmmm    mmmmmmm     aaaaaaaaaaaaa  nnnn  nnnnnnnn      aaaaaaaaaaaaa     ggggggggg   ggggg    eeeeeeeeeeee    
            mm:::::::m  m:::::::mm   a::::::::::::a n:::nn::::::::nn    a::::::::::::a   g:::::::::ggg::::g  ee::::::::::::ee  
            m::::::::::mm::::::::::m  aaaaaaaaa:::::an::::::::::::::nn   aaaaaaaaa:::::a g:::::::::::::::::g e::::::eeeee:::::ee
            m::::::::::::::::::::::m           a::::ann:::::::::::::::n           a::::ag::::::ggggg::::::gge::::::e     e:::::e
            m:::::mmm::::::mmm:::::m    aaaaaaa:::::a  n:::::nnnn:::::n    aaaaaaa:::::ag:::::g     g:::::g e:::::::eeeee::::::e
            m::::m   m::::m   m::::m  aa::::::::::::a  n::::n    n::::n  aa::::::::::::ag:::::g     g:::::g e:::::::::::::::::e 
            m::::m   m::::m   m::::m a::::aaaa::::::a  n::::n    n::::n a::::aaaa::::::ag:::::g     g:::::g e::::::eeeeeeeeeee  
            m::::m   m::::m   m::::ma::::a    a:::::a  n::::n    n::::na::::a    a:::::ag::::::g    g:::::g e:::::::e           
            m::::m   m::::m   m::::ma::::a    a:::::a  n::::n    n::::na::::a    a:::::ag:::::::ggggg:::::g e::::::::e          
            m::::m   m::::m   m::::ma:::::aaaa::::::a  n::::n    n::::na:::::aaaa::::::a g::::::::::::::::g  e::::::::eeeeeeee  
            m::::m   m::::m   m::::m a::::::::::aa:::a n::::n    n::::n a::::::::::aa:::a gg::::::::::::::g   ee:::::::::::::e  
            mmmmmm   mmmmmm   mmmmmm  aaaaaaaaaa  aaaa nnnnnn    nnnnnn  aaaaaaaaaa  aaaa   gggggggg::::::g     eeeeeeeeeeeeee  
                                                                                                    g:::::g                     
                                                                                        gggggg      g:::::g                     
                                                                                        g:::::gg   gg:::::g                     
                                                                                        g::::::ggg:::::::g                     
                                                                                        gg:::::::::::::g                      
                                                                                            ggg::::::ggg                        
                                                                                            gggggg                     



    """

    def stock_otimization(self):
        if self.simulation.stock_management_mode == 1:
            self.traditional_stock_management()
            return 1
        elif self.simulation.stock_management_mode == 2:
            self.machine_learnning_stock_management()
            return 2
        elif self.simulation.stock_management_mode == 3:
            self.blockchian_stock_management()
            return 3
        else :
            raise Exception("Erro no stock otimization, método não selecionado")

    def traditional_stock_management(self):
        logs.new_log(day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", )

        #para cada um dos produtos
        for product in self.get_actor_product_list():

            #valita de tem todos os parametros necessários
            parameters=0

            #analisa o stock dos ultimos dias
            orders_stats = self.get_orders_stats(product=product, reorder_history_size= self.reorder_history_size)

            if orders_stats:
                avg_demand, deviation_demand = orders_stats
                parameters = parameters + len(orders_stats)
            
  

            # analisa as tansações


            transasctions_stats = self.get_delivery_stats(product_id=product)

            if transasctions_stats:
                avg_delivery_time, deviation_delivery_time = transasctions_stats
                parameters = parameters + len(transasctions_stats)

            if self.safety_factor:
                parameters += 1

            if parameters < 5:
                logs.new_log(day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg="ERROR, missing parameters to calculate order")
                continue

            logs.new_log(actor=self.id, file="actors", function="traditional_stock_management", day=self.simulation.time,
                         debug_msg=f" avg_demand: {avg_demand} deviation_demand: {deviation_demand} avg_delivery_time: {avg_delivery_time} deviation_delivery_time: {deviation_delivery_time}  safety_factor: {self.safety_factor}")

            if parameters == 5:
                new_delivery_quantity = self.get_order_quantity( avg_demand = avg_demand,
                                                            deviation_demand = deviation_demand,
                                                            avg_delivery_time = avg_delivery_time,
                                                            deviation_delivery_time = deviation_delivery_time,
                                                            safety_factor = self.safety_factor)
            
            else: 
                new_delivery_quantity = self.get_product_safety_stock(product_id=product)

            #prepara a encomendas
            #vai ver a composição 
            #manda vir a quantidade necessária para o new_delivery_quantity
            order_info = self.get_order_preparation( product_quantity= new_delivery_quantity, product_id=product)

            for product_order in order_info:         

                # #ESTOUAQUI
                if not self.place_order( product_order["product_id_to_order"], quantity = product_order["quantity_to_order"]):
                    logs.new_log(day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg="ERROR, order not placed!!!")

        # self.actor_inventory.set_product_safety_inventory(product_id= self.id*1000+1, quantity = int(new_delivery_quantity) )

    # def prepare_order()

    def blockchian_stock_management(self):
        # print("new actor \n")
        actors_colection = self.simulation.actors_collection
        todays_order=[]
        #for actor in actors_colection:
        if self.id == 1:
            for open_order in self.actor_orders_record.open_orders_record:
                if open_order[0]>0:
                    if self.get_order_criation_date(order=open_order) == self.simulation.time:
                        todays_order=open_order
                        # print(todays_order)
            if len(todays_order)>0:
                for i in range(2,6):
                    product= i*1000+1
                    self.place_order( product_id= product  ,
                                        quantity= int( self.get_ordered_quantity(order=todays_order)),
                                        client= int(i)-1)


            # self.send_transaction( order_id=)

            # list_of_open_orders=actor.actor_orders_record.open_orders_record
            # #loop pelas encomendas do ator
            # for item in list_of_open_orders:
            #     # if self.get_order_state(item)==
            #     orders_data.append(item[1:3])

            # if len(orders_data)==1: break



    def blockchian_stock_management_old(self):
        # print("new actor \n")


        actors_colection= self.simulation.actors_collection
        block_array=[]

        actors_list=[]
        #loop pelos atores
        for actor in actors_colection:
            orders_data = []
            inventory_data=0

            list_of_open_orders=actor.actor_orders_record.open_orders_record
            #loop pelas encomendas do ator
            for item in list_of_open_orders:
                # if self.get_order_state(item)==
                orders_data.append(item[1:3])

            if len(orders_data)==1: break

            # print(orders_data)

            orders_data.remove(orders_data[0])


            orders_array = np.array(orders_data)
            orders_array.sum(axis=0)

            soma_total=orders_array.sum(axis=0)[-1]

            actors_list.append([ orders_data[0][0] , soma_total ])

        actors_array = np.array(actors_list)

        procura_no_sc = actors_array[0:self.id-1]

        if len(procura_no_sc)>0:
            #print(procura_no_sc, procura_no_sc.sum(axis=0)[-1])
            self.actor_inventory.set_product_safety_inventory(product_id= self.id*1000+1, quantity = int( procura_no_sc.sum(axis=0)[-1]) )
            logs.log(debug_msg="| blockchain       | actor {} product {}, prcura {}".format(self.id, self.id*1000+1 , procura_no_sc.sum(axis=0)[-1], ))

        # return procura_no_sc.sum(axis=0)[-1]
        # print(actors_array)

            # a ideia é criar a array com as ordens,
            # por cada produto sumar as quantidades

            #criar um arrey para o ator onde adiciona [prd, qdd ordered, qdd inventario]

            #depois junta tudo numa matriz global com todos os atores

            # a quantidade de pedido que o ator X vai receber é igual ao seu indice na matrix,

            #exporta uma submatriz para o caso do ator e faz a soma geral.


            # for order in orders_data:

            # inventory_data = inventory_data + self.get_product_stock(product=item[1])

            # block_array.append(item[1:2])
            # # ["Time", "Product", "Qty","Client","Order_id","Status"]



            #adicionar aos atores
