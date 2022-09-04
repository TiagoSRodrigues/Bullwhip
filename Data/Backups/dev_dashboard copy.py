import dash
from dash import dcc
from dash import html
import os, sys, json
from dash_html_components.Title import Title
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dash_table
try: import simulation_configuration as sim_cfg
except:
    sys.path.append('N:/TESE/Bullwhip')
    import simulation_configuration as sim_cfg



dir_files =  os.listdir( __file__[:-17].replace('\\','//') )


# Set up the app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


orders_datasets={}
# transactions_datasets={}
for file in dir_files:
    if file[0:6] == "orders":
       orders_datasets[file] = pd.read_csv(file, names=["Time", "Product", "Qty","Client","Order_id","Status"] )

    # elif file[0:12] == "transactions":
    #     transactions_dataset =  pd.read_json('TRANSCTIONS_RECORDS_FILE.json' )


def get_transactions_dataset():
    with open(sim_cfg.TRANSCTIONS_RECORDS_FILE, 'r') as file:
        data=file.read()+"]"
        data=data.replace("'", '"')
        data=data.replace("False", str('"'+"False"+'"'))
    return data

transactions=get_transactions_dataset()

transactions_dataset =  pd.read_json(transactions)



# Format the Table columns
transactions_columns=transactions_dataset.columns
# print(columns)
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




# Define Cards

left_card = dbc.Card(
    [
        dbc.CardHeader(html.H2("Actors Orders")),
        dbc.CardBody(
            dbc.Row(
                dbc.Col(
                    # dcc.Graph(
                    #     id="graph",
                    #     figure=image_with_contour(
                    #         img,
                    #         current_labels,
                    #         table,
                    #         color_column="area",
                    #     ),
                    # ),
                )
            )
        ),
        dbc.CardFooter(
            dbc.Row(
                [
                ],
                align="center",
            ),
        ),
    ]
)


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
            [dbc.Row([dbc.Col(left_card, md=6), dbc.Col(transactions_card, md=6)])],
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


@app.callback(
    Output("transactions-table", "data"),
     Input('interval-component', 'n_intervals'))
def update_table(n):

    transactions_dataset = pd.read_json(get_transactions_dataset() )
    return transactions_dataset.to_dict('records')


if __name__ == "__main__":
    app.run_server(debug=True)