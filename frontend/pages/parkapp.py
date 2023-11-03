import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import random

dash.register_page(__name__) #signifies homepage

#sample_data = pd.read_csv('D:/Data Science and Analytics/DSA3101/dsa3101-2310-14-carpark/frontend/data/sample_data_frontend_2.csv') ### CHANGE TO UR LOCAL DIR

# Variables
campus_events = ['No Event','First Week New AY', 'Well-Being Day', 'Commencement', 'Examinations', 'Staff WFH Day', 'Rag & Flag Day', 'SuperNova', 'Open Day', 'Public Holiday']
months = [{'label':'January','value':1},{'label':'February','value':2},{'label':'March','value':3},{'label':'April','value':4},
          {'label':'May','value':5},{'label':'June','value':6},{'label':'July','value':7},{'label':'August','value':8},
          {'label':'September','value':9},{'label':'October','value':10},{'label':'November','value':11},{'label':'December','value':12}]

default_button = "100"
default_arrivals = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0}

#Helper function to generate arrival rates given month
def generate_arrival_rate_month(x):
    keys = range(0,24)
    random_numbers = [random.randint(1, 1000) for _ in range(24)]
    d = dict(zip(keys,random_numbers))
    #temp = sample_data[sample_data["month"] == x]
    #d = temp.set_index("hour")["delta_nett"].to_dict()
    return d

def generate_arrival_rate_event(x):
    keys = range(0,24)
    random_numbers = [random.randint(1, 500) for _ in range(24)]
    d = dict(zip(keys,random_numbers))
    return d 

#Helper function to generate plots from dictionary representation
def generate_arrival_graph(d):
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates to Simulate</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width=300, height=300)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(minallowed=0)
    return fig



layout = dbc.Container([
    dbc.Row([
        dbc.Col( # Left partition
            html.Div([
                html.H4("Currently Simulating:"),
                html.Div("None",id = "simulation-contents")
            ]
            ),style = {'text-align':'center','background-color':'#003d7c','padding-top':'1%','color':'#FFFFFF'}
            ),
        dbc.Col( # Center partition
            html.Div([
            html.Div(html.Img(src=dash.get_asset_url('nus_map.png'), style={'width': '100%', 'height': 'auto'}), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
            html.Div([
                html.Button(default_button, id='cp3', className = 'cp-button', style = {'top':'16%', 'left':'27%'}),
                html.Div('CP3', style = {'position': 'absolute', 'top': '12.5%', 'left': '27.7%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp3a', className = 'cp-button', style = {'top':'17%', 'left':'32%'}),
                html.Div('CP3A', style = {'position': 'absolute', 'top': '13.5%', 'left': '32.3%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp4', className = 'cp-button', style = {'top':'32%', 'left':'34%'}),
                html.Div('CP4', style = {'position': 'absolute', 'top': '39%', 'left': '34.8%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp5', className = 'cp-button',style = {'top':'34%', 'left':'43%'}),
                html.Div('CP5', style = {'position': 'absolute', 'top': '41%', 'left': '43.8%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp5b', className = 'cp-button', style = {'top':'25.5%', 'left':'42%'}),
                html.Div('CP5B', style = {'position': 'absolute', 'top': '22%', 'left': '42.3%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp6b', className = 'cp-button', style = {'top':'62%', 'left':'62%'}),
                html.Div('CP6B', style = {'position': 'absolute', 'top': '69%', 'left': '62.3%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp10', className = 'cp-button', style = {'top':'53%', 'left':'84%'}),
                html.Div('CP10', style = {'position': 'absolute', 'top': '60%', 'left': '84.3%', 'font-weight': 'bold'})
                ]
                ),
                ],
                style={'position': 'relative', 'font-size': '22.8px'}
            ),
            width=8,
            style= {'padding': '0px'}
            ),
        dbc.Col([ # Right partition
            html.Div([html.Div(html.B("Select Event")),
            html.Div(dcc.Dropdown(id = 'event-picker', options=campus_events, value = "No Event", clearable = False))]),
            html.Br(),
            html.Div([html.Div(html.B("Select Month")),
            html.Div(dcc.Dropdown(id = 'month-picker', options=months))]),
            html.Br(),
            html.Div(dcc.Graph(id = "arrival-graph",config = {'staticPlot': True},figure = generate_arrival_graph(default_arrivals)),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
            html.Br(),
            html.Button('Refine Arrival Rate', id='refine-button', style={'margin-bottom':'2%'}),
            html.Button('Reset Parameters', id='reset-button', style={'display':'inline-block','margin-right':'2%'}),
            html.Button('Simulate', id='simulate-button', style={'display':'inline-block'})
            ], 
            style = {'text-align':'center','padding-top':'2%', 'background-color':'#ef7c00'})
            ])
    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})


# Callback for select event interactions with select month
# Can only select month when value of select event is No Event
@callback(
    Output(component_id = "month-picker", component_property='value'),
    Output(component_id = "month-picker", component_property = 'placeholder'),
    Output(component_id = "month-picker", component_property = 'disabled'),
    Input(component_id='event-picker', component_property='value')
)
def disable_month(event):
    if event == "No Event":
        return dash.no_update,"Select Month...",False
    else:
        return None, "Cannot Select Month", True
    
# Callback to display graph of selected month
@callback(
    Output(component_id = 'arrival-graph', component_property = 'figure'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value')
    
)
def update_graph(month,event):
    if month is None and event == "No Event":
        return generate_arrival_graph(default_arrivals)
    elif month is not None and event == "No Event":
        d = generate_arrival_rate_month(month)
        return generate_arrival_graph(d)
    else:
        d = generate_arrival_rate_event(event)
        return generate_arrival_graph(d) 

'''
# Callback to display grpah of selected event
@callback(
    Output(component_id = 'arrival-graph', component_property = 'figure',allow_duplicate=True),
    Input(component_id = 'event-picker', component_property = 'value'),
    prevent_initial_call = True
)
def update_graph_event(event):
    if event != 'No Event':
        d = generate_arrival_rate_event(event)
        return generate_arrival_graph(d)
    else:
        return dash.no_update'''


# Callback to revert to original settings and carpark state
@callback(
    Output(component_id='simulation-contents',component_property='children'),
    Output(component_id='arrival-graph', component_property='figure',allow_duplicate=True),
    Output(component_id='cp3',component_property='children'),
    Output(component_id='cp3a',component_property='children'),
    Output(component_id='cp4',component_property='children'),
    Output(component_id='cp5',component_property='children'),
    Output(component_id='cp5b',component_property='children'),
    Output(component_id='cp6b',component_property='children'),
    Output(component_id='cp10',component_property='children'),
    Output(component_id='month-picker',component_property='value', allow_duplicate=True),
    Output(component_id='event-picker',component_property='value'),
    Input(component_id='reset-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def reset_state(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-button' in changed_id:
        return 'None',generate_arrival_graph(default_arrivals),default_button,default_button,default_button,default_button,default_button,default_button,default_button,None,"No Event"
    else:
        return dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(
    Output(component_id='simulation-contents',component_property='children',allow_duplicate=True),
    Output(component_id='arrival-graph', component_property='figure', allow_duplicate=True),
    Output(component_id='cp3',component_property='children',allow_duplicate=True),
    Output(component_id='cp3a',component_property='children',allow_duplicate=True),
    Output(component_id='cp4',component_property='children',allow_duplicate=True),
    Output(component_id='cp5',component_property='children',allow_duplicate=True),
    Output(component_id='cp5b',component_property='children',allow_duplicate=True),
    Output(component_id='cp6b',component_property='children',allow_duplicate=True),
    Output(component_id='cp10',component_property='children',allow_duplicate=True),
    Input(component_id='simulate-button', component_property='n_clicks'),
    State(component_id='cp3',component_property='children'),
    prevent_initial_call=True
)
def test(clicks,hi):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'simulate-button' in changed_id:
        return str(int(hi)+1),generate_arrival_graph(default_arrivals),str(int(hi)+1),"1","1","1","1","1","1"
    else:
        return dash.no_update,dash.no_update,dash.no_update, dash.no_update,dash.no_update, dash.no_update,dash.no_update, dash.no_update,dash.no_update