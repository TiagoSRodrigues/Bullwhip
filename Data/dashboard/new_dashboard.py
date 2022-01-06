import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import db_connections as db_con



db= db_con.db_connection()

#db.get_collection_data(collection_name="db_log")


#app = dash.Dash()

df = pd.DataFrame.from_dict(db.get_inventories(), orient='index')

print(df)

# fig = px.scatter(
#     df,
#     x="GDP",
#     y="Life expectancy",
#     size="Population",
#     color="continent",
#     hover_name="Country",
#     log_x=True,
#     size_max=60,
# )

# app.layout = html.Div([dcc.Graph(id="life-exp-vs-gdp", figure=fig)])


# if __name__ == "__main__":
#     app.run_server(debug=True)