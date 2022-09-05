from re import X
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
# from dash_html_components.Center import Center

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
def get_transactions_table_html():
    data=dp.get_transactions_df()

    table=dash_table.DataTable(
        id='transactions',
        columns=[{"name": i, "id": i} for i in data.columns],
        style_as_list_view=True,
        style_header={ 'border': '1px solid black' },
        style_cell={ 'border': '1px solid grey',
                    "heigth ": "50%",
},
        data=data.to_dict('records'),
     )

    return table


transactions_card = dbc.Card(
    [
        dbc.CardHeader(html.H3("Transactions"), style={"font-weight": "bold","text-align": "center"}),
        dbc.CardBody(
            dbc.Row(

                    get_transactions_table_html() ,
            )

            )
    ]
)





layout_page_2 = html.Div(
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
                     html.Div( [ transactions_card ]), md=12)

            ])
    ],
            fluid=True,
        ),
 ]
)