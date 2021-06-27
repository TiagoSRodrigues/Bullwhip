import pandas as pd
            
import dash
import dash_core_components as dcc
import dash_html_components as html
import os, sys, json
from dash_html_components.Title import Title 
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table
try: import simulation_configuration as sim_cfg 
except: 
    sys.path.append('N:/TESE/Bullwhip')
    import simulation_configuration as sim_cfg 

class dashboard_data():
    def __init__(self, simulation_object, options=None):
        self.simulation = simulation_object

        self.open_transactions              = []
        self.delivered_transactions         = []
        self.transactions_log               = []
        self.transaction_id                 = 0 #parece que n precisam ser iniciados logo

        self.actors_dataset={}
        #simulation data

        self.update_datasets(self.simulation)
        #actors data

        
        self.create_dashboard(self.simulation)
    #isto vai precisar de ser otimizado!!! mas até lá good enough 
    def update_datasets(self, simulation ):
        self.simulation = simulation

        time =  self.simulation.time

        self.open_transactions  = self.simulation.ObejctTransationsRecords.open_transactions 
        self.delivered_transactions  = self.simulation.ObejctTransationsRecords.delivered_transactions 

        self.transaction_id         = self.simulation.ObejctTransationsRecords.transaction_id 
    #   
        self.actors_collection=self.simulation.actors_collection
        
        for actor in self.actors_collection:
            name , id = actor.name , actor.id
            Open_Orders, closed_orders = actor.actor_stock_record.Open_Orders_Record, actor.actor_stock_record.closed_orders_record
            invetory= actor.actor_inventory.main_inventory
            self.actors_dataset[str(id)] = [name, Open_Orders, closed_orders, invetory]

            #example os iventary {1001: {'Composition': {'2001': 1}, 'Name': 'ProductA', 'id': 1001, 'safety_stock': 2, 'in_stock': 10},


        self.get_transactions_dataset()
        self.update_table()

    def get_transactions_dataset(self):
        data=self.open_transactions
        data=str(data)
        data=data.replace("'", '"')
        data=data.replace("False", str('"'+"False"+'"'))
        data=data.replace("True", str('"'+"True"+'"'))
        
        return pd.read_json(data)

    def create_dashboard(self, simulation):
        print("criating dashboard")
        external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        server = app.server

        transactions_dataset = self.get_transactions_dataset()


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
                                        src=app.get_asset_url("assets/dash-logo-new.png"),
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


        # @app.callback(
        #     Output("transactions-table", "data"),


        app.run_server(debug=True)
        #     Input('interval-component', 'n_intervals'))
    def update_table(self):
        
        transactions_dataset = pd.read_json(self.get_transactions_dataset() )
        return self.create_dashboard.transactions_dataset.to_dict('records')
    