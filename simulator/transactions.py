from . import logging_management as logs
import simulation_configuration as sim_cfg
logs.log(debug_msg="Started transactions.py")
#############################################################################################################
#       Classe que contem todas as funções associadas às transações entre atores                            #
# Esta classe cria o registo de transações e os atores podem vir cá ver se há emcomendas para eles          #
#############################################################################################################

class transactionsClass:
    """
    this class handle any transactions action"""
    def __init__(self, simulation):
        self.open_transactions =  []
        self.delivered_transactions =[]     
        self.transaction_id = 0 
        self.simulation = simulation
        
        #Start transaction log
        with open(sim_cfg.transactions_record_file, 'a') as file:
            # file.write("[{'transaction_id': 0, 'deliver_day': 0, 'sending_day': 0, 'receiver': 0, 'sender': 0, 'product': 0, 'quantity': 0, 'delivered': 'True', 'recording_time': 0}")
            file.write("[")


    def add_transaction(self, sender, receiver, quantity, product, deliver_date, sending_date):
        logs.log(debug_msg="| TRANSACTION ADDED| Transactions  |   sender {} receiver {} quantity {} product {} deliver_date {} sending_date {}".format( sender, receiver, quantity, product, deliver_date, sending_date))
        self.transaction_id = self.transaction_id + 1
                
        transaction_info={"deliver_day":deliver_date,
                "sending_day":sending_date,
                "receiver":receiver,
                "sender":sender,
                "product":product,
                "quantity": quantity,
                "delivered": 0,
                "last_update": self.simulation.time
                }
        
        
        values_to_add =  transaction_info
        values_to_add["transaction_id"]= self.transaction_id  #!isto é para ficar até a DB estar a funcionar
        

        self.open_transactions.append(values_to_add)
        self.simulation.update_simulation_stats("transactions_opened")
        self.add_to_orders_log( record=values_to_add)

        self.update_database( self.transaction_id, transaction_info, delivered=False)

    def update_database(self, transaction_id, transaction_info=None, delivered=None):
        """Atualiza a base de dados, se não existir o registo cria-o, se existir altera o estado
        """

        if not delivered:
            if not self.simulation.mongo_db.add_transaction_to_db(self.transaction_id, transaction_info):
                print("erro a adicionar transação à DB")
                raise Exception
        if delivered==1:
            try:
                self.simulation.mongo_db.update_transaction_on_db(self.transaction_id)
            except:
                raise Exception("Error, updating database")
            
        if (transaction_info is None) and (delivered == None):
            raise Exception("Erro no update, só pode ter um None | transaction_id: {}, transaction_info:{}, delivered:{}".format(transaction_id, transaction_info, delivered))
        
    def record_delivered(self,transaction_id ):
        logs.log(debug_msg="| TRANSACTION REMVD| Transactions  | transaction_id "+str(transaction_id)) 
        
        for record in self.open_transactions:
            if record['transaction_id']==transaction_id:
                record['delivered']=True
                record['recording_time']=self.simulation.time
                
                self.delivered_transactions.append(record)
                self.open_transactions.remove(record)
               
                #self.add_to_orders_log(record = record) #!obsulento com a db
                self.update_database(transaction_id,  delivered=1)
                self.simulation.update_simulation_stat("transactions_closed")

                return True

        print("Trasaction {} not found!! in \n{}".format(transaction_id,self.open_transactions))
        logs.log(info_msg="| TRANSACTION DLVRD| Transactions  | transaction_id   Trasaction {} not found!!".format(transaction_id))
        
        
    def show_all_transactions(self):
        print("\n\nall open transactions\n",self.open_transactions, "\n\n all delivered transactions\n",self.delivered_transactions,"\n\n")    

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
            
    def get_transaction_by_id(self, id):
        try:
            for record in self.open_transactions:
                if record['transaction_id'] == id:
                    return record
        except:
            raise Exception("Transaction requested is not in open transactions")

    def get_todays_transactions(self, actor):
        logs.log(debug_msg="| Customer transac | Transactions  | getting transactions for actor: {}".format( actor.name )) 

        pending_transactions=[]

        for record in self.open_transactions:
            if record['deliver_day']== self.simulation.time  and  record['receiver'] == actor.id:
                pending_transactions.append(record['transaction_id'])
        return pending_transactions


######################foda-se
        
    def add_to_orders_log(self, record = dict): #  record_time são recording_time  
        
        recordstr=str(record).replace("'", '"').replace("False", str('"'+"False"+'"')).replace(" True", str(' "'+"True"+'"'))

        # print(type(record))
        #self.simulation.mongo_db.add_to_simulation_db(collection_name="transactions",value= record )
        with open(sim_cfg.transactions_record_file, 'a') as file:

            file.write("\n" +str(recordstr)+"," )


    def deliver_to_final_client(self):
        logs.log(debug_msg="| FUNCTION         | Transactions  | deliver_to_final_client : ")

        customer = self.simulation.get_actor_by_id(0) #retorna o objecto actor zero (ou customer)

        transactions_to_deliver=self.get_todays_transactions(customer)
        
        try:
                for trans in transactions_to_deliver:
                    transaction_info = self.get_transaction_by_id(trans)

                    customer.actor_inventory.add_to_inventory( product  = transaction_info["product"], quantity = transaction_info["quantity"])

                    self.record_delivered(trans)
                    logs.log(debug_msg="| Customer transac | Transactions  | deliver_to_final_client  transaction: {}   transaction info: {}".format( trans ,transaction_info ))
     
        except:
            self.record_delivered(trans) 
            raise Exception("Customer Deliver error actor {} transaction {} of a list{}".format( customer.id, self.get_transaction_by_id(trans),transactions_to_deliver ))
            

##############################################################################################
#      funções relacionadas com operações realizadas pelo actor da cadeia de valor           #
##############################################################################################
# from main import simulation_id
# from actors import ClassOrdersRecord



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

