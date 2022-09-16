import pandas as pd
class dashboard_data():
    def __init__(self, simulation_object, options=None):
        self.simulation = simulation_object

        # self.open_transactions
        # self.delivered_transactions
        # self.transactions_log
        # self.transaction_id parece que n precisam ser iniciados logo

        self.actors_dataset={}
        #simulation data

        self.update_datasets(self.simulation)
        #actors data

    #isto vai precisar de ser otimizado!!! mas até lá good enough
    def update_datasets(self, simulation ):
        self.simulation = simulation

        time =  self.simulation.time

        self.open_transactions  = self.simulation.ObejctTransationsRecords.open_transactions
        self.delivered_transactions  = self.simulation.ObejctTransationsRecords.delivered_transactions
        self.transactions_log        = self.simulation.ObejctTransationsRecords.open_transactions
        self.transaction_id         = self.simulation.ObejctTransationsRecords.transaction_id
    #
        self.actors_collection=self.simulation.actors_collection

        for actor in self.actors_collection:
            name , id = actor.name , actor.id
            Open_Orders, closed_orders = actor.actor_stock_record.Open_Orders_Record, actor.actor_stock_record.closed_orders_record
            invetory= actor.actor_inventory.main_inventory
            self.actors_dataset[str(id)] = [name, Open_Orders, closed_orders, invetory]

            #example os iventary {1001: {'Composition': {'2001': 1}, 'Name': 'ProductA', 'id': 1001, 'safety_stock': 2, 'in_stock': 10},



