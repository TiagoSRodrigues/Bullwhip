import math
from re import A
from . import logging_management as logs
import simulation_configuration as sim_cfg
import numpy as np
import inspect
logs.log(debug_msg="Started Order_records.py")

############################################################################################
#       Classe dos regitos individuais dos actores                                         #
############################################################################################
class ClassOrdersRecord:
    def __init__(self,actor ):
        self.actor = actor
        self.last_order_id = self.actor.id * 10**6       #tracks the last product id

        #Status order 0-Received
        #             1 - sended
        #             5 - waiting for order raw_material
        #             9 - sended

        #Acho que o nome n vai servir para nada,
        # columns = ["Criation Time", "Product", "Qty", "Client", "Order_id", "Status", "Notes"]
        # columns = [        0,            1       2      3           4           5        6   ]


        columns = [-1, -2, -3, -4, -5, -6 ,-7]
        self.open_orders_record = [columns]
        self.closed_orders_record = [columns]  #Já existe um outro registo do histórico, isto deve perder a função
        self.orders_history=[]
        self.orders_waiting_stock = set()       #vai guardar as orders abertas que não foram enviadas por falta de stock

        # self.order_history=np.

        logs.new_log(file="orders_records", actor=self.actor.id, function="constructor", debug_msg= f" orders records created : {self.actor.id}")

        #                                  """
        #                                  doh




        #                                                                                  tttt
        #                                                                              ttt:::t
        #                                                                              t:::::t
        #                                                                              t:::::t
        #                                  ggggggggg   ggggg    eeeeeeeeeeee    ttttttt:::::tttttttttttttt
        #                                  g:::::::::ggg::::g  ee::::::::::::ee  t:::::::::::::::::tt:::::
        #                                  g:::::::::::::::::g e::::::eeeee:::::eet:::::::::::::::::tt::::
        #                                  g::::::ggggg::::::gge::::::e     e:::::etttttt:::::::tttttttttt
        #                                  g:::::g     g:::::g e:::::::eeeee::::::e      t:::::t
        #                                  g:::::g     g:::::g e:::::::::::::::::e       t:::::t
        #                                  g:::::g     g:::::g e::::::eeeeeeeeeee        t:::::t
        #                                  g::::::g    g:::::g e:::::::e                 t:::::t    tttttt
        #                                  g:::::::ggggg:::::g e::::::::e                t::::::tttt:::::t
        #                                  g::::::::::::::::g  e::::::::eeeeeeee        tt::::::::::::::t
        #                                  gg::::::::::::::g   ee:::::::::::::e          tt:::::::::::tt
        #                                      gggggggg::::::g     eeeeeeeeeeeeee            ttttttttttt
        #                                              g:::::g
        #                                  gggggg      g:::::g
        #                                  g:::::gg   gg:::::g
        #                                  g::::::ggg:::::::g
        #                                  gg:::::::::::::g

        #                                  """


    def get_order_criation(self, order=None, order_id=None):
        if order:
            return order[0]
        elif order_id:
            return self.get_order_by_id(order_id=order_id)[0]

    def get_order_status(self,order=None, order_id=None):
        if order:
            return order[-2]
        if order_id:
            return self.get_order_by_id(order_id=order_id)[-2]
    def get_order_status(self,order=None, order_id=None):
        if order:
            return order[-2]
        if order_id:
            return self.get_order_by_id(order_id=order_id)[-2]

    def get_order_id(self,order=None, order_id=None):
        if order:
            return int(order[-3])
        if order_id:
            return int(self.get_order_by_id(order_id=order_id)[-3])

    def get_order_by_id(self, order_id):
        records_found = 0
        for order in self.open_orders_record:
            if order[-3]==order_id:
                order_asked = order
                records_found+=1

        for order in self.closed_orders_record:
            if order[-3]==order_id:
                order_asked = order
                records_found+=1

        if records_found >1:
            logs.log(debug_msg="| FUNCTION         | Orders_records| get_order_by_id  ERROR order found in two places at same time! order_id:{}  actor: {}".format(order_id, self.actor.id))
            raise Exception("encomenda dupicada")
        if records_found >0:
            return order_asked
        return False

    def get_order_quantity(self, order=None, order_id=None):
        if order:
            return order[2]
        if order_id:
            return self.get_order_by_id(order_id=order_id)[2]

    def get_waiting_stock(self):
        stock = 0
        for order in self.orders_waiting_stock:
            stock += self.get_order_quantity(order_id=order)
        return stock

    def get_orders_waiting_stock(self):
        return self.orders_waiting_stock
        
    def get_orders_sequence(self):
        def get_id(l):
            return l[-3]

        open_orders = self.open_orders_record
        open_orders.sort(key=get_id)

        sequence=[]
        for order in open_orders:
            if order[-3] == -5:
                continue
            sequence.append(order[-3])
        sequence.sort()
        return sequence

    def get_fist_open_order_id(self):
        orders_sequence = self.get_orders_sequence()
        if len(orders_sequence) > 0:
            return self.get_orders_sequence()[0]
        return False

    def get_product_orders(self,  product, orders_list):
        orders = []
        for order in orders_list:
            if order[1] == product:
                orders.append(order)
        return orders



    def get_orders_stats(self, product, history_days= None):
        """
        copia o histórico de encomendas,
        extai a coluna das quantidades
        retorna a média e o std
        """


        orders_array = np.array(self.get_orders_history(history_days))
        product_history = self.get_product_orders(product=product, orders_list = orders_array)



        if len(product_history) < 1:
            return False
        # print(orders_array  )

        orders_values=orders_array[:,2]

        orders_avg = math.ceil(orders_values.mean())
        orders_std = math.ceil(orders_values.std())
        logs.new_log(file="orders_records", actor=self.actor.id, function="get_orders_stats", debug_msg= f"history:{history_days} orders_avg: {str(orders_avg)} orders_std:{str(orders_std)}")

        return orders_avg, orders_std

    def get_orders_history(self, history_days=0):
        """
        extrai todas as encomendas do entro do intervalo temporal
        """
        if history_days is None:
            return self.orders_history

        orders = []
        for order in self.orders_history:
            if self.actor.simulation.time - order[0]  <= history_days:
                orders.append(order)
        return orders



        #                                        """                                         tttt
                                                                                       # ttt:::t
                                                                                       # t:::::t
                                                                                       # t:::::t
                                                   # ssssssssss       eeeeeeeeeeee    ttttttt:::::ttttttt
        #                                        ss::::::::::s    ee::::::::::::ee  t:::::::::::::::::t
        #                                        ss:::::::::::::s  e::::::eeeee:::::eet:::::::::::::::::t
        #                                        s::::::ssss:::::se::::::e     e:::::etttttt:::::::tttttt
        #                                        s:::::s  ssssss e:::::::eeeee::::::e      t:::::t
        #                                        s::::::s      e:::::::::::::::::e       t:::::t
                                                   # s::::::s   e::::::eeeeeeeeeee        t:::::t
        #                                        ssssss   s:::::s e:::::::e                 t:::::t    tttttt
        #                                        s:::::ssss::::::se::::::::e                t::::::tttt:::::t
        #                                        s::::::::::::::s  e::::::::eeeeeeee        tt::::::::::::::t
        #                                        s:::::::::::ss    ee:::::::::::::e          tt:::::::::::tt
        #                                        sssssssssss        eeeeeeeeeeeeee            ttttttttttt

        #                                        """


    def set_order_state_to_waiting(self, order=None, order_id=None):
        logs.new_log(file="orders_records", actor=self.actor.id, function="set_order_state_to_waiting", debug_msg= f"order: {order} order id {order_id}")

        if not (isinstance(order, list) or isinstance(order_id,int)):
            raise Exception("set_order_state_to_waiting: order or order_id must be a list or int")

        if order_id:
            self.orders_waiting_stock.add(order_id)
            self.set_order_status(order_id= order_id, status=6)
        if order:
            order_id=self.get_order_id(order=order)
            self.orders_waiting_stock.add(order_id)
            self.set_order_status(order_id=order_id, status=6)


    def set_order_state_to_processed(self, order=None, order_id=None):
        if order_id:
            self.set_order_status(order_id= order_id, status=9)
        if order:
            self.set_order_status(order_id= order[-3], status=9)


    def set_order_status(self, order_id, status):
        for order in self.open_orders_record:
            if order[-3] == order_id:
                order[-2] = status


    def add_to_open_orders(self,  product, qty, client, notes=None):
        if notes is None:
            notes={}


        self.last_order_id += 1  
     

           #   0                 1       2       3        4        5        6
        #[ creation Time,  Product , Qty , Client , Order_id, Status, notes]
        to_add = [self.actor.simulation.time  ,product, qty,  client, self.last_order_id, 0,notes]

        if self.get_order_by_id(self.last_order_id) is not False:

            logs.new_log(day=self.actor.simulation.time, actor=self.actor.id, function="add_to_open_orders", file="actors" , debug_msg= "ERROR Ordem duplicada product {product} quantity {qty} client {client} notes {notes}  ")
            raise Exception("ordem duplicada")

        self.orders_history.append(to_add)
        self.open_orders_record.append(to_add)

        logs.new_log(day=self.actor.simulation.time, actor=self.actor.id, function="add_to_open_orders", file="actors" , debug_msg= f" ORDERED ADDED  product {product} quantity {qty} client {client} notes {notes} | order id {self.last_order_id} ")
        # print(f" ORDERED ADDED  product {product} quantity {qty} client {client} notes {notes} | order id {self.last_order_id} ")
        self.actor.simulation.mongo_db.add_order_to_db(actor_id = self.actor.id,
                                                       time = self.actor.simulation.time ,
                                                       product = product,
                                                       quantity = qty,
                                                       client = client,
                                                       order_id=self.last_order_id,
                                                       status= 0 )

        self.check_orders_integrity()
        self.actor.simulation.update_simulation_stats("orders_opened")
        logs.append_line_to_file(file_path=f"{self.actor.simulation.simulation_results_folder}orders_open_actor_{self.actor.id}_{self.actor.simulation.simulation_id}.csv", line=f"{','.join(str(e) for e in to_add)},\n")


    def close_order(self,  order_id):
        #
        time = self.actor.simulation.time

        def check_open_orders_sequence():
            def get_id(l):
                return l[-3]
            open_orders = self.open_orders_record
            open_orders.sort(key=get_id)


            # return open_orders
            # order_sequence=check_open_orders_sequence()

            for i in open_orders:
                if i[-3] == -5:
                    continue
                if i[-3] < order_id:
                    logs.new_log(file="orders_records", actor=self.actor.id, function="close_order", debug_msg= f"ERRO no oder id")
                    raise Exception("ERRO",i[-3] ,"<", order_id)

            check_open_orders_sequence()

        for record in self.open_orders_record:
            if record[-3] == order_id:
                record[0] = time
                record[-2] = 9              #set_order_state_to_processed
                self.open_orders_record.remove(record)
                self.closed_orders_record.append(record)
                order= self.get_order_by_id(order_id=order_id )

                self.actor.simulation.update_simulation_stats("orders_closed")
                self.orders_waiting_stock.discard(order_id)
                #self.add_to_orders_log(product=order[1], quantity=order[2], client= order[3], order_id=order[-3], status =1)
                self.actor.simulation.mongo_db.close_order_on_db(actor_id=self.actor.id, order_id=order[-3])
                logs.append_line_to_file(file_path=f"{self.actor.simulation.simulation_results_folder}orders_closed_actor_{self.actor.id}_{self.actor.simulation.simulation_id}.csv", line=f"{','.join(str(e) for e in record)},\n")

        self.check_orders_integrity()
        logs.new_log(file="orders_records", actor=self.actor.id, function="close_order", debug_msg= f"close_order order {str(order_id)} removed from actor {str(self.actor.id)} {str(self.open_orders_record)}")


    def check_orders_integrity(self):
       # verifica se as encomeendas estão por ordem de id
        open_orders = self.open_orders_record
        closed_orders= self.closed_orders_record

        def get_id(l):
            return l[-3]

        open_orders.sort(key=get_id)
        closed_orders.sort(key=get_id)

        def check_sequence(order_list, list_name):
            inial_list= []
            if len(order_list)>1:
                 for i in range(len(order_list)):
                    inial_list.append(self.get_order_id(order_list[i]))


            sorted_list= sorted(inial_list)
            if sorted_list != inial_list:
                raise Exception(f"integrity error in {list_name} -> {order_list} ")

            #     #se for o header passa à frente
                #     if order_list[i][5] < 0:
                #         continue

                #     #compara 2 a 2 se o segundo vem a seguir ao primeito (1, 2 -> ok 1,3 -> not ok)
                #     a=order_list[i][-3]
                #     b=order_list[i+1][-3]

                #     if a+1 != b:
                #         self.actor.simulation.export_db(sim_cfg.FINAL_EXPORT_FILES_PATH)

                #         print(f"ERRO NA SEQUENCIA DE ORDENS {1+a} != { b}")

                #         for order in order_list:
                #             print(f"{order} -> {order_list[i][5]}")


        # #print("open orders")
        check_sequence(open_orders, "open_orders")
        # #print("closed orders")
        check_sequence(closed_orders, "closed_orders")
        logs.new_log(file="orders_records", actor=self.actor.id, function="check_orders_integrity", debug_msg= f"order integrity checked!! ok!")


