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


        self.last_order_point     = 0
        # self.own_products         = products  os produtos dele, começam pelo nº do ator!!!!

        ee.print_actor(self.id,self.reorder_history_size)
        # if self.id == 0:
        #     self.is_customer = True
        # else: self.is_customer = False

        self.orders_above_safety = False

        self.received_transactions=[]  #registo para histórico

        #para gestão de stock
        self.stock_scheduled_to_arrive={}
        self.stock_scheduled_to_send={}

        #record of open order by day
        self.daily_open_orders= np.array([])
        
        self.ordered_today={}
        # #VARIAVEL TEMPORARIA PARA PROVA DE CONCEITO:
        # self.reorder_quantity=25


        ### Variable Properties  ######
        #para prevenir loop infinito o estado vai avançando
        self.actor_state="0"  #states 0 = idle  1=busy

        #Cria o Registo de encomendas
        self.actor_orders_record = orders_records.ClassOrdersRecord(self)

        #Cria os inventários
        self.actor_inventory = inventory.ClassInventory(actor = self ,
                                                    max_capacity = max_inventory,
                                                    products=products)
        self.products_list = self.get_actor_product_list()

        logs.new_log(state=self.actor_state, actor=self.id, file="actors", function="constructor",  info_msg=f"Actor created           id={str(self.id)} name: {self.name} called by "+stack()[1][3])

        # #LAST THING: Adiciona o ator à lista de objectos (atores) da simulação #*foi apagado porque n fazia sensido estar aqui, passei para a simulations, durante a criação
        # self.simulation.add_to_actors_collection(self)
        self.simulation.mongo_db.add_to_db(colection_name="scheduled_stock",
                                           data={"_id":self.id,
                                                 "stock":{}})
        #logs
        try:
            logs.new_log(state=self.actor_state, actor=self.id, file="actors", function="constructor",  info_msg=f"Actor data : AVG: {str(self.average_time)} var: {str(self.deviation_time)} max_inventory: {str(self.max_inventory)}  Products: {str(self.products)}")
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
    # def get_ordered_stock(self, product_id):
    #     ordered_stock = 0

    #     for order in self.actor_orders_record.open_orders_record:
    #         if self.get_order_state(order) == 6:
    #             if self.get_ordered_product(order) == product_id:
    #                 ordered_stock += self.get_ordered_quantity(order)
    #     logs.new_log(state=self.actor_state, file="actors",function="get_ordered_stock", actor=self.id, debug_msg=f"actor {self.id} product_id: {product_id} ordered stock today {ordered_stock}")
    #     return ordered_stock



    def get_actor_inventory(self):
        return self.actor_inventory.main_inventory

    def get_actor_product_list(self):
        logs.new_log(state=self.actor_state, file="actors",function="get_actor_product_list", actor=self.id, debug_msg=f"actor {self.id} products: {self.products}")

        products_list=[]
        for product in self.products:
            if str(product["id"])[0] == str(self.id):
                products_list.append(int(product["id"]))
        return products_list

    def get_product_composition(self, product_id):
        """Vai buscar a composição do produto ao seu registo interno dos produtos
        tem de ser ao registo interno, pois são os que o ator deve produzir, no inventário tem os que produz e a matéria prima (que deve ser comprada)

        Args:
            product_id ([
        Returns:
            dict :  compusição do producto, ex:{'2001': 1}
        """
        if str(product_id)[0] in  self.get_root_actors():
            logs.new_log(state=self.actor_state, file="actors",function="get_product_composition", actor=self.id, debug_msg=f"get_product_composition tentativa de ver composicao de produdo de fim de SC . product id:{str(product_id)}")

            return False


        for product in self.products:
            logs.new_log(state=self.actor_state, file="actors",function="get_product_composition", actor=self.id, debug_msg="get_product_composition tentativa de ver composicao de produdo id:"+str(product['id']))
            if int(product["id"]) == int(product_id):
                #print(product["composition"])
                return product["composition"]

    def get_open_orders(self):
        "ordens abertas que ainda não foram enviadas"
        # logs.new_log(state=self.actor_state, file="actors",function="get_open_orders", actor=self.id, debug_msg="get_open_orders       "+str(self.id))

        pending=[]

        for record in self.actor_orders_record.open_orders_record:
            order_state= self.get_order_state(order= record)
            if order_state in [0,1,2,3,4,5,6]:
                pending.append(record)

        logs.new_log(state=self.actor_state, file="actors",function="get_open_orders", actor=self.id, debug_msg="   from actor {}, pending: {}".format(self.id, pending))

        return pending

    # def get_actor_present_capacity(self):
    #     return self.actor_inventory.present_capacity

    def get_product_stock(self,product):
        inventory = self.actor_inventory.get_product_stock(product_id = int(product))
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="get_product_stock", file="actors", debug_msg=f"actor {self.id} inventory  {inventory}" )
        return inventory


    def get_product_safety_stock(self,product):
        return self.actor_inventory.get_product_safety_stock(product)


    def get_delivering_transactions(self):
        self.set_actor_state(state=11, log_msg="get_delivering_transactions")
        return self.simulation.ObejctTransationsRecords.get_delivering_transactions(self)

    def get_orders_to_send(self):
        """ devovler as encomendas pendentes ordenadas por id
        """
        def get_id(l):
            return l[-3]

        to_send = self.get_open_orders()
        to_send.sort(key=get_id)
        logs.new_log(state=self.actor_state, file="actors",function="get_orders_to_send", actor=self.id, debug_msg= f"orders_to_send {to_send}")
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

    def set_order_state_to_processed(self, order_id ):
        return  self.actor_orders_record.set_order_state_to_processed(order_id=order_id)

    def set_order_state(self, order_id, status):
        return  self.actor_orders_record.set_order_status(order_id=order_id, status=status)

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
    def get_orders_waiting_stock(self):
        return self.actor_orders_record.get_orders_waiting_stock()

        #! TOD Validar este history hard limit a zero
    def get_orders_history(self, history_cut=0):
        #retorna a média e o std
        return self.actor_orders_record.get_orders_history(history_cut)

    def get_orders_stats(self,product, reorder_history_size=0):
        #retorna a média e o std
        return self.actor_orders_record.get_orders_stats(product= product,history_days= reorder_history_size)

    def get_transactions_stats(self, actor_id:int, product:int, history_size:int):
        actor, product, history_size = int(actor_id), int(product), int(history_size)
        #retorna a média e o std
        return self.simulation.ObejctTransationsRecords.get_transactions_stats(actor_id, product, history_size)

    def get_delivery_stats(self, product_id:int):
        product_id = int(product_id)
        """calcula a media e o desvio padrão do tempo de entrega de um produto
            indo buscar a composição do produto e calculando as estatisticas de cada um dos componentes
            devolve o tempo maior
        """

        avg, std = 0, 0
        composition = self.get_product_composition(product_id)
        # print(f"composition {composition}")
        for ingredient in composition.keys():

            transactions_stats = self.get_transactions_stats(actor_id= self.id, product=int(ingredient), history_size= self.reorder_history_size)
            if transactions_stats:
                p_avg, p_std = transactions_stats
                if p_avg > avg:
                    avg = p_avg
                    std = p_std

        logs.new_log(state=self.actor_state, actor=self.id, file="actors", function="get_delivery_stats", day=self.simulation.time, debug_msg=f"product_id: {ingredient} avg: {avg} std: {std}")

        if avg+std == 0:
            return False
        return avg, std

    def get_product_default_delivery_stats(self, product_id:int):
        actor_id = str(product_id)[0]
        actor_data = self.simulation.get_actor_delivery_stats(actor_id=actor_id)
        return actor_data['average_time'], actor_data['deviation_time']

    def get_order_quantity(self, avg_demand, deviation_demand, avg_delivery_time, deviation_delivery_time, safety_factor = 1):
        """ Calulates the order quantity based on:
        the average demand,
        the deviation of the demand,
        the average delivery time,
        the deviation of the delivery time and
        the safety factor, if none, sets to 1


        """

        order_point_base = avg_demand * avg_delivery_time


        safety_component = safety_factor * ( math.sqrt(
                                        (avg_delivery_time * deviation_demand**2  ) + ((avg_demand**2) * (deviation_delivery_time **2) )
                                        )
                                            )
        self.last_order_point = order_point_base + safety_component

        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="get_order_quantity", file="actors", debug_msg= f"| stock_otimization| calculate_order order_point_base: {order_point_base} safety_component: {safety_component} last_order_point: {self.last_order_point}")
        return  self.last_order_point


    def get_waiting_stock(self, product_id):
        # checks waiting orders
        # ir ordered product is the same as the product_id
        # sums the quantity

        orders_waiting_stock = self.get_orders_waiting_stock()

        waiting_stock = 0
        for order in orders_waiting_stock:
            order = self.get_order_by_id(order_id=order)
            if self.get_ordered_product(order) == product_id:
                waiting_stock += self.get_ordered_quantity(order)
        return waiting_stock





    #     """                                         tttt
    #                                               ttt:::t
    #                                               t:::::t
    #                                               t:::::t
    #        ssssssssss       eeeeeeeeeeee    ttttttt:::::ttttttt
    #      ss::::::::::s    ee::::::::::::ee  t:::::::::::::::::t
    #    ss:::::::::::::s  e::::::eeeee:::::eet:::::::::::::::::t
    #    s::::::ssss:::::se::::::e     e:::::etttttt:::::::tttttt
    #     s:::::s  ssssss e:::::::eeeee::::::e      t:::::t
    #       s::::::s      e:::::::::::::::::e       t:::::t
    #          s::::::s   e::::::eeeeeeeeeee        t:::::t
    #    ssssss   s:::::s e:::::::e                 t:::::t    tttttt
    #    s:::::ssss::::::se::::::::e                t::::::tttt:::::t
    #    s::::::::::::::s  e::::::::eeeeeeee        tt::::::::::::::t
    #     s:::::::::::ss    ee:::::::::::::e          tt:::::::::::tt
    #      sssssssssss        eeeeeeeeeeeeee            ttttttttttt

    #     """


    def set_product_safety_stock(self, product_id, quantity):
        return self.actor_inventory.set_product_safety_stock(product_id, quantity=quantity)


    def update_safety_stock(self, product_id):
        orders_stats = self.get_orders_stats(product=int(product_id), reorder_history_size= self.reorder_history_size)
        avg_demand=0
        if orders_stats:
            avg_demand = orders_stats[0]
        if avg_demand > self.last_order_point:
            safety_stock = avg_demand
        if avg_demand <= self.last_order_point:
            safety_stock = self.last_order_point
        if safety_stock == 0:
            logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="update_safety_stock",
                         file="actors", debug_msg= f"ERROR last_order_point is zero")
        
        self.actor_inventory.set_product_safety_stock(product_id=product_id, quantity=safety_stock)

    def update_product_waiting_stock(self, product_id, quantity):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="update_product_waiting_stock", file="actors", debug_msg= f"  product_id: {product_id} quantity waiting: {quantity}")
        self.actor_inventory.update_product_waiting_stock(product_id, quantity)

    def add_to_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="add_to_stock_scheduled_to_arrive", file="actors", debug_msg= "add_to_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))

        try:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]+quantity
        except:
            self.stock_scheduled_to_arrive[product_id]=quantity

    def remove_from_stock_scheduled_to_arrive(self,product_id, quantity):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="remove_from_stock_scheduled_to_arrive", file="actors", debug_msg= " remove_from_stock_scheduled_to_arrive actor {} product {} qty {}".format(self.id,product_id, quantity))

        # print("(-> id ", self.id,"prd", product_id,"qty", quantity)0
        if self.id != 0:
            self.stock_scheduled_to_arrive[product_id]=self.stock_scheduled_to_arrive[product_id]-quantity #

    def add_to_stock_scheduled_to_send(self,product_id, quantity):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="add_to_stock_scheduled_to_send", file="actors", debug_msg= "add_to_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))

        try:
            present=self.stock_scheduled_to_send[product_id]
            self.stock_scheduled_to_send[product_id] = present + quantity
        except:
            self.stock_scheduled_to_send[product_id] = quantity

    def remove_from_stock_scheduled_to_send(self,product_id, quantity):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="remove_from_stock_scheduled_to_send", file="actors", debug_msg= "remove_from_stock_scheduled_to_send actor {} product {} qty {}".format(self.id,product_id, quantity))

        if self.id != 0:
            self.stock_scheduled_to_send[product_id]=self.stock_scheduled_to_send[product_id]-quantity

    def add_to_received_transactions(self, transaction):

        self.received_transactions.append(transaction)
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="add_to_received_transactions", file="actors", debug_msg= "add_to_received_transactions {}".format(transaction))


    def add_to_order_today(self,  product=None, quantity=None):
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="add_to_order_today", file="actors", debug_msg= "from actor {}, product: {}, quantity: {}".format(self.id, product, quantity))

        if product in self.order_today:
            self.order_today[product] =     self.order_today[product] + quantity
            # print(self.id, self.order_today[product] , quantity)
        else:
            self.order_today[product] =     quantity

        return True

    def add_to_waiting_stock(self, order_id):
        self.actor_orders_record.set_order_state_to_waiting(order_id)


    def set_actor_state(self, state:int, log_msg=None ):
        state = int(state)

        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, file="actors", function="set_actor_state",  info_msg= f" a:{str(self.id)} NEW STATE: {str(state)} | {str(log_msg)}" )

        self.actor_state = state


    def get_order_preparation(self, product_id, product_quantity):
        """ recebe um produto e uma quantidade objectivo,
        devolve as encomendas necessárias para a sua preparação"""
        self.set_actor_state(70, log_msg="preparating order")
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
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="get_order_preparation", file="actors", debug_msg= "order preparation from actor {}  produto {}  composition {} order data {}".format((self.id),str(product_id),str(composition),str(order_data)))

        return order_data

    def get_root_raw_material(self):
        '''devolve os produtos dos atores do fim da cadeia'''
        end_of_chain_products = self.get_root_actors()[0]*1000+1
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="get_end_of_chain_products", file="actors", debug_msg= f"get_end_of_chain_products {end_of_chain_products}")
        return end_of_chain_products
    
    def get_root_actors(self):
        '''devolve a lista de atores do fim da cadeia'''
        return self.simulation.Object_supply_chain.get_end_of_chain_actors()
#-----   actor management   --------------------------------------------------------------------------------------------------------------------#

    
    def place_order(self, product_id, quantity, client= None):
        ' uses product id and quantity to place an order automatically'
        if client is None:
            client= self.id
        self.set_actor_state(state=65, log_msg="placing orders")

        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="place_order", file="actors", debug_msg= "place_order from actor {} producto {} quantity {}".format(self.id,product_id, quantity))
        supplier_id = str(product_id)[0]
        product  =  product_id
        quantity =  quantity


        for actor_object in self.simulation.actors_collection:

            if int(actor_object.id) == int(supplier_id):
                actor_object.receive_order(supplier= supplier_id, quantity=quantity, product=product, client= client, notes={} )    #adiciona encomenda no ator destino
                actor_object.add_to_stock_scheduled_to_send(product_id=product_id, quantity= quantity)                                #adiciona À lista a enviar do ator destino

                if sim_cfg.SIMULATION_MODE == 1:
                    self.add_to_stock_scheduled_to_arrive(product_id=product_id, quantity= quantity)                                      #adiciona À lista a recever do ator

                logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="place_order", file="actors", debug_msg= f"placed order of product {product_id} quantity {quantity} to supplier {supplier_id} from actor {client}  || debug: {actor_object.id}")
        return True

    def receive_order(self, supplier, quantity, product, client, notes={} ):
        self.set_actor_state(state=5, log_msg="receiving order")
        if quantity == 0:
            raise ValueError("quantity can't be 0")

        if int(supplier) == int(client):
            raise ValueError("Erro nos clientes - receive order   suplpyer {self.i} == client {client}")
        logs.new_log(state=self.actor_state, file="actors", function="receive_order", day=self.simulation.time, actor=self.id, debug_msg= f" actor: {str(self.id)} received order from : {str(client)} of qty {str(quantity)} of the product {product}" )


        self.actor_orders_record.add_to_open_orders(product , quantity , client, notes )
        self.add_to_stock_scheduled_to_send(product_id= product, quantity= quantity)

        # for el_actor in self.simulation.actors_collection:
        #     if int(el_actor.id) == int(supplier):
        #         el_actor.actor_orders_record.add_to_open_orders(product , quantity , client, notes )

        #         el_actor.add_to_stock_scheduled_to_send(product_id= product, quantity= quantity)

    def receive_orders(self, orders_to_receive):

        for transaction_id in orders_to_receive:
            self.set_actor_state(state=20, log_msg=f" Receiving transaction {transaction_id} " )
            if not self.receive_transaction(transaction_id ):
                return False
        return True


    def send_orders(self, orders_to_send):
        """ envia as encomendas pendentes
        """
        self.set_actor_state(state=40, log_msg="sending orders")

        orders_sent=set()
        orders_not_sent= set()

        without_stock_bool = False #! this variable is to save runtime, for multi product shold be removed
        # logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f"order_id}")
        for order in orders_to_send:
            if without_stock_bool:
                break

            order_id = self.get_order_id(order)
            ordered_quantity=self.get_ordered_quantity(order)
            logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f" a tentar enviar a order {order_id}")


            # se não existirem produtos suficientes para enviar a encomenda
            transaction_id = self.send_transaction(order_id )
            if transaction_id > 0:
                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f" order {order_id} enviada com sucesso na transaction {transaction_id}" )
                orders_sent.add(order_id)

            if transaction_id < 0 :                                                       #tenta enviar
                ordered_product= self.get_ordered_product(order)
                if self.manufacture_product(ordered_product, reference_quantity= ordered_quantity):
                    if self.send_transaction(order_id):        # tanta produzir, se conseguir envia logo
                        orders_sent.add(order_id)

                else:
                    orders_not_sent.add(order_id)
                    logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f"ERRO falhou o envio da order {order_id}" )
                    without_stock_bool= True

        if len(orders_not_sent) > 0:
            for order in orders_not_sent:
                self.actor_orders_record.set_order_state_to_waiting(order_id= order)
            logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="send_orders", file="actors", debug_msg= f" orders not sent {orders_not_sent}" )



    def execute_todays_orders(self):
        # self.set_actor_state(state=60, log_msg="executing todays orders")

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

        logs.new_log(state=self.actor_state, day=self.simulation.time, actor= self.id, file="actors", function="send_transaction",   debug_msg= f"tryng to send transaction of order {order_id}" )

        self.set_actor_state(state=31, log_msg="sending  transaction of order "+str(order_id) )
        day= self.simulation.time

        order=self.actor_orders_record.get_order_by_id(order_id)

        #time                 = order[0]
        product              = order[1]
        ordered_quantity     = order[2]
        client               = order[3]              #  ["Time", "Product", "Qty","Client","Order_id","Status", "notes"]


        if (ordered_quantity) ==0 :
            logs.new_log(state=self.actor_state, day=day, file="actors", actor=self.id, function="send_transaction",   debug_msg="ERROR, trying to order 0")
            raise Exception("\n\na tentar encomendar zero!!!!\n\n"+str(order))

        stock_quantity       = int(self.get_product_stock(product)) # verifica stock


        logs.new_log(state=self.actor_state, day=day, file="actors", actor=self.id, function="send_transaction",   debug_msg=" ordered qty:"+str(ordered_quantity)+" em stock: "+str(stock_quantity) )

        self.set_actor_state(state=32)

        if int(stock_quantity) < int(ordered_quantity):
            logs.new_log(state=self.actor_state, file="actors", function="send_transaction", actor=self.id, debug_msg= "send_transaction NAO ENVIVOU PORQUE NAO TINHA STOCK  Quantity ordered: "+str(ordered_quantity)+" stock: "+str(stock_quantity) )
            return -1


        self.set_actor_state(state=33, log_msg="Product with stock")

        logs.new_log(state=self.actor_state, day=self.simulation.time, actor= self.id, file="actors", function="send_transaction",   debug_msg= f"manage_stock IF stock_quantity > ordered_quantity order {str(order)} pruduct {str(product)}" )

        self.set_actor_state(state= 34, log_msg="Removing from inventary")

        # remove o enviado do inventário
        try:
            if self.actor_inventory.remove_from_inventory(product=product, quantity= ordered_quantity) is False:
                return False
        except:
            logs.new_log(state=self.actor_state, day=self.simulation.time, actor= self.id, file="actors", function="send_transaction",   debug_msg= f" send_transaction erro ao remover o enviado do inventário  order id: {str(order_id)}" )

            raise Exception("Não conseguiu remover do inventário depois de verificar que tinha stock")

        self.set_actor_state(state= 35, log_msg="adding to transasctions")
        #envia encomendas
        logs.new_log(state=self.actor_state, day=day, file="actors", actor=self.id, function="send_transaction",   debug_msg=" send_transaction trying to send transaction order id:"+str(order_id) )

        deliver_day = day+ math.ceil(self.get_deliver_time())
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
            "transit_time":-1,
            "lead_time": -1,
            "theoretical_lead": deliver_day - order_criation_day,
            "update_day": day,
            "transaction_id": -1,
            "delivered": 0,
                }

        transaction = self.simulation.ObejctTransationsRecords.add_transaction(transaction_info)


        if transaction is False:
            raise Exception("Não conseguiu criar a transação")

        self.set_actor_state(state=36, log_msg="removing from orders")
        #remove from open orders
        self.actor_orders_record.close_order(order_id )

        self.remove_from_stock_scheduled_to_send(product_id=product, quantity=ordered_quantity)

        logs.new_log(state=self.actor_state, file="actors", function="send_transaction", actor=self.id, debug_msg= f"Transaction SUCECESSFULLY SENDED !!!  transaction id:{str(transaction)} order id:{str(order_id)}")
        self.set_actor_state(state=37, log_msg="Orders sending complete")
        return transaction




    def receive_transaction(self, transaction_id):
        """
        Recebe os productos de uma encomendas
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
        self.set_actor_state(state= 6, log_msg="Receiving transaction")
        transaction = self.get_transactions_by_id(transaction_id)

        product              = transaction["product"]
        ordered_quantity     = transaction["quantity"]
        inventory_capacity   = self.actor_inventory.refresh_inventory_capacity()

        #verifica capacidade
        if (int(inventory_capacity) + int(ordered_quantity)) > int(self.max_inventory):
            self.set_actor_state(state= 7, log_msg="sem espaço para receber encomendas")
            return False

        self.set_actor_state(state= 8, log_msg="recording transaction reception")

        #adiciona ao inventário
        if not self.actor_inventory.add_to_inventory(product, ordered_quantity):
            raise Exception("Error, could not add to inventory")

        # regista que recebeu
        self.simulation.ObejctTransationsRecords.update_transaction(transaction_id)

        if sim_cfg.SIMULATION_MODE == 1:
            self.add_to_received_transactions(transaction=transaction_id)
            self.remove_from_stock_scheduled_to_arrive(product_id=product, quantity= ordered_quantity)

        self.set_actor_state(state= 9, log_msg=" Finished transcaction reception")

        logs.new_log(state=self.actor_state, file="actors", function="receive_transaction", day=self.simulation.time, actor=self.id, debug_msg= f"  Transaction SUCECESSFULLY received id: {transaction_id}" )




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
        self.set_actor_state(state = 54, log_msg="manufacture_product {}".format(product))

        if not isinstance(product, int):
            raise Exception("product must be an int")


        if str(product)[0] in self.get_root_actors():
            logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= f"  " )
            # self.actor_inventory.add_to_inventory(product=product, quantity = 999999)
            return True

                #raise Exception("tring to manufacture in the end of supply chain ")

        self.set_actor_state(state= 42 ,  log_msg=" trying to manufacture product {} ref quantity: {}".format(str(product), str(reference_quantity)))

        logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg=  "manufacture_product actor:"+str(self.name) + " product " +str(product) )
        recepe = self.simulation.cookbook[product]
        present_inventory_capacity = self.actor_inventory.present_capacity
        max_max_inventory_capacity = self.max_inventory

        def get_max_production(product, recepe):
            self.set_actor_state(state= 43, log_msg=" Calculating max possible production")

            logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= "manufacture_product - get_max_production actor:"+str(self.name) + " product " +str(product) + "composition: "+str(recepe))

            production_matrix=[]

            for raw_material_id in recepe:

                in_stock =  self.get_product_stock(raw_material_id )
                production_matrix.append(
                    # product id,                   #ratio
                    [raw_material_id ,  in_stock  // int(recepe[raw_material_id])    ])

                RL_id, min  = production_matrix[0]

            min_qty = math.floor(production_matrix[0][-1])

            for el in production_matrix:
                if el[-1] < min_qty:
                    min_qty, RL_id =el[-1], el[0]

                if not isinstance(min_qty,int): raise "Manuracture_error on min_qty data type"
            logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= "manufacture_product - get_max_production max "+str(min_qty) +" RL "+ str(RL_id) )
            return min_qty , RL_id

        max_prod , Limiting_reagent = get_max_production(product= product, recepe=recepe)

        #teste para verificar que a produção n supera o inventários # para csasos em que 1u de mp origina mais de 1u de produto
        if (max_prod + present_inventory_capacity) > max_max_inventory_capacity:
            max_prod = max_max_inventory_capacity - present_inventory_capacity

            logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= " ERRO manufacture_product producao de {} limitada a {} por limitacoes de stock".format(str(product), str(max_prod)))

        elif max_prod == 0:
            self.set_actor_state(state= 44, log_msg="actor {} Witout raw material {}".format(self.id, Limiting_reagent))
            return False

        elif reference_quantity > max_prod:
            self.set_actor_state(state= 44, log_msg="actor {} Witout enough raw material for order {}".format(self.id, Limiting_reagent))
            return False

        elif self.production(product, quantity=max_prod, recepe = recepe):
            self.set_actor_state(state= 48, log_msg=" Manutacture finished with sucess")
            return True

        #!todo rever isto
        # raise Exception("Erro na manufatura, não returnou produção nem falta de stock")

    def production(self, product, quantity, recepe):
        #print(type(product), type(quantity), type(recepe))
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

        self.set_actor_state(state= 45, log_msg=" production order placed for {} units of {}".format(str(quantity), str(product) ) )
        logs.new_log(state=self.actor_state, file="actors", function="manufacture_product", day=self.simulation.time, actor=self.id, debug_msg= "manufacture_product - in production - actor "+str(self.id) +" Pd "+ str(product)+" qty "+ str(quantity)+" recepe "+ str(recepe) )
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
            self.set_actor_state(state= 46, log_msg=" A converter ingredientes")

            # remove raw material from inventory
            for i  in raw_material:
                self.actor_inventory.remove_from_inventory(product=i[0] , quantity = i[1])
            # add new to inventory

                    #adiciona ao inventário
            if not self.actor_inventory.add_to_inventory(product=product, quantity = quantity):
                raise Exception("Error, could not add to inventory in production")

            self.set_actor_state(state= 48, log_msg=" Production Finished")
            return True
        else:
            raise Exception("ERRO NA PRODUÇÃO, SE EXISTE UM ERRO AQUI A QUANTIDADE MÁXIMA ESTÁ A SER MAL CALCULADA")


    def check_orders_above_safety(self):
        """Se o ator receber uma encomenda para o qual não tenha stock mas esta esteja acima do safety stock
        não vai enviar pq não tem stock mas não encomenda materia prima porque não atingio o safety stock
        ["Time", "Product", "Qty","Client","Order_id","Status"]
        """
        #history=self.simulation.mongo_db.get_actor_orders(self.id)
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



    def get_orders_received_today(self):
        """
            Devolve uma lista com as encomendas recebidas hoje
        """
        return self.actor_orders_record.get_orders_history(history_days=0)




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
    def manage_orders(self):
        # print(self.id,self.actor_orders_record.orders_waiting_stock)
        """ gere as ordens de encomenda,
        tem um sistema de estados para evidar rotas incorrecta e para facilitar a analise dos logs

        """

        self.set_actor_state(state = 10, log_msg="Checking transctions to receive" )
        logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"actor id: {self.id}" )

        # orders          =   self.actor_orders_record.open_orders_record
        # max_capacity    =   self.actor_inventory.max_capacity
        # inventory       =   self.actor_inventory.main_inventory


        # verifica se tem encomendas para RECEBER       ######################################

        to_receive = self.get_delivering_transactions()

        logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg=f"Encomendas para receber: {str(to_receive)}")

        if len(to_receive)>0 :
            self.set_actor_state(state = 12, log_msg=f"has { len(to_receive)} order to receive" )
            self.receive_orders(to_receive)



        # verifica se tem encomendas para Enviar       ######################################
        self.set_actor_state(state = 30, log_msg="Checking transctions to send with mode: ")

        orders_to_send = self.get_orders_to_send()


        if orders_to_send:
            logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"encomendas para enviar: { str(orders_to_send)}" )
            self.send_orders(orders_to_send)

        else:
            logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="manage_orders", file="actors", debug_msg= f"sem ncomendas para enviar: { str(orders_to_send)}" )

        self.set_actor_state(state = 49, log_msg=str(len(orders_to_send))+" Orders sent from stock ")

        return True



    
    def manage_stock(self):
        """
        Executado depois da destão de encomendas
        verifica se algum dos productos está abaixo do stock minimo
        """
        self.set_actor_state(state = 50, log_msg=" maganing stock")

        if self.id in self.get_root_actors():
            self.set_actor_state(state = 90, log_msg=str("o actor{} está no fim da cadeia, o estado vai alterar para terminado 90".format(self.id)))
            #get inventory
            logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="manage_stock", file="actors", debug_msg= f"actor: {self.id} detected, state chenged to 80" )
            
            root_rm = self.get_root_raw_material()
            if self.actor_inventory.get_product_stock(product_id = root_rm ) < 1000_0000_000:
                #if inventory is below min_stock, order MP
                
                self.actor_inventory.set_product_inventory(product_id = root_rm, new_quantity= 1000_000_000)
            return True

        self.stock_otimization()
        self.set_actor_state(state = 40, log_msg=str("| STATE          | actors        | manage_stock      Actor {} Started stock management".format(self.id)))


        return True

    def manufacture_all(self):
        """manufacture all products in products list"""
        for product_id in self.products_list:
            self.manufacture_product(product_id)






    def stock_otimization(self):
        self.set_actor_state(state = 51, log_msg="stock_otimization started")
        if self.simulation.stock_management_mode == 1:
            self.traditional_stock_management()
            return 1
        else:
            self.blockchain_stock_management()
            return 3


    def traditional_stock_management(self):
        self.set_actor_state(state = 52, log_msg="stock_otimization started")

        # waiting_stock = self.actor_orders_record.get_waiting_stock()


        #para cada um dos produtos
        for product in self.get_actor_product_list():
            self.set_actor_state(state = 53, log_msg="managing product {}".format(product))

            ordered_stock = self.get_waiting_stock(product_id=product)


            #tenta produzir o que pode
            self.manufacture_product(product) # converte tudo o que pode em stock

            order_point =  self.get_product_safety_stock(product)
            present_stock = self.get_product_stock(product=product)
            # waiting_stock = self.get_waiting_stock(product_id=product)

            #verifica se chegou ao stock se segurança
            if present_stock + ordered_stock  > order_point:
                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="traditional_stock_management", file="actors", debug_msg= f"product {product} stock {present_stock}+ ordered_stock:{ordered_stock} > order point {order_point}" )


            if present_stock + ordered_stock  <= order_point:
                
                
                self.set_actor_state(state = 54, log_msg="stock inferior ao safety ")
                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="traditional_stock_management", file="actors", debug_msg= f"product {product} stock {present_stock}+ ordered_stock:{ordered_stock} < order point {order_point}" )


                # get order quantity

                # valida se chegou ao stock de segurança

                # self.check_safety_inveotry()
                #valita de tem todos os parametros necessários
                parameters= []

                #analisa o stock dos ultimos dias
                orders_stats = self.get_orders_stats(product=int(product), reorder_history_size= self.reorder_history_size)

                if orders_stats:
                    avg_demand, deviation_demand = orders_stats
                    parameters.append(f"orders_stats {orders_stats}")

                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="traditional_stock_management", file="actors", debug_msg= f"oders stats {orders_stats}" )


                # analisa as tansações


                transasctions_stats = self.get_delivery_stats(product_id=product)
                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="traditional_stock_management", file="actors", debug_msg= f"transasctions_stats {transasctions_stats}" )
                if not transasctions_stats:
                    transasctions_stats = self.get_product_default_delivery_stats(product_id=product)

                if transasctions_stats:
                    avg_delivery_time, deviation_delivery_time = transasctions_stats
                    parameters.append(f"transactions_stats {transasctions_stats}")

                if self.safety_factor:
                    parameters.append(f"safety_factor {self.safety_factor}")

                logs.new_log(state=self.actor_state, actor=self.id, day=self.simulation.time, function="traditional_stock_management", file="actors", debug_msg= f"parameters {parameters}" )
                # if parameters < 5 and self.simulation.time > 100:
                #     raise Exception("Erro no stock otimization, falta de parametros para calcular o stock")

                if len(parameters) < 3:
                    logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg=f"ERROR, missing parameters to calculate order {parameters}")
                    continue

                logs.new_log(state=self.actor_state, actor=self.id, file="actors", function="traditional_stock_management", day=self.simulation.time,
                            debug_msg=f" avg_demand: {avg_demand} deviation_demand: {deviation_demand} avg_delivery_time: {avg_delivery_time} deviation_delivery_time: {deviation_delivery_time}  safety_factor: {self.safety_factor}")

                if len(parameters) == 3:
                    self.set_actor_state(state = 56, log_msg=f"calculating order  with 5 prameters: {parameters}")
                    new_delivery_quantity  = self.get_order_quantity(avg_demand = avg_demand,
                                                                deviation_demand = deviation_demand,
                                                                avg_delivery_time = avg_delivery_time,
                                                                deviation_delivery_time = deviation_delivery_time,
                                                                safety_factor = self.safety_factor)



                # se não consegiu calcular, usa o default safety stock

                else:
                    self.set_actor_state(state = 57, log_msg="calculating order - without parameters")
                    new_delivery_quantity = self.get_product_safety_stock(product_id=product)

            #prepara a encomendas
            #vai ver a composição
            #manda vir a quantidade necessária para o new_delivery_quantity
                order_info = self.get_order_preparation(product_quantity= new_delivery_quantity, product_id=product)
                logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg=f"order infor {order_info}")

                for product_order in order_info:

                    if not self.place_order(product_order["product_id_to_order"], quantity = product_order["quantity_to_order"]):
                        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg="ERROR, order not placed!!!")
                    self.update_product_waiting_stock(product_id=product, quantity = new_delivery_quantity)

            self.update_safety_stock(product_id=product) #atualiza o stock de segurança
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="traditional_stock_management", file="actors", debug_msg="funcion exit")
        return True
        # self.actor_inventory.set_product_safety_stock(product_id= self.id*1000+1, quantity = int(new_delivery_quantity) )

    # def prepare_order()

    def blockchain_stock_management(self):
        '''Manage orders by sharing information'''
        self.set_actor_state(state = 60, log_msg="blockchain_stock_management started")
        
        #for actor in actors_colection:
        if self.id == 1:
            logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="blockchain_stock_management", file="actors", debug_msg="ACTOR 1 INSIDE BC STOCK MANAGEMENT ")
            
            for order in self.get_orders_received_today():
                for actor_id in self.simulation.Object_supply_chain.get_middle_of_chain_actors():
                    product_id= actor_id*1000+1
                    self.place_order(product_id= product_id  ,
                                            quantity= int(self.get_ordered_quantity(order=order)*1.5),
                                            client= int(actor_id)-1)
                    self.set_order_state_to_processed(order_id = self.actor_orders_record.get_order_id(order=order))
            
            
        # for product in self.products_list:
        #     # self.correct_safety_stock(product_id=product)
        #     safety_stock = self.get_product_safety_stock(product=product)
            
        #     if (self.get_product_stock(product) + self.get_waiting_stock(product_id=product)) < safety_stock:
        #         order_info = self.get_order_preparation(product_quantity= safety_stock, product_id=product)
        #         logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="blockchain_stock_management", file="actors", debug_msg=f"order info {order_info}")

        #         for product_order in order_info:

        #             if not self.place_order(product_order["product_id_to_order"], quantity = product_order["quantity_to_order"]):
        #                 logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="blockchain_stock_management", file="actors", debug_msg="ERROR, order not placed!!!")
        #             self.update_product_waiting_stock(product_id=product, quantity = safety_stock)
            
        return True
        
      
    def correction_function(self, stock, total,  slope_sign ):
        if total == 0:
            if np.sum(self.daily_open_orders[-1:]) == 0:
                return stock*.50
            if np.sum(self.daily_open_orders[-2:]) == 0:
                return stock*.40
            if np.sum(self.daily_open_orders[-3:]) == 0:
                return stock*.30
            if np.sum(self.daily_open_orders[-4:]) == 0:
                return stock*.20
            if np.sum(self.daily_open_orders[-5:]) == 0:
                return stock*.10
            if np.sum(self.daily_open_orders[-6:]) == 0:
                return stock*.02
            
        #     correction  = stock *   slope_sign*0.5
        if slope_sign > 0:
            return stock *1.25
        
        if slope_sign < 0:
            return stock*.75
        # return stock *   slope_sign* math.log(total)
        
    def correct_safety_stock(self, product_id):
        old_stock = self.get_product_safety_stock(product=product_id)
        total_open_orders = len(self.get_open_orders())
        wainting_stock = self.get_waiting_stock(product_id=product_id)
        
        if (old_stock == 0) and (total_open_orders >0):
            self.set_product_safety_stock(product_id=product_id, quantity= self.get_orders_stats(product=product_id, reorder_history_size = 5)[0])
            print(f"\ncorrect_safety_stock: {product_id}: {int(self.get_product_safety_stock(product=product_id))} {total_open_orders}")
            return True
        print(f"\ncorrect_safety_stock: {product_id}: {int(self.get_product_safety_stock(product=product_id))} {total_open_orders}")
            
            
            
        self.daily_open_orders = np.append(self.daily_open_orders, total_open_orders)
                
        if len(self.daily_open_orders) < 2:
            corrected_value = self.get_orders_stats(product=product_id,reorder_history_size = 5)[0]
            return True
        
        if self.daily_open_orders[-2] > 1:
            if (self.daily_open_orders[-1] - self.daily_open_orders[-2]) == 0:
                slope_sign = 1
            else:
                slope_sign = np.divide( (self.daily_open_orders[-1]-self.daily_open_orders[-2]), (abs(self.daily_open_orders[-1]-self.daily_open_orders[-2])) )
        else:
            slope_sign = 1
 
        corrected_value = self.correction_function(stock = self.get_product_safety_stock(product=product_id), total = total_open_orders, slope_sign = slope_sign)
        if corrected_value > wainting_stock:
             corrected_value = self.get_orders_stats(product=product_id,reorder_history_size = 5)[0]
        logs.new_log(state=self.actor_state, day=self.simulation.time, actor=self.id, function="correct_safety_stock", file="actors", debug_msg= f"corrected value {corrected_value}, slope sign {slope_sign}, total open orders {total_open_orders}, daily open orders {self.daily_open_orders}")
        self.set_product_safety_stock(product_id=product_id, quantity=corrected_value)
        
        
    