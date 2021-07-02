import  time
import dash
import dash_core_components as dcc
import dash_html_components as html
import os, sys, json
from dash_html_components.Title import Title 
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
from pandas.core.frame import DataFrame
try: import simulation_configuration as sim_cfg 
except: 
    sys.path.append('N:/TESE/Bullwhip')
    import simulation_configuration as sim_cfg 

class datasets():
    def __init__(self,object,  object_name):
        self.object = object
        self.name   = object_name


# Set up the app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


#sim_cfg_orders_record_path
transactions_dataset={}

def get_inventory_dataset():
    
    inventory_file = sim_cfg.inventory_file
    try:
        with open(inventory_file, 'r') as file:
            data=file.read()   #aqui entra como str

            data=json.loads(data)         #rebenta aqui com :    00
            df1 = pd.DataFrame([]) 
            for actor in data:
                for prod in data[actor].keys():
                    df2 = pd.DataFrame( [ [ actor, prod, data[actor][prod] ]  ]  , columns=["Ator","Product", "Quantity"] )
                df1=df1.append(df2) 

            return df1
    except:
        time.sleep(0.5)
        get_inventory_dataset()

inventory_dataset= get_inventory_dataset()

inventory_dataset_columns = inventory_dataset.columns


def get_transactions_dataset():
    
    transactions_file = sim_cfg.transactions_record_file
    try:
        with open(transactions_file, 'r') as file:
            data=file.read()+"]"
            data=data.replace("'", '"')
            data=data.replace("False", str('"'+"False"+'"'))
            
            # print(len(data),"\n\n\n\n\n\n\n")

        return pd.read_json(data)
    except:
        time.sleep(0.5)
        get_transactions_dataset()


transactions_dataset =  get_transactions_dataset()

def get_actors_oders():
    orders_datasets={}
    dir_files=os.listdir(sim_cfg.orders_record_path)

    for file in dir_files:
        if file[0:6] == "orders":
            orders_datasets[file[:-4]] = pd.read_csv(sim_cfg.orders_record_path + file, names=["Time", "Product", "Qty","Client","Order_id","Status"] )

            # elif file[0:12] == "transactions":
            #     transactions_dataset =  pd.read_json('transactions_record_file.json' )
    return orders_datasets

# actores_main_dataset = get_actors_oders()
# 
# nr_of_actors=len(actores_main_dataset)

def update_open_orders_dataset():
    actores_main_dataset = get_actors_oders()

    open_orders_dataset={}

    for actor in actores_main_dataset:
        actor_dataset = actores_main_dataset[actor]
        open_orders_a1 = actor_dataset[actor_dataset["Status"]!=1]
        
        open_orders_dataset["open_"+str(actor)]=open_orders_a1


    return open_orders_dataset


# Format the Table columns
transactions_columns = transactions_dataset.columns

# Define Modal - Botão top ritgh 
with open("N:/TESE/Bullwhip/dashboard/assets/modal.md", "r") as f:
    howto_md = f.read()

modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown(howto_md)], id="howto-md")),
        dbc.ModalFooter(dbc.Button("Close", id="howto-close", className="howto-bn")),
    ],
    id="modal",
    size="lg",
)



# Buttons
button_gh = dbc.Button(
    "Learn more",
    id="howto-open",
    outline=True,
    color="secondary",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

button_howto = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/TiagoSRodrigues/Bullwhip",
    id="gh-link",
    style={"text-transform": "none"},
)



# Define Header Layout
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            html.Img(
                                src=app.get_asset_url("dash-logo-new.png"),
                                height="30px",
                            ),
                            href="https://plotly.com/dash/",
                        )
                    ),
                    dbc.Col(dbc.NavbarBrand("Bullwhip simulator - Development mode")),
                    modal_overlay,
                ],
                align="center",
            ),
            dbc.Row(
                dbc.Col(
                    [  dbc.NavbarToggler(id="navbar-toggler"),
                        dbc.Collapse(
                            dbc.Nav(
                                [dbc.NavItem(dbc.NavLink("by: Tiago Rodrigues", href="#")),dbc.NavItem(button_howto), dbc.NavItem(button_gh)],
                                className="ml-auto",
                                navbar=True,
                            ),
                            id="navbar-collapse",
                            navbar=True,
                        ),
                    ]
                ),
                align="center",
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
)

# # Color selector dropdown
# color_drop = dcc.Dropdown(
#     id="color-drop-menu",
#     options=[
#         {"label": col_name.capitalize(), "value": col_name}
#         for col_name in table.columns
#     ],
#     value="label",
# )





inventory_dataset_columns




 ## TRANSACTIONS

Inventory_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Inventory")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    
                        dash_table.DataTable(
                            id="inventory-table",
                            columns=[
                                    {"name": i, "id": i} for i in sorted(inventory_dataset_columns)
                                ],
                            data=get_inventory_dataset().to_dict('records')
,
                        ),
                    
                )
            )
        ),
    ]
)




def create_actor_table():
    open_orders_dataset=update_open_orders_dataset()

    # Define Cards
    ### ACTORS
    actors_tables = datasets(object=[], object_name="actors_tables")
    table_name=[]
    for actor in open_orders_dataset:

        dataset = open_orders_dataset[actor]
        table_name.append(str(actor)+"-table")

        actors_tables.object.append(
                dbc.CardHeader(actor))
        actors_tables.object.append(
                dbc.CardBody(
                    dbc.Row(
                        dbc.Col(
                            
                                dash_table.DataTable(
                                    id=str(actor)+"-table",
                                    columns=[
                                            {"name": i, "id": i} for i in sorted(dataset.columns)
                                        ],
                                    data=dataset.to_dict('records')
        ,
                               style_table={'height': '300px', 'overflowY': 'auto'} ),      
                        )
                    )
              ),
        )
    return actors_tables

actors_tables =  create_actor_table().object



left_card = dbc.Card(
    actors_tables  
)
 ## TRANSACTIONS

transactions_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Transactions")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    
                        dash_table.DataTable(
                            id="transactions-table",
                            columns=[
                                    {"name": i, "id": i} for i in sorted(transactions_dataset.columns)
                                ],
                            data=transactions_dataset.to_dict('records')
,
                        ),
                    
                )
            )
        ),
    ]
)


app.layout = html.Div(
    [
        header,
        dbc.Container(
            [dbc.Row(
                [dbc.Col(  html.Div(left_card, id="actors_data_table", className="actors_row") ,  md=6), 
            dbc.Col(
                     html.Div( [ Inventory_card,
                                transactions_card])
              , md=6)

            ])
    ],
            fluid=True,
        ),
   dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ) ]
)




def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# we use a callback to toggle the collapse on small screens
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# print(actors_tables.object)

@app.callback(
        Output(  "actors_data_table" , component_property='children'),
        Input('interval-component', 'n_intervals'))
def update_actors_tables(n):

    actor_table = create_actor_table().object


    return actor_table



@app.callback(
    Output("transactions-table", "data"),
     Input('interval-component', 'n_intervals'))
def update_transactions_table(n):
    transactions_dataset = get_transactions_dataset() 
    return transactions_dataset.to_dict('records')



@app.callback(
    Output("inventory-table", "data"),
     Input('interval-component', 'n_intervals'))
def update_transactions_table(n):
    inventory_dataset=get_inventory_dataset
    return inventory_dataset().to_dict('records')


if __name__ == "__main__":
    app.run_server(debug=False)

