import dash
import dash_bootstrap_components as dbc
from re import X
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc




# Set up the app
external_stylesheets = [dbc.themes.BOOTSTRAP, "assets/object_properties_style.css"]
app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)
server = app.server









""" 
HEADER 
"""
# modal_overlay = dbc.Modal(
#     [
#         dbc.ModalBody(html.Div([dcc.Markdown("howto_md")], id="howto-md")),
#         dbc.ModalFooter(dbc.Button("Close", id="howto-close", className="howto-bn")),
#     ],
#     id="modal",
#     size="lg",
# )

# Buttons
button_gh = dbc.Button(
    "Learn more",
    id="howto-open",
    outline=True,
    color="secondary",
    # Turn off lowercase transformation for class .button in stylesheet
    style={"textTransform": "none"},
)

button_made_by = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/TiagoSRodrigues/Bullwhip",
    id="gh-link",
    style={"text-transform": "none"},
)
# Define Header Layout
header = dbc.Navbar(
    dbc.Container([
            dbc.Row(
                [
                    dbc.Col(
                        html.A(
                            html.Img(
                                src=app.get_asset_url("dash-logo-new.png"),
                                height="30px",
                            ),
                            href="https://plotly.com/dash/",
                        ),
                    width=3,),
                    dbc.Col(
                        dbc.Row([
                            html.Div("Bullwhip simulator",style= {"color": "white",
                                                                           "font-weight": "bold",
                                                                           "font-size":"150%" ,
                                                                           "align":"left"},
                                     ),
                            html.Div("by: Tiago Rodrigues",style= {"color": "gray",
                                                                           "font-weight": "bold", 
                                                                           "align":"left"},
                                     )
                         
                        ]),
                        width=4,),       
           
                    dbc.Col(
                        html.Div([
                                html.Button('Actores', id='btn-nclicks-1', n_clicks=0),
                                html.Button('Transactions', id='btn-nclicks-2', n_clicks=0),
                                html.Button('Stats', id='btn-nclicks-3', n_clicks=0),
                                html.Div(id='container-button-timestamp')
                            ]), width=5,),
             
                ],align="center" )
            ,]
        ,
        fluid=False,
    ),
    color="dark",
    dark=True,
)




def page_content():
    pass

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    header,
    html.Div(id='page-content')
])
