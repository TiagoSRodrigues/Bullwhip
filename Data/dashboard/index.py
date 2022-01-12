import dash_core_components as dcc
import dash_html_components as html
import dash

from app import app
from dashboard_page_1 import layout_page_1
from dashboard_page_2 import layout_page_2
import callbacks

from dash import callback_context


"""
call backs
"""



@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    dash.dependencies.Input('btn-nclicks-1', 'n_clicks'),
    dash.dependencies.Input('btn-nclicks-2', 'n_clicks'),
    dash.dependencies.Input('btn-nclicks-3', 'n_clicks')


)
def display_page(btn1, btn2, btn3):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if "btn-nclicks-1" in changed_id:
        return layout_page_1
    elif'btn-nclicks-2' in changed_id:
        return layout_page_2
    elif 'btn-nclicks-3' in changed_id:
        pass
        #msg = 'Button 3 was most recently clicked'
    else:
        return layout_page_1



if __name__ == '__main__':
    app.run_server(debug=False)
    
    
    