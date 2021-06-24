from . import logging_management as logs
logs.log(debug_msg="Started transactions.py")
#############################################################################################################
#       Classe que contem todas as funções associadas às transações entre atores                            #
# Esta classe cria o registo de transações e os atores podem vir cá ver se há emcomendas para eles          #
#############################################################################################################

class transactionsClass:
    def __init__(self, simulation):
        self.transactions_log =  []
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
                "delivered": False
                }
        self.transactions_log.append(values_to_add)


    def deliver_transaction(self,transaction_id ):
        for record in self.transactions_log:
            if record['transaction_id']==transaction_id:
                record['delivered']=True
                self.delivered_transactions.append(record)
                self.transactions_log.remove(record)
                return
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

    def get_todays_transactions(self, actor):
        pending_transactions=[]
        day= self.simulation.time

        for record in self.transactions_log:
            if record['deliver_day']== day  and  record['receiver'] == actor.id:
                pending_transactions.append['transaction_id']
        return pending_transactions
        
        # self.delivered_transactions.append(record)
        # self.transactions_log.remove(record)
        
###############################################################################################
#      funções relacionadas com operações realizadas pelo actor da cadeia de valor            #
###############################################################################################
# from main import simulation_id
# from actors import ClassOrdersRecord


def receive_order(actor, quantity, product=None):
    if product== None:
        product=1
    actor.get_inventory()


def place_order(actor, quantity, product=None):
    if product== None:
        product=1

