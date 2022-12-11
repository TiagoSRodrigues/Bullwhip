import inspect
from sys import stderr
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



    def get_transactions_stats(self, actor_id, product:int, history_days:int):
        actor_id, product, history_days = int(actor_id), int(product), int(history_days)
        """
        copia a lista de transações entregues
        extai a coluna das quantidades
        retorna a média e o std
        """
        logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f" actor {actor_id}, product {product} history {history_days} " )

        transaction_list=[]

        for item in self.delivered_transactions:

            if int(item["receiver"])  == actor_id:
                # logs.append_line_to_file(file_path= "N:\\TESE\\Bullwhip\\data\\logs\\tmp\\get_transactions_receiver", line=f"{item['receiver']},\n")

                if int(item["product"]) == product:
                    # logs.append_line_to_file(file_path= "N:\\TESE\\Bullwhip\\data\\logs\\tmp\\get_transactions_receiver2", line=f" time {self.simulation.time} - h {history_days}  = {self.simulation.time - history_days} || time { self.simulation.time }  - u  {item['update_day']} -> {self.simulation.time - int(item['update_day'])}  || {(self.simulation.time - history_days)  } >= {(self.simulation.time - int(item['update_day']))} { (self.simulation.time - history_days) >= (self.simulation.time - int(item['update_day']))},\n")

                    transaction_list.append(item['transit_time'] )


                    # if (self.simulation.time - history_days) >= (self.simulation.time - int(item["update_day"])):

                    # if (self.simulation.time - history_days) <= 0 :
                    #     transaction_list.append(item )
        if len(transaction_list) == 0:
            return False
        if len(transaction_list) <= history_days:
            t_array = np.array(transaction_list)
            # calculate mean and std


            return t_array.mean(), t_array.std()
        if len(transaction_list) == 0:
             return False
        else:
            t_array = np.array(transaction_list[:-history_days])

            #     print(f"day {self.simulation.time}")
            #     print(self.delivered_transactions)
            #     raise Exception("mean is zero")
            return t_array.mean(), t_array.std()

            # print("ssss",transaction_list)

        # else:
            # print("xxxxxx",transaction_list)
            # #calculate mean and std

        # transaction_array=np.array(transaction_list)


        # if len(transaction_array) < 2:
        #     logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f" ERROR, transactions stats failed actor {actor_id} product {product} - " )

            #     logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f"{trans}" )

            # if self.simulation.time > 100:
            #     for el in inspect.stack():
            #         for i in el:
            #             print(i)
            # return False



        # times=[]
        # for t in transaction_array:
        #     times.append(t['lead_time'])

        # avg = np.array(times).mean()
        # std = np.array(times).std()


        # logs.new_log(day=self.simulation.time, actor=actor_id, file= "transactions", function="get_transactions_stats", debug_msg=f"transactions  mean:{avg} std:{std}" )

        # return avg, std

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
        logs.log(debug_msg="| Customer transac | Transactions  | getting transactions for actor: {}".format(actor.id ))

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



        pending_transactions=[]

        for record in self.open_transactions:
            if (record['deliver_day'] <= self.simulation.time ) and  (record['receiver'] == actor.id):
                pending_transactions.append(record['transaction_id'])


        logs.new_log(day=self.simulation.time, actor=actor.id, file= "transactions", function="get_delivering_transactions", debug_msg = f"today shod be delivered: {len(pending_transactions)} transactions" )
        return pending_transactions


    # SETTERS


    def add_transaction(self, transaction_info):#, order_id, order_creation,  sender, receiver, quantity, product, deliver_date, sending_date):

        self.validate_transaction_schema(transaction_info)
        logs.append_line_to_file(file_path=f"{self.simulation.simulation_results_folder}transactions_opened{self.simulation.simulation_id}.csv", line=f"{transaction_info},\n")
        self.transaction_id = self.transaction_id + 1
        # logs.log(debug_msg=f"| TRANSACTION ADDED| Transactions  | transactions_id {self.transaction_id}  transaction info: {transaction_info} ")
        logs.new_log(day=self.simulation.time,file= "transactions", function="add_transaction", actor= transaction_info["sender"], debug_msg="Transaction added -> {}".format(transaction_info))


        values_to_add =  transaction_info
        values_to_add["transaction_id"]= self.transaction_id  #!isto é para ficar até a DB estar a funcionar

        #adiciona ao registo interno
        self.open_transactions.append(values_to_add)

        #adiciona à db
        self.update_database(self.transaction_id, transaction_info, delivered=False)

        self.simulation.update_simulation_stats("transactions_opened")

        return self.transaction_id

    def update_database(self, transaction_id, transaction_info=None, delivered=None):
        """Atualiza a base de dados, se não existir o registo cria-o, se existir altera o estado
        """
        logs.new_log(day=self.simulation.time,file= "transactions", function="add_transaction", actor= transaction_info["sender"], debug_msg=f"transaction id  {transaction_id}, tansaction info { transaction_info}, delivered {delivered} ")

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

    def update_transaction(self,transaction_id ):
        logs.new_log(day=self.simulation.time,file= "transactions", function="update_transaction", actor= " ", debug_msg="Updating transaction  -> {}".format(transaction_id))

        for record in self.open_transactions:
            if record['transaction_id']==transaction_id:
                self.validate_transaction_schema(record)
                record['delivered']=1
                record['update_day']=self.simulation.time
                record['lead_time']= self.simulation.time - record['order_criation_day']
                record['transit_time']= record["deliver_day"] - record['order_criation_day']

                self.delivered_transactions.append(record)
                self.open_transactions.remove(record)

                self.update_database(transaction_id,  delivered=1, transaction_info=record)


                self.simulation.mongo_db.add_to_db(colection_name="t_bkup", data=record)
                logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="update_transaction", debug_msg=f"sucesseful delivered Trasaction: {record}" )
                self.simulation.update_simulation_stats("transactions_delivered")

                logs.append_line_to_file(file_path=f"{self.simulation.simulation_results_folder}transactions_closed{self.simulation.simulation_id}.csv", line=f"{record},\n")
                return True

        logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="update_transaction", debug_msg=f" ERROR, transactions failed Trasaction: {transaction_id} not found!! | open transactions: {self.open_transactions}" )
        return False

    def validate_transaction_schema(self, transaction_dict):
        # validate the schema of the transaction
        reference={"deliver_day": int, "order_id": int, "order_criation_day":int, "sending_day":int, "receiver": int, "sender": int, "product": int, "quantity": int, "transit_time": int, "lead_time": int, "theoretical_lead": int, "update_day": int, "delivered": int, "transaction_id": int }

        if transaction_dict.keys() != reference.keys():
            raise Exception(f"Error, transaction schema not valid invalid -> {transaction_dict}")


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




    def deliver_to_final_client(self):

        customer = self.simulation.get_actor_by_id(0) #retorna o objecto actor zero (ou customer)



        transactions_to_deliver=self.get_delivering_transactions(customer)
        if not transactions_to_deliver:
            logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg="Any deliver for final cliente ")

        logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"t : {transactions_to_deliver}, ator {customer.id} ")
        try:
            for trans in transactions_to_deliver:
                transaction_info = self.get_transaction_by_id(trans)

                customer.receive_transaction(transaction_info["transaction_id"])

                logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"delivered: {transaction_info}  ")

        except:
            logs.new_log(day=self.simulation.time, actor=0, file= "transactions", function="deliver_to_final_client", debug_msg = f"ERROR customer não recebeu encomenda  ")
            raise Exception("Customer Deliver error actor {} transaction {} of a list{}".format(customer.id, self.get_transaction_by_id(trans),transactions_to_deliver ))



    def check_transactions_integrity(self):
        logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"  ")

        open = self.open_transactions
        delivered = self.delivered_transactions

        id = self.transaction_id
        today = self.simulation.time

        open_trasactions_ids_set = set()
        open_trasactions_ids = []

        open_trasactions_order_set =set()
        open_trasactions_order = []

        delivered_transaction_ids = []
        delivered_transaction_order = []


        for d in delivered:
            delivered_transaction_ids.append(d['transaction_id'])
            delivered_transaction_order.append(d['order_id'])

        for o in open:
            open_trasactions_ids.append(o['transaction_id'])
            open_trasactions_ids_set.add(o['transaction_id'])
            open_trasactions_order.append(o['order_id'])
            open_trasactions_order_set.add(o['order_id'])


        # for trans in delivered:
        #     print(trans)


        if len(open_trasactions_ids_set) != len(open_trasactions_ids):
            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"ERROR, open trasactions ids are not unique")
            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"set: {open_trasactions_ids_set}")
            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"list: {open_trasactions_ids}")

            raise Exception("ERROR, open trasactions ids are not unique")


        if len(open_trasactions_order_set) != len(open_trasactions_order):
            print("set:" ,open_trasactions_order_set)
            print("list:" ,open_trasactions_order)




            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"ERROR, open trasactions order are not unique")
            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"set: {open_trasactions_order_set}")
            logs.new_log(day=self.simulation.time, actor= " ", file= "transactions", function="check_transactions_integrity", debug_msg = f"list: {open_trasactions_order}")
            raise Exception("ERROR, open trasactions order are not unique")
