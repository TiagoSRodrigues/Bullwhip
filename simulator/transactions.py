import inspect
import numpy as np
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
        # with open(sim_cfg.TRANSCTIONS_RECORDS_FILE, 'a') as file:
        #     # file.write("[{'transaction_id': 0, 'deliver_day': 0, 'sending_day': 0, 'receiver': 0, 'sender': 0, 'product': 0, 'quantity': 0, 'delivered': 'True', 'recording_time': 0}")
        #     file.write("[")


    def get_transactions_stats(self, actor_id, product, history_days=1000000):
        """
        copia a lista de transações entregues
        extai a coluna das quantidades
        retorna a média e o std
        """
        #apagar logs.log(debug_msg= f"| GET TRANSACTION  | Transactions  | actor id  {actor_id} ")

        transaction_list=[]
        for item in self.delivered_transactions:
            # print("item",item)
            if item["receiver"]  == actor_id and item["product"] == product:
                if self.simulation.time - history_days <= item["deliver_day"]:
                    transaction_list.append( item )

        transaction_array=np.array(transaction_list)
        # print("delivered transactions", transaction_list)
        if not transaction_array:
            logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f" ERROR, transactions stats failed   actor {actor_id} product {product} -  self.delivered_transactions = {self.delivered_transactions}" )
            return False

        logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f"transactions  mean:{transaction_array.mean()} std {transaction_array.std()}" )
        print(transaction_array.mean() , transaction_array.std(), "get_transactions_stats")
        return transaction_array.mean() , transaction_array.std()





    def add_transaction(self, transaction_info):#, order_id, order_creation,  sender, receiver, quantity, product, deliver_date, sending_date):
        self.transaction_id = self.transaction_id + 1
        # logs.log(debug_msg=f"| TRANSACTION ADDED| Transactions  | transactions_id {self.transaction_id}  transaction info: {transaction_info} ")
        logs.new_log(day=self.simulation.time,file= "transactions", function="add_transaction", actor= transaction_info["sender"], debug_msg="Transaction added -> {}".format(transaction_info))


        values_to_add =  transaction_info
        values_to_add["transaction_id"]= self.transaction_id  #!isto é para ficar até a DB estar a funcionar

        #adiciona ao registo interno
        self.open_transactions.append(values_to_add)

        #adiciona à db 
        self.update_database( self.transaction_id, transaction_info, delivered=False)

        self.simulation.update_simulation_stats("transactions_opened")

        return True

    def update_database(self, transaction_id, transaction_info=None, delivered=None):
        """Atualiza a base de dados, se não existir o registo cria-o, se existir altera o estado
        """
        logs.log(debug_msg= f"| Update DB        | Transactions  | transaction id  {transaction_id}, tansaction info { transaction_info}, delivered {delivered} ")

        if not delivered:
            if not self.simulation.mongo_db.add_transaction_to_db(self.transaction_id, transaction_info):
                raise Exception("Error adding transaction to DB")
        if delivered==1:
            try:
                self.simulation.mongo_db.update_transaction_on_db(self.transaction_id,transaction_info )
            except:
                raise Exception("Error, updating database")

        if (transaction_info is None) and (delivered == None):
            raise Exception("Erro no update, só pode ter um None | transaction_id: {}, transaction_info:{}, delivered:{}".format(transaction_id, transaction_info, delivered))

    def record_delivered(self,transaction_id ):
        logs.log(debug_msg="| TRANSACTION REMVD| Transactions  | transaction_id "+str(transaction_id))

        for record in self.open_transactions:
            if record['transaction_id']==transaction_id:
                record['delivered']=1
                record['update_day']=self.simulation.time
                record['lead_time']=self.simulation.time-record['order_criation_day']

                self.delivered_transactions.append(record)
                self.open_transactions.remove(record)

                self.update_database(transaction_id,  delivered=1, transaction_info=record)
                # self.simulation.update_simulation_stats("transactions_delivered")


                self.simulation.mongo_db.add_to_db(colection_name="t_bkup", data=record)
                logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="record_delivered", debug_msg=f"sucesseful delivered Trasaction: {transaction_id}" )

                return True

        logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="record_delivered", debug_msg=f" ERROR, transactions failed Trasaction: {transaction_id} not found!! | open transactions: {self.open_transactions}" )
        return False


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

    def get_transaction_by_id(self, transaction_id):
        try:
            for record in self.open_transactions:
                if record['transaction_id'] == transaction_id:
                    return record
        except:
            raise Exception("Transaction requested is not in open transactions")

    def get_todays_transactions(self, actor):
        """ Este método está obsuleto, não deve ser utilizado, pode deixar encomendas atrasadas no limbo
        """
        logs.log(debug_msg="| Customer transac | Transactions  | getting transactions for actor: {}".format( actor.id ))

        pending_transactions=[]

        for record in self.open_transactions:
            if record['receiver'] == actor.id:
                if record['deliver_day'] == self.simulation.time:
                    pending_transactions.append(record['transaction_id'])

        return pending_transactions


    def get_delivering_transactions(self, actor):
        # self.check_transactions_integrity()
        """Verifica que existe alguma encomenda no registo com dia de entrega igual ou anterior ao presente

        Returns:
            list: lsita com id das transações transações
        """

        #apagar logs.log(debug_msg="| Customer transac | Transactions  | getting transactions for actor: {}".format( actor.id ))

        pending_transactions=[]

        for record in self.open_transactions:
            if (record['deliver_day'] <= self.simulation.time ) and  (record['receiver'] == actor.id):
                pending_transactions.append(record['transaction_id'])


        logs.new_log(day=self.simulation.time, actor=actor.id, file= "transactions", function="get_delivering_transactions", debug_msg = f"pending_transactions_today:{pending_transactions}" )
        return pending_transactions



    def deliver_to_final_client(self):

        customer = self.simulation.get_actor_by_id(0) #retorna o objecto actor zero (ou customer)



        transactions_to_deliver=self.get_delivering_transactions(customer)
        if not transactions_to_deliver: 
            logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg="Any deliver for final cliente ")

        logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"t : {transactions_to_deliver}, ator {customer.id} ")
        try:
            for trans in transactions_to_deliver:
                transaction_info = self.get_transaction_by_id(trans)

                customer.receive_transaction( transaction_info["transaction_id"])

                logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"delivered: {transaction_info}  ")

        except:
            logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"ERROR customer não recebeu encomenda  ")
            raise Exception("Customer Deliver error actor {} transaction {} of a list{}".format( customer.id, self.get_transaction_by_id(trans),transactions_to_deliver ))



    def check_transactions_integrity(self):
        logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"  ")

        open=self.open_transactions
        delivered=self.delivered_transactions
        id=self.transaction_id
        today=self.simulation.time
        for el in open:
            if el["deliver_day"] < today:
                raise Exception("Transaction {} is in open transactions but is in the past".format(el["transaction_id"]))

