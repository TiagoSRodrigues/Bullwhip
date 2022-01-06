from typing import Sequence
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

        #Status order 0-Received 1-sended
        #Acho que o nome n vai servir para nada,
        # columns = ["Time", "Product", "Qty","Client","Order_id","Status"]
        columns = [-1, -2, -3, -4, -5, -6 ]
        self.Open_Orders_Record = [columns]
        self.closed_orders_record = [columns]  #Já existe um outro registo do histórico, isto deve perder a função

        logs.log(info_msg="| CREATED OBJECT   | Order_record  actor:"+str(self.actor)) 
        
        

    def get_order_by_id(self, order_id):
        order_record = False
        records_found = 0
        for order in self.Open_Orders_Record:
            if order[-2]==order_id:
                order_record = order
                records_found+=1

        for order in self.closed_orders_record:
            if order[-2]==order_id:
                order_record = order
                records_found+=1

        if records_found >1:
            logs.log(debug_msg="| FUNCTION         | Orders_records| get_order_by_id  ERROR order found in two places at same time! order_id:{}  actor:".format(order_id, self.actor.id))

        return order_record


        """Orders management
        """
    def add_to_open_orders(self,  product, qty, client):
        logs.log(debug_msg="| FUNCTION         | Orders_records| add_to_open_orders with parameters: time:" + str(self.actor.simulation.time ) + " product: "+ str(product) + " Qty " + str(qty) + "from " + str(self.actor) + " Client: "+ str(client))
        # actor_id = self.actor
                
        self.last_order_id = self.last_order_id + 1   #! Está aqui um possivel erro, last order_id = last_order+1, mas tmb pode estar certo
        #initial status = 0
        #print("temp adding order", self.last_order_id)
        to_add = [self.actor.simulation.time  ,product, qty,  client, self.last_order_id, 0]
        
        if self.get_order_by_id( self.last_order_id) is not False:
            print("add_to_open_orders",self.get_order_by_id( self.last_order_id))
            raise Exception("ordem duplicada")
        
        self.Open_Orders_Record.append(to_add)
        self.actor.simulation.update_simulation_stats("orders_opened")

        logs.log(debug_msg="| ORDERED ADDED    | Orders_records| Order added to {} of qty {} of Product:{} ordered from:{}".format(self.actor, qty, product, client))
        

        self.actor.simulation.mongo_db.add_order_to_db(self.actor.id, self.actor.simulation.time ,  product, qty, client, self.last_order_id, 0)
    
        self.check_orders_integrity()

    def get_orders_sequence(self):
        def get_id(l):
                return l[-2]
            
        open_orders = self.Open_Orders_Record
        open_orders.sort(key=get_id)
            
        sequence=[]
        for order in open_orders:
            if order[-2] == -5:
                continue
            sequence.append(order[-2])
        sequence.sort()
        return sequence

    def get_fist_open_order(self):
        return self.get_orders_sequence()[0]

    def remove_from_open_orders(self,  order_id):
        time = self.actor.simulation.time 

        def check_open_orders_sequence():
            def get_id(l):
                return l[-2]
            open_orders = self.Open_Orders_Record
            open_orders.sort(key=get_id)
            
            
            # return open_orders
            # order_sequence=check_open_orders_sequence()
            
            for i in open_orders:
                if i[-2] == -5:
                    continue
                if i[-2] < order_id:
                    print(inspect.stack())
                    raise Exception("ERRO",i[-2] ,"<", order_id)
            check_open_orders_sequence()

        for record in self.Open_Orders_Record:
            if record[-2] == order_id:
                record[0] = time
                self.Open_Orders_Record.remove(record)
                self.closed_orders_record.append(record)
                order= self.get_order_by_id(order_id=order_id )


                #self.add_to_orders_log( product=order[1], quantity=order[2], client= order[3], order_id=order[-2], status =1)
                self.actor.simulation.mongo_db.close_order_on_db(actor_id=self.actor.id, order_id=order[-2])
                self.actor.simulation.update_simulation_stats("orders_closed")

        logs.log(debug_msg="| FUNCTION         | Orders_records| remove_from_open_orders order "+str(order_id)+" removed from actor "+str(self.actor.id)+str(self.Open_Orders_Record))


    def get_ordered_products(self,time_interval=None,product=None):
        history=self.get_history(time_interval,product=None)
        logs.log(debug_msg="Ordered products: "+history.shape[0]-1)
        return history.shape[0]-1


    def check_orders_integrity(self):
        open_orders = self.Open_Orders_Record
        cloed_orders= self.closed_orders_record

        def get_id(l):
            return l[-2]
            
        open_orders.sort(key=get_id)
        cloed_orders.sort(key=get_id)
        
        def check_sequence(order_list):
            
            if len(order_list)>1:
                for i in range(0,len(order_list)-2,1):
                    if order_list[i][-2] == -5:
                        continue
                    if order_list[i][-2]+1 != order_list[i+1][-2]:
                        print("check:",order_list[i][-2] +1 , order_list[i+1][-2])
                        for el in open_orders:
                            print(el)
                        for el in cloed_orders:
                            print(el)
                        raise Exception("inconsistencia in "+str(order_list))
                
        #print("open orders")
        check_sequence(open_orders)
        #print("closed orders")
        check_sequence(cloed_orders)
