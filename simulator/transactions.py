from . import logging_management as logs
import simulation_configuration as sim_cfg
logs.log(debug_msg="Started transactions.py")
#############################################################################################################
#       Classe que contem todas as funções associadas às transações entre atores                            #
# Esta classe cria o registo de transações e os atores podem vir cá ver se há emcomendas para eles          #
#############################################################################################################

class transactionsClass:
    def __init__(self, simulation):
        self.open_transactions =  []
        self.delivered_transactions =[]     
        self.transaction_id = 0 
        self.simulation = simulation
        '''        estrutura
            [
                {
                    "transaction_id":"id",
                    "deliver_day":"ddd",
                    "sending_day":"ddd",
                    "receiver":"actor_id",
                    "sender":"actor_id",
                    "product":"product_id",
                    "quantity": "int",
                    "delivered": False
                    }
            ]

            ''' 
        # for i in range(1,10,1):
        #     self.add_transaction(sender=0, receiver=1, quantity=23, product=1002, deliver_date=i, sending_date=i-1)
        #     self.add_transaction(sender=0, receiver=1, quantity=23, product=1002, deliver_date=i, sending_date=i-1)
        #     self.add_transaction(sender=0, receiver=1, quantity=23, product=1002, deliver_date=i, sending_date=i-1)
        #     self.add_transaction(sender=0, receiver=1, quantity=23, product=1002, deliver_date=i, sending_date=i-1)

        # print(self.open_transactions)

        #Start transaction log
        with open(sim_cfg.transactions_record_file, 'a') as file:
            file.write("[{'transaction_id': 0, 'deliver_day': 0, 'sending_day': 0, 'receiver': 0, 'sender': 0, 'product': 0, 'quantity': 0, 'delivered': 'True', 'recording_time': 0}")


    def add_transaction(self, sender, receiver, quantity, product, deliver_date, sending_date):
        self.transaction_id = self.transaction_id + 1
        values_to_add =  {
                "transaction_id":self.transaction_id,
                "deliver_day":deliver_date,
                "sending_day":sending_date,
                "receiver":receiver,
                "sender":sender,
                "product":product,
                "quantity": quantity,
                "delivered": False,
                "recording_time": self.simulation.time
                }
        self.open_transactions.append(values_to_add)
        self.add_to_orders_log( record=values_to_add)


    def record_delivered(self,transaction_id ):
        for record in self.open_transactions:
            if record['transaction_id']==transaction_id:
                record['delivered']=True
                record['recording_time']=self.time
                self.delivered_transactions.append(record)
                self.open_transactions.remove(record)
               
                self.add_to_orders_log(record = record)               
                return True

        print("Trasaction {} not found!!".format(transaction_id))
        logs.log(info_msg="[FUNCTION deliver_transaction]  Trasaction {} not found!!".format(transaction_id))
        
        

    def show_transactions_record(self, record_object, title=None):
        print("\n",title,"\n")
        for el in record_object:
            string=""
            for key, value in el.items():
                if key == "transaction_id" and isinstance(value, int): value     = f'{int(value):06d}'
                if key == "deliver_day" and isinstance(value, int): value        = f'{int(value):03d}'
                if key == "sending_day" and isinstance(value, int): value        = f'{int(value):03d}'
                if key == "receiver" and isinstance(value, int): value           = f'{int(value):02d}'
                if key == "sender" and isinstance(value, int): value             = f'{int(value):02d}'
                if key == "product" and isinstance(value, int): value            = f'{int(value):04d}'
                if key == "quantity" and isinstance(value, int): value           = f'{int(value):03d}'
                
                if isinstance(value, int) and value < 10:
                    value = ""+str(value)

            
            print(string)
            
    def get_transaction_by_id(self,id):
         for record in self.open_transactions:
            if record['transaction_id']== id:
                return record

    def get_todays_transactions(self, actor):
        pending_transactions=[]
        day= self.simulation.time
        # print("getting transactions for actor ",actor.name)

        for record in self.open_transactions:
            if record['deliver_day']== day  and  record['receiver'] == actor.id:
                # print(record)
                pending_transactions.append(record['transaction_id'])
        return pending_transactions
        
        # self.delivered_transactions.append(record)
        # self.open_transactions.remove(record)
        
    def add_to_orders_log(self, record = dict): #  record_time são recording_time  
        with open(sim_cfg.transactions_record_file, 'a') as file:
            file.write(",\n" +str(record)  )


###############################################################################################
#      funções relacionadas com operações realizadas pelo actor da cadeia de valor            #
###############################################################################################
# from main import simulation_id
# from actors import ClassOrdersRecord


