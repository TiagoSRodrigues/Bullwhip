from re import X
import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.express as px
import pandas as pd
import db_connections as db_con
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import sys
import json
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
import data_processing as dp

""" Get data """
mongo = db_con.db_connection()

def update_inventories():
    return mongo.get_inventories()
def update_transactions():
    return mongo.get_transactions
def update_orders():
    return mongo.get_orders




class datasets():
    def __init__(self, object,  object_name):
        self.object = object
        self.name   = object_name


# Set up the app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#imports
actors_list = mongo.get_actors_id()
active_actors = actors_list[1:]


""" 
HEADER 
"""
modal_overlay = dbc.Modal(
    [
        dbc.ModalBody(html.Div([dcc.Markdown("howto_md")], id="howto-md")),
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


"""
inventory
"""
def get_inventory_table_html():
    table_list=[]
    for actor in actors_list:
        data=dp.get_actor_inventory_df(actor_id=actor)
        #print(data)
        
        label=html.Label("Actor "+str(actor)),
        table=dash_table.DataTable(
            id='inventory_'+str(actor),
            columns=[{"name": i, "id": i} for i in data.columns],
            data=data.to_dict('records'),
         )
        
        div=html.Div([
                        html.Label(
                            "Actor "+str(actor),
                            style={ "font-weight": "bold","text-align": "center" }, 

                            
                            
                            
                            ),
                        table
                        ],
                     style={'padding': 5, 'flex': 1})
        table_list.append(div)
    return table_list


def get_orders_table_html():
    table_list=[]
    for actor in active_actors:
        data=dp.get_actor_orders_df(actor_id=actor)
        #print(data)
        
        label=html.Label("Actor "+str(actor)),
        table=dash_table.DataTable(
            id='orders_'+str(actor),
            columns=[{"name": i, "id": i} for i in data.columns],
            data=data.to_dict('records'),
         )
        
        div=html.Div([
                        html.Label(
                            "Actor "+str(actor),
                            style={ "font-weight": "bold","text-align": "center" }, 

                            
                            
                            
                            ),
                        table
                        ],
                     style={'padding': 5, 'flex': 1})
        table_list.append(div)
    return table_list



inventory_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Inventory")),
        dbc.CardBody(
            dbc.Row(
                           
                    get_inventory_table_html() ,
            )
               
            )
    ]
)
orders_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Orders")),
        dbc.CardBody(
            dbc.Row(
                           
                    get_orders_table_html() ,
            )
               
            )
    ]
)





app.layout = html.Div(
    [
        header,
        dbc.Container(
            [dbc.Row([
                dbc.Col(
                    html.Div( id="actors_inventory_table",
                                    className="actors_inventory_row")
                                    ,  md=12
                            ),
                dbc.Col(
                     html.Div( [ inventory_card, orders_card ]), md=12)

            ])
    ],
            fluid=True,
        ),
   dcc.Interval(
            id='interval-component',
            interval=1, # in milliseconds
            n_intervals=0
        ) ]
)


# html.Div([
#     html.H1('Hello Dash'),
#     html.Div([
#         html.P('Dash converts Python classes into HTML'),
#         html.P("This conversion happens behind the scenes by Dash's JavaScript front-end")
#     ])
# ])





if __name__ == '__main__':
    app.run_server(debug=True)