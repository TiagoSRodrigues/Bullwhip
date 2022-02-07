
class ClassInventory:
    def update_inicial_inventory(self):
    def add_to_inventory(self, product, quantity):
    def remove_from_inventory(self, product, quantity):
    def get_product_inventory(self, product_id):
    def set_product_inventory(self, product_id, qty):
    def get_product_safety_inventory(self, product_id):
    def get_product_reorder_history_size(self, product_id):
    def refresh_inventory_capacity(self):
    def show_present_composition(self):
       
class actor:
    def __init__(self, simulation_object , id:int , name:str , avg:int , var:int, max_inventory:int)
    def get_actor_product_list(self):
    def get_product_composition(self, product_id):
    def get_orders_pending(self):
    def get_actor_present_capacity(self):
    def get_product_inventory(self,product):
    def get_product_safety_inventory(self,product):
    def get_product_reorder_history_size(self,product):
    def get_todays_transactions(self):
    def get_actor_info(self):
    def set_actor_state(self, state:int, log_msg=None ):
    def receive_order(self, supplier, quantity, product, client ):
    def manage_orders(self):
    def manage_stock(self):
    def send_transaction(self, order):
    def receive_transaction(self, transaction_id):
    def place_order(self, actor_supplier_id, product, quantity):
    def manufacture_product(self, product):
    def get_max_production(product, recepe):
    def production(self, product, quantity, recepe):
class MongoDB:
    def __init__(self, simulation, drop_history=True):
    def drop_database(self):
    def add_transaction_to_db(self, transaction_id=int, transaction_data=dict):
    def update_transaction_on_db(self, transaction_id):
    def add_order_to_db(self,actor_id, time,  product, quantity, client, order_id, status):
    def close_order_on_db(self, actor_id, order_id):
    def update_inventory_db(self,actor_id, product, quantity):
    def add_actor_to_db(self, actor_id, orders, inventory):
    def check_connection(self):
    
class ClassSimulation:
    def __init__(self):
    def add_to_actors_collection(self, actor):
    def get_actors_collection(self):
    def get_actors_configurations(self,actors_configuration):
    def create_actors(self,actors_configuration_file):
    def get_actor_parameters(self,configs_dict,actor):
    def change_simulation_status(self, status):
    def update_global_inventory(self, actor, product, qty):
    
    def update_simulation_stat(self, stat):

class transactionsClass:
    def __init__(self, simulation):
    def add_transaction(self, sender, receiver, quantity, product, deliver_date, sending_date):
    def update_database(self, transaction_id, transaction_info=None, delivered=None):
    def record_delivered(self,transaction_id ):
    def show_all_transactions(self):
    def show_transactions_record(self, record_object, title=None):
    def get_transaction_by_id(self, id):
    def get_todays_transactions(self, actor):
    def add_to_orders_log(self, record = dict): #  record_time são recording_time  
    def deliver_to_final_client(self):
       
class ClassSupplyChain:
    def __init__(self, simulation):
    def add_to_supply_chain(self,actor):
    def show_supply_chain(self):
    def get_supply_chain(self):
    def get_end_of_chain_actors(self):
