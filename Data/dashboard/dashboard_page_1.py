from re import X
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

import plotly.express as px
import pandas as pd
import db_connections as db_con
import time
import dash
from dash import dcc
from dash import html
import os
import sys
import json
import pandas as pd
from dash.dependencies import Input, Output
from dash import dash_table
import data_processing as dp

""" Get data """
mongo = db_con.db_connection()

#imports
actors_list = mongo.get_actors_id()
active_actors = actors_list[1:]




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





layout_page_1 = html.Div(
    [
        html.Div(id='app-1-display-value'),

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