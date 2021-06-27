import pandas as pd
class dashboard_data():
    def __init__(self, simulation_object, options=None):
        self.simulation = simulation_object
        self.update_datasets()

        #simulation data

        #actors data

    #isto vai precisar de ser otimizado!!! mas até lá good enough 
    def update_datasets(self ):

        time =  self.simulation.time

        open_transactions  = self.simulation.ObejctTransationsRecords.open_transactions 
        delivered_transactions  = self.simulation.ObejctTransationsRecords.delivered_transactions 
        transactions_log        = self.simulation.ObejctTransationsRecords.open_transactions 
        transaction_id         = self.simulation.ObejctTransationsRecords.transaction_id 
    #   
        actors_collection=self.simulation.actors_collection
        actor_dataset={}
        for actor in actors_collection:
            name , id = actor.name , actor.id
            Open_Orders, closed_orders = actor.actor_stock_record.Open_Orders_Record, actor.actor_stock_record.closed_orders_record
            invetory= actor.actor_inventory.main_inventory
            actor_dataset[id] = [name, Open_Orders, closed_orders, invetory]

            #example os iventary {1001: {'Composition': {'2001': 1}, 'Name': 'ProductA', 'id': 1001, 'safety_stock': 2, 'in_stock': 10},


        df = pd.DataFrame.from_dict(open_transactions)

        # print(df)
        # print(open_transactions )
  
 

            
        # print(x )
        # print(dir(x))

     #transactions data

 
        # print( dir("object"))

        #show inside object: dir(transactions)

class dataset():
    def __init__(self, object):
        pass

'''

actor_X_dataset:{
    inventary:[]
    orders:[]
}

'''

# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import dash_table
# import pandas as pd

# app = dash.Dash(__name__)

# app.layout = html.Div([
#     dash_table.DataTable(
#         id='table',
#         columns=[{"name": i, "id": i} 
#                  for i in df.columns],
#         data=df.to_dict('records'),
#         style_cell=dict(textAlign='left'),
#         style_header=dict(backgroundColor="paleturquoise"),
#         style_data=dict(backgroundColor="lavender")
#     )
# ])

# app.run_server(debug=True)