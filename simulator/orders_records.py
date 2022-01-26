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
        #             1-sended
        #             8- waiting for order raw_material
        #             9- waiting raw material
        #Acho que o nome n vai servir para nada,
        # columns = ["Criation Time", "Product", "Qty","Client","Order_id","Status","Notes"]

        columns = [-1, -2, -3, -4, -5, -6 ,-7]
        self.Open_Orders_Record = [columns]
        self.closed_orders_record = [columns]  #Já existe um outro registo do histórico, isto deve perder a função
        self.orders_history=[]
        self.orders_waiting_stock = []         #vai guardar as orders abertas que não foram enviadas por falta de stock

        # self.order_history=np.

        logs.log(info_msg="| CREATED OBJECT   | Order_record  actor:"+str(self.actor))

    """
    Getters
    """ 


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
            return order[-3]
        if order_id:
            return self.get_order_by_id(order_id=order_id)[-3]

    def get_order_by_id(self, order_id):
        # order_record = False
        records_found = 0
        for order in self.Open_Orders_Record:
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

    def get_orders_waiting_stock(self):
        return  self.orders_waiting_stock

    def get_orders_sequence(self):
        def get_id(l):
                return l[-3]

        open_orders = self.Open_Orders_Record
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

    # def get_ordered_products(self,time_interval=None):
    #     history=self.get_history(time_interval,product=None)
    #     logs.log(debug_msg="Ordered products: "+history.shape[0]-1)
    #     return history.shape[0]-1


        """
        Setters
        """
    def add_to_orders_waiting_stock(self, order=None, order_id=None):
        logs.log(debug_msg="| FUNCTION         | orders        | add to wainting orders       ")

        if not (isinstance(order, list) or isinstance(order_id,int)):
            for el in inspect.stack():
                print(el)

        if order_id:
            # self.orders_waiting_stock.append(order_id)
            self.set_order_status(order_id= order_id, status=8)
        if order:
            order_id=self.get_order_id(order=order)

            # self.orders_waiting_stock.append(order_id)
            self.set_order_status(order_id=order_id, status=8)

    def set_order_processed(self, order=None, order_id=None):
        if order_id:
            self.set_order_status(order_id= order_id, status=9)
        if order:
            self.set_order_status(order_id= order[-3], status=9)



    def set_order_status(self, order_id, status):
        for order in self.Open_Orders_Record:
            if order[-3] == order_id:
                order[-2] = status

    def refresh_orders_waiting_stock(self):
        logs.log(debug_msg="| FUNCTION         | Orders_records| Refresh waiting orders")

        new_list=[]
        for open_order in self.Open_Orders_Record:
            if self.get_order_status(order=open_order) in [0,8]:
                new_list.append(self.get_order_id(order= open_order))

        self.orders_waiting_stock = new_list

        # print("templ",new_list)

    def add_to_open_orders(self,  product, qty, client, notes=None):
        logs.log(debug_msg="| FUNCTION         | Orders_records| add_to_open_orders with parameters: time:" + str(self.actor.simulation.time ) + " product: "+ str(product) + " Qty " + str(qty) + "from " + str(self.actor.id) + " Client: "+ str(client))
        # actor_id = self.actor

        if notes is None:
            notes={}

        self.last_order_id = self.last_order_id + 1   #! Está aqui um possivel erro, last order_id = last_order+1, mas tmb pode estar certo
        #initial status = 0
        #print("temp adding order", self.last_order_id)

           #   0                 1       2       3        4        5        6
        #[ creation Time,  Product , Qty , Client , Order_id, Status, notes]
        to_add = [self.actor.simulation.time  ,product, qty,  client, self.last_order_id, 0,notes]

        if self.get_order_by_id( self.last_order_id) is not False:
            print("add_to_open_orders",self.get_order_by_id( self.last_order_id))
            raise Exception("ordem duplicada")

        self.orders_history.append(to_add)
        self.Open_Orders_Record.append(to_add)
        self.actor.simulation.update_simulation_stats("orders_opened")

        logs.log(debug_msg="| ORDERED ADDED    | Orders_records| Order added to {} of qty {} of Product:{} ordered from:{}".format(self.actor.id, qty, product, client))


        self.actor.simulation.mongo_db.add_order_to_db(actor_id = self.actor.id,
                                                       time = self.actor.simulation.time ,
                                                       product = product,
                                                       quantity = qty,
                                                       client = client,
                                                       order_id=self.last_order_id,
                                                       status= 0 )

        self.check_orders_integrity()  #TODO acho que isto n devia estar aqui mas sim no remove


    def remove_from_open_orders(self,  order_id):
        time = self.actor.simulation.time

        def check_open_orders_sequence():
            def get_id(l):
                return l[-3]
            open_orders = self.Open_Orders_Record
            open_orders.sort(key=get_id)


            # return open_orders
            # order_sequence=check_open_orders_sequence()

            for i in open_orders:
                if i[-3] == -5:
                    continue
                if i[-3] < order_id:
                    print(inspect.stack())
                    raise Exception("ERRO",i[-3] ,"<", order_id)
            check_open_orders_sequence()

        for record in self.Open_Orders_Record:
            if record[-3] == order_id:
                record[0] = time
                self.Open_Orders_Record.remove(record)
                self.closed_orders_record.append(record)
                order= self.get_order_by_id(order_id=order_id )


                #self.add_to_orders_log( product=order[1], quantity=order[2], client= order[3], order_id=order[-3], status =1)
                self.actor.simulation.mongo_db.close_order_on_db(actor_id=self.actor.id, order_id=order[-3])
                self.actor.simulation.update_simulation_stats("orders_closed")

        self.refresh_orders_waiting_stock()
        logs.log(debug_msg="| FUNCTION         | Orders_records| remove_from_open_orders order "+str(order_id)+" removed from actor "+str(self.actor.id)+str(self.Open_Orders_Record))


    def check_orders_integrity(self):
        if self.actor.simulation.order_priority == "fifo":
            open_orders = self.Open_Orders_Record
            cloed_orders= self.closed_orders_record

            def get_id(l):
                return l[-3]

            open_orders.sort(key=get_id)
            cloed_orders.sort(key=get_id)

            def check_sequence(order_list):

                if len(order_list)>1:
                    for i in range(0,len(order_list)-2,1):
                        if order_list[i][-3] == -5:
                            continue
                        if order_list[i][-3]+1 != order_list[i+1][-3]:
                            print("check:",order_list[i][-3] +1 , order_list[i+1][-3])
                            for el in open_orders:
                                print(el)
                            for el in cloed_orders:
                                print(el)
                            raise Exception("inconsistencia in "+str(order_list))


        # #print("open orders")
        # check_sequence(open_orders)
        # #print("closed orders")
        # check_sequence(cloed_orders)

    def get_orders_stats(self, history_size=0):
        """ 
        copia o histórico de encomendas,
        extai a coluna das quantidades
        retorna a média e o std
        """
        orders_array = np.array(self.orders_history[-history_size:])
        if len(orders_array) == 0:
            return
        orders_array=np.array(orders_array[:,2])
        return orders_array.mean() , orders_array.std()
    
    def get_orders_history(self, history_cut=0):
        """ 
        copia o histórico de encomendas,
        extai a coluna das quantidades
        retorna a média e o std
        """
        return self.orders_history[-history_cut:]
  