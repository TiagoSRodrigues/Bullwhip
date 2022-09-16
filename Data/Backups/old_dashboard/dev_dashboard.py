import time
import dash
from dash import dcc
from dash import html
import os
import sys
import json
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash import dash_table

try:
    import simulation_configuration as sim_cfg
except:
    sys.path.append('N:/TESE/Bullwhip')
    import simulation_configuration as sim_cfg


class datasets():
    def __init__(self, object,  object_name):
        self.object = object
        self.name   = object_name


# Set up the app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


#sim_cfg_ORDERS_RECORDS_FILE_PATH
# transactions_dataset ={}

def check_file_existance(File_path):
    try:
         with open(File_path, 'r') :
            return True
    except:
        return False



def get_inventory_dataset():
    INVENTORY_FILE = sim_cfg.INVENTORY_FILE

    while not check_file_existance(INVENTORY_FILE):
        print("  Waiting for INVENTORY_FILE", end='\r', flush=True)
        time.sleep(0.3)

    with open(INVENTORY_FILE, 'r') as file:
        data=file.read()   #aqui entra como str

        data=json.loads(data)         #rebenta aqui com :    00
        df1 = pd.DataFrame([])
        for actor in data:
            for prod_list in data[actor]:
                for prod in prod_list:
                    df2 = pd.DataFrame( [ [ actor, prod, prod_list[prod] ]  ]  , columns=["Ator","Product", "Quantity"] )
                df1=df1.append(df2)
        file.close

        # with open("inventario.txt", 'a') as f:
        #     f.write(df1.to_string())   #aqui entra como str

        return df1.sort_values(by='Ator')


inventory_dataset= get_inventory_dataset()


inventory_dataset_columns = inventory_dataset.columns

def get_transactions_dataset():

    transactions_file = sim_cfg.TRANSCTIONS_RECORDS_FILE

    while not check_file_existance(transactions_file):
        print("Waiting for transactions_file", end='\r', flush = True)
        time.sleep(0.1)

    with open(transactions_file, 'r') as file:
        data=file.read()+"{}]"  #fecha o array

        return pd.read_json(data)



transactions_dataset =  get_transactions_dataset()



def get_actors_oders():
    orders_datasets={}
    dir_files=os.listdir(sim_cfg.ORDERS_RECORDS_FILE_PATH)

    for file in dir_files:
        if file[0:6] == "orders":
            orders_datasets[file[:-4]] = pd.read_csv(sim_cfg.ORDERS_RECORDS_FILE_PATH + file, names=["Time", "Product", "Qty","Client","Order_id","Status"] )

            # elif file[0:12] == "transactions":
            #     transactions_dataset =  pd.read_json('TRANSCTIONS_RECORDS_FILE.json' )
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
                            data=inventory_dataset.to_dict('records')
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
                               style_table={'height': '200px', 'overflowY': 'auto'} ),
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
            interval=.5*1000, # in milliseconds
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
def update_inventory_table(n):
    inventory_dataset=get_inventory_dataset()
    return inventory_dataset.to_dict('records')


if __name__ == "__main__":
    app.run_server(debug=False)

