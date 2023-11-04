import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import random
import time

import os
path = os.getcwd()

import sys
sys.path.append(path + r'\backend\des')

from params import get_month_arrival_rate, get_day_arrival_rate


dash.register_page(__name__) #signifies homepage


#sample_data = pd.read_csv('D:/Data Science and Analytics/DSA3101/dsa3101-2310-14-carpark/frontend/data/sample_data_frontend_2.csv') ### CHANGE TO UR LOCAL DIR

# Variables
campus_events = ['No Event','Week 0 New AY', 'Well-Being Day', 'Commencement', 'Examinations', 'Staff WFH Day', 'Rag & Flag Day', 'SuperNova', 'Open Day', 'Public Holiday']
months = [{'label':'January','value':1},{'label':'February','value':2},{'label':'March','value':3},{'label':'April','value':4},
          {'label':'May','value':5},{'label':'June','value':6},{'label':'July','value':7},{'label':'August','value':8},
          {'label':'September','value':9},{'label':'October','value':10},{'label':'November','value':11},{'label':'December','value':12}]
month_dict = {1: 'January', 2: 'Februrary', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 
                      8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December' }
default_button = "0"
default_arrivals = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0}
cp_names = {'cp3':'UCC/YST Conservatory of Music', 'cp3a':'LKCNHM', 'cp4':'Raffles Hall/CFA', 'cp5':'University Sports Centre', 'cp5b':'NUS Staff Club', 'cp6b':'University Hall', 'cp10':'S17'}

# Sample Data for Months
month_data_values = [dict(zip(range(0,24),[random.randint(1, 1000) for _ in range(24)])) for i in range(12)]
month_data_keys = range(1,13)
month_data = dict(zip(month_data_keys,month_data_values))

# Sample Data Events
events_data_values = ['','2022-08-01','2022-10-21','2022-07-16','2022-11-21','2023-04-06','2022-08-06','2022-08-12','2023-03-04','2023-01-01']
events_data = dict(zip(campus_events,events_data_values))

#Helper function to generate arrival rates given month
def generate_arrival_rate_month(x):
    #keys = range(0,24)
    #random_numbers = [random.randint(1, 1000) for _ in range(24)]
    #d = dict(zip(keys,random_numbers))
    #temp = sample_data[sample_data["month"] == x]
    #d = temp.set_index("hour")["delta_nett"].to_dict()
    return get_month_arrival_rate(x)

def generate_arrival_rate_event(x):
    date = events_data[x]
    d = get_day_arrival_rate(date)
    nd = {}

    for i in range(24):
        if i in d.keys():
            nd[i] = d[i]
        else:
            nd[i] = 0

    return nd

# Helper function to run fake simulation
def simulate_des(arrival_rates, lots_d):
    cp3_ls = [random.randint(1, 1000), random.randint(1, 1000), random.randint(1, 500),random.randint(1, 500), 30, 10]
    cp3a_ls = [random.randint(1, 1000), random.randint(1, 1000), random.randint(1, 500),random.randint(1, 500), 30, 5]
    cp4_ls = [random.randint(1, 1000), random.randint(1, 1000), random.randint(1, 500),random.randint(1, 500), 30, 5]
    cp5_ls = [random.randint(1, 1000), random.randint(1, 1000), random.randint(1, 500),random.randint(1, 500), 30, 5]
    cp5b_ls = [random.randint(1, 1000), 78, random.randint(1, 500),78, 30, 0]
    cp6b_ls = [random.randint(1, 1000), 78, random.randint(1, 500),78, 30, 10]
    cp10_ls = [random.randint(1, 1000), 78, random.randint(1, 500),78, 30, 10]
    return {'cp3':cp3_ls, 'cp3a':cp3a_ls, 'cp4':cp4_ls, 'cp5':cp5_ls, 'cp5b':cp5b_ls,'cp6b':cp6b_ls, 'cp10':cp10_ls}


#Helper function to generate plots from dictionary representation
def generate_arrival_graph(d):
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates to Simulate</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width=300, height=300)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(rangemode='nonnegative')
    return fig

def generate_simulate_modal_graph(d):
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates to Simulate</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width=300, height=300)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(rangemode='nonnegative')
    return fig

def generate_simulation_graph(d):
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals',
                  labels = {'hour':'Hour of Day', 'arrivals': ''},width=250, height=250)
    fig.update_layout(margin = dict(l=0,r=0,b=0,t=0), font_family = "Open Sans")
    fig.update_yaxes(rangemode='nonnegative')
    return fig

def vert_slider(hour, val):
    return dbc.Col([html.Div(html.Div(str(val), id = "value_" + str(hour)), style= {'font-size':'16px','text-align':'center', 'margin-right':'50%'}),
                    html.Div(dcc.Slider(id = "slider_" + str(hour),min = 0, max = 9999, step = 1, value = val, vertical = True,marks = None), style={'padding':'0px','margin-left':'10%'}), 
                    html.Div(html.Div(str(hour)), style= {'text-align':'center', 'margin-right':'50%'})],style={'padding':'0px'})



#Helper function for refine graph modal
def refine_modal(base, d):
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Current Base: "+ base), close_button= False),
        dbc.ModalBody([html.H4("Drag Sliders to Modify Number of Cars arriving in NUS at each hour"),
                        dbc.Row([vert_slider(i, d[i]) for i in range(24)], id = 'row_slider', style={'padding-left':'2%'}),
                        html.B('Enter Hour')
                        ], style= {'text-align':'center', 'font-size':'19px'}),
                        
        dbc.ModalFooter([
                    dbc.Button('Reset to Base', id = 'refine-modal-reset',style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
                    dbc.Button(
                        "Save and Exit", id="close-refine-modal", style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}
                    )])
    ], id = 'refine-modal', is_open= False, backdrop = False, centered = True, size = 'xl')

# Helper function for carpark modal
def cp_modal(cp,a,b,c,d):
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(cp.upper() + ": " + cp_names[cp], style = {"color" : "white"}), close_button= False, style = {"background-color": "#003d7c"}),
        dbc.ModalBody([
            html.Div([
            html.B("Occupied Lots: " + str(a+c) + '/' + str(b+d), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(a) + '/' + str(b), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(c) + '/' + str(d), style = {"color" : "white"})], id = 'occupied_'+cp),
            html.Br(),
            html.H4('Simulation Parameters:', style = {"color" : "white"}),
            html.Div('Carpark Status:', style = {"color" : "white"}),
            html.Div(dcc.Dropdown(options=['Open','Closed'], id = 'cp_status_'+cp, value = "Open", clearable = False), style={'margin-bottom':'3%'}),
            html.Div([
            html.Div(html.Div('Adjust Red Lot Capacity:'),style= {'text-align':'center', 'color' : '#FF2800'}),
            html.Div(dcc.Slider(id = "slider_red_"+cp,min = 0, max = b, step = 1, value = b, marks = None)),
            html.Div(html.Div('Adjust White Lot Capacity:'),style= {'text-align':'center', 'color' : 'white'}),
            html.Div(dcc.Slider(id = "slider_white_"+cp,min = 0, max = d, step = 1, value = d, marks = None)),
            html.Div(
                [html.B("Red Lot Capacity to Simulate: " + str(b) + " (100% Capacity)",id = 'to_simulate_red_'+cp, style = {'font-size':'15px', 'color':'#FF2800'}),
                 html.Br(),
                html.B("White Lot Capacity to Simulate: " + str(d) + " (100% Capacity)",id = 'to_simulate_white_'+cp, style = {'font-size':'15px', "color" : "white"})]
            )
            ])

        ], style= {'text-align':'center', 'font-size':'19px', "background-color": "#003d7c"}),
        dbc.ModalFooter([
                    dbc.Button('Reset Parameters', id = 'reset-modal-'+cp,style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
                    dbc.Button(
                        "Save and Exit", id="close-modal", style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}
                    )]
                    , style = {"background-color" : "#003d7c"})
    ], id = 'modal-'+cp, is_open= False, backdrop = False, centered = True)

# Helper function for confirmation of simulation modal
def simulate_modal():
    return dbc.Modal([
         dbc.ModalHeader(dbc.ModalTitle('Initializing Simulation:'), close_button= False),
         dbc.ModalBody(id = 'simulate-modal-contents', style = {'text-align':'center', 'font-size':'15px'}),
         dbc.ModalFooter([
            html.H5("Confirm Simulation?"),
            dbc.Button('Yes', id = 'simulate-modal-yes' ,style = {'background-color':'#06a11b', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
            dbc.Button('No', id = 'simulate-modal-no' ,style = {'background-color':'red', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
         ])
    ], id = 'simulate-modal', is_open = False, backdrop = False, centered = True)


# layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col( # Left partition
            html.Div([
                html.H4("Currently Simulating:", style={'font-weight':'bold'}),
                html.Div("None",id = "simulation-contents")
            ]
            ),
            width={'size': 2, 'order': 1},
            style = {'text-align':'center','background-color':'#003d7c','padding-top':'1%','color':'#FFFFFF'}
            ),
        dbc.Col( # Center partition
            html.Div([
            html.Div(html.Img(src=dash.get_asset_url('nus_map.png'), style={'width': '100%', 'height': 'auto'}), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
            html.Div([
                html.Button(default_button, id='cp3', className = 'cp-button', style = {'top':'16%', 'left':'27%'}),
                html.Div('CP3', style = {'position': 'absolute', 'top': '12%', 'left': '27.7%', 'font-weight': 'bold'})
                ]
                ),
            html.Div([
                html.Button(default_button, id='cp3a', className = 'cp-button', style = {'top':'17%', 'left':'32%'}),
                html.Div('CP3A', style = {'position': 'absolute', 'top': '13%', 'left': '32.3%', 'font-weight': 'bold'})
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
                html.Div('CP5B', style = {'position': 'absolute', 'top': '21.5%', 'left': '42.3%', 'font-weight': 'bold'})
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
            width={'size': 8, 'order': 2},
            style= {'padding': '0px'}
            ),
        dbc.Col([ # Right partition
            html.Div([html.Div(html.B("Select Event")),
            html.Div(dcc.Dropdown(id = 'event-picker', options=campus_events, value = "No Event", clearable = False))]),
            html.Br(),
            html.Div([html.Div(html.B("Select Month")),
            html.Div(dcc.Dropdown(id = 'month-picker', options=months))]),
            html.Br(),
            html.Div(dcc.Graph(id = "arrival-graph",config = {'staticPlot': True},figure = generate_arrival_graph(default_arrivals), style={'width': '100%'}),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'width': '100%'}),
            html.Br(),
            dbc.Button('Refine Arrival Rate', id='refine-button', style={'margin-bottom':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
            dbc.Button('Reset All', id='reset-button', style={'margin-bottom':'2%','display':'inline-block','margin-right':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            dbc.Button('Simulate', id='simulate-button', style={'margin-bottom':'2%','display':'inline-block', 'background-color':'#000000', 'color' : '#FFFFFF' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
            dbc.Button('Reset CP Params', id='reset-cp-button', style={'display':'inline-block','margin-bottom':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
            dbc.Button('Reset Events and Months', id='reset-events-button', style={'display':'inline-block', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            ], 
            width={'size': 2, 'order': 3},
            style = {'text-align':'center','padding-top':'2%', 'background-color':'#ef7c00'})
            ]),
            html.Div(refine_modal('No Event', default_arrivals), id = 'refine-modal-block'),
            html.Div(cp_modal("cp3",0,31,0,212), id = 'cp3_modal'),
            html.Div(cp_modal("cp3a",0,14,0,53), id = 'cp3a_modal'),
            html.Div(cp_modal("cp4",0,21,0,95), id = 'cp4_modal'),
            html.Div(cp_modal("cp5",0,17,0,53), id = 'cp5_modal'),
            html.Div(cp_modal("cp5b",0,32,0,0), id = 'cp5b_modal'),
            html.Div(cp_modal("cp6b",0,130,0,43), id = 'cp6b_modal'),
            html.Div(cp_modal("cp10",0,211,0,164), id = 'cp10_modal'),
            html.Div(dbc.Modal([dbc.ModalBody("All Carpark Parameters have been resetted!"),dbc.ModalFooter(dbc.Button("Close", id="close-reset-cp-modal"))],id="reset-cp-modal",is_open=False)),
            html.Div(dbc.Modal([dbc.ModalBody("All Events and Months have been resetted!"),dbc.ModalFooter(dbc.Button("Close", id="close-reset-events-modal"))],id="reset-events-modal",is_open=False)),
            html.Div(dbc.Modal([dbc.ModalBody("All simulations and settings have been resetted!"),dbc.ModalFooter(dbc.Button("Close", id="close-reset-all-modal"))],id="reset-all-modal",is_open=False)),
            html.Div(simulate_modal()),
            html.Div(dbc.Modal([
                dbc.ModalBody([
                html.B("Simulation in Progress! Please wait..."), 
                html.Div(dbc.Spinner(color="primary", type="border"), style = {'float':'right'})
                ]),
                ],id="loading-modal",is_open=False,backdrop = False,
        ))

    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})

'''
CALLBACKS FOR CARPARKS
'''
# Callback to toggle cp modal
@callback(
        Output('modal-cp3','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp3','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp3" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp3','disabled'),
    Output('slider_white_cp3','disabled'),
    Input('cp_status_cp3','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp3','children'),
    Output('to_simulate_white_cp3','children'),
    Input('cp_status_cp3','value'),
    Input('slider_red_cp3','value'),
    Input('slider_white_cp3','value'),
    State('slider_red_cp3', 'max'),
    State('slider_white_cp3', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp3','value'),
    Output('slider_white_cp3','value'),
    Output('cp_status_cp3','value'),
    Input('reset-modal-cp3','n_clicks'),
    State('slider_red_cp3','max'),
    State('slider_white_cp3','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp3' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update


# Callback to toggle cp modal
@callback(
        Output('modal-cp3a','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp3a','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp3a" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp3a','disabled'),
    Output('slider_white_cp3a','disabled'),
    Input('cp_status_cp3a','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp3a','children'),
    Output('to_simulate_white_cp3a','children'),
    Input('cp_status_cp3a','value'),
    Input('slider_red_cp3a','value'),
    Input('slider_white_cp3a','value'),
    State('slider_red_cp3a', 'max'),
    State('slider_white_cp3a', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp3a','value'),
    Output('slider_white_cp3a','value'),
    Output('cp_status_cp3a','value'),
    Input('reset-modal-cp3a','n_clicks'),
    State('slider_red_cp3a','max'),
    State('slider_white_cp3a','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp3a' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp4','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp4','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp4" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp4','disabled'),
    Output('slider_white_cp4','disabled'),
    Input('cp_status_cp4','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp4','children'),
    Output('to_simulate_white_cp4','children'),
    Input('cp_status_cp4','value'),
    Input('slider_red_cp4','value'),
    Input('slider_white_cp4','value'),
    State('slider_red_cp4', 'max'),
    State('slider_white_cp4', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp4','value'),
    Output('slider_white_cp4','value'),
    Output('cp_status_cp4','value'),
    Input('reset-modal-cp4','n_clicks'),
    State('slider_red_cp4','max'),
    State('slider_white_cp4','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp4' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp5','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp5','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp5" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp5','disabled'),
    Output('slider_white_cp5','disabled'),
    Input('cp_status_cp5','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp5','children'),
    Output('to_simulate_white_cp5','children'),
    Input('cp_status_cp5','value'),
    Input('slider_red_cp5','value'),
    Input('slider_white_cp5','value'),
    State('slider_red_cp5', 'max'),
    State('slider_white_cp5', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp5','value'),
    Output('slider_white_cp5','value'),
    Output('cp_status_cp5','value'),
    Input('reset-modal-cp5','n_clicks'),
    State('slider_red_cp5','max'),
    State('slider_white_cp5','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp5' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update


# Callback to toggle cp modal
@callback(
        Output('modal-cp5b','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp5b','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp5b" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp5b','disabled'),
    Output('slider_white_cp5b','disabled'),
    Input('cp_status_cp5b','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp5b','children'),
    Output('to_simulate_white_cp5b','children'),
    Input('cp_status_cp5b','value'),
    Input('slider_red_cp5b','value'),
    Input('slider_white_cp5b','value'),
    State('slider_red_cp5b', 'max'),
    State('slider_white_cp5b', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: 0 (100% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp5b','value'),
    Output('slider_white_cp5b','value'),
    Output('cp_status_cp5b','value'),
    Input('reset-modal-cp5b','n_clicks'),
    State('slider_red_cp5b','max'),
    State('slider_white_cp5b','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp5b' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update



# Callback to toggle cp modal
@callback(
        Output('modal-cp6b','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp6b','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp6b" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp6b','disabled'),
    Output('slider_white_cp6b','disabled'),
    Input('cp_status_cp6b','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp6b','children'),
    Output('to_simulate_white_cp6b','children'),
    Input('cp_status_cp6b','value'),
    Input('slider_red_cp6b','value'),
    Input('slider_white_cp6b','value'),
    State('slider_red_cp6b', 'max'),
    State('slider_white_cp6b', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp6b','value'),
    Output('slider_white_cp6b','value'),
    Output('cp_status_cp6b','value'),
    Input('reset-modal-cp6b','n_clicks'),
    State('slider_red_cp6b','max'),
    State('slider_white_cp6b','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp6b' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp10','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp10','n_clicks')
        
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp10" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp10','disabled'),
    Output('slider_white_cp10','disabled'),
    Input('cp_status_cp10','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp10','children'),
    Output('to_simulate_white_cp10','children'),
    Input('cp_status_cp10','value'),
    Input('slider_red_cp10','value'),
    Input('slider_white_cp10','value'),
    State('slider_red_cp10', 'max'),
    State('slider_white_cp10', 'max'),
)
def params_to_simulate(status,red,white,red_max,white_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/white_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp10','value'),
    Output('slider_white_cp10','value'),
    Output('cp_status_cp10','value'),
    Input('reset-modal-cp10','n_clicks'),
    State('slider_red_cp10','max'),
    State('slider_white_cp10','max')
)
def reset_cp_params(clicks,max_red,max_white):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp10' in changed_id:
        return max_red, max_white, "Open"
    else:
        return dash.no_update, dash.no_update,dash.no_update



'''
CALLBACKS FOR Month and Event
'''
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
    Output('refine-modal-block','children'),
    Output(component_id = 'arrival-graph', component_property = 'figure'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value')
    
)
def update_graph(month,event):
    if month is None and event == "No Event":
        return refine_modal("No Event (Custom Arrivals)", default_arrivals),generate_arrival_graph(default_arrivals)
    elif month is not None and event == "No Event":
        d = generate_arrival_rate_month(month)
        return refine_modal(month_dict[month], d),generate_arrival_graph(d)
    else:
        d = generate_arrival_rate_event(event)
        return refine_modal(event, d),generate_arrival_graph(d) 

    
# Callback to toggle refine modal
@callback(
        Output('refine-modal','is_open'),
        Input('refine-button','n_clicks'),
        Input("close-refine-modal",'n_clicks')
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "refine-button" in changed_id:
        return True
    else:
        return False

# Callback to use refine modal to adjust graph arrival rates
@callback(
    Output('arrival-graph','figure', allow_duplicate=True),
    Output('value_0','children'),
    Output('value_1','children'),
    Output('value_2','children'),
    Output('value_3','children'),
    Output('value_4','children'),
    Output('value_5','children'),
    Output('value_6','children'),
    Output('value_7','children'),
    Output('value_8','children'),
    Output('value_9','children'),
    Output('value_10','children'),
    Output('value_11','children'),
    Output('value_12','children'),
    Output('value_13','children'),
    Output('value_14','children'),
    Output('value_15','children'),
    Output('value_16','children'),
    Output('value_17','children'),
    Output('value_18','children'),
    Output('value_19','children'),
    Output('value_20','children'),
    Output('value_21','children'),
    Output('value_22','children'),
    Output('value_23','children'),
    Input('slider_0','value'),
    Input('slider_1','value'),
    Input('slider_2','value'),
    Input('slider_3','value'),
    Input('slider_4','value'),
    Input('slider_5','value'),
    Input('slider_6','value'),
    Input('slider_7','value'),
    Input('slider_8','value'),
    Input('slider_9','value'),
    Input('slider_10','value'),
    Input('slider_11','value'),
    Input('slider_12','value'),
    Input('slider_13','value'),
    Input('slider_14','value'),
    Input('slider_15','value'),
    Input('slider_16','value'),
    Input('slider_17','value'),
    Input('slider_18','value'),
    Input('slider_19','value'),
    Input('slider_20','value'),
    Input('slider_21','value'),
    Input('slider_22','value'),
    Input('slider_23','value'),
    prevent_initial_call=True
)
def update_graph_after_refine(*args):
    d = dict(zip(range(24),args))
    return generate_arrival_graph(d), *args

# Callback to reset refine modal
@callback(
    Output('row_slider','children'),
    Output(component_id = 'arrival-graph', component_property = 'figure', allow_duplicate=True),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value'),
    Input(component_id='refine-modal-reset', component_property='n_clicks'),
    prevent_initial_call=True
)

def reset_refine_modal(month,event, clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'refine-modal-reset' in changed_id:
        if month is None and event == "No Event":
            return [vert_slider(i, default_arrivals[i]) for i in range(24)],generate_arrival_graph(default_arrivals)
        elif month is not None and event == "No Event":
            d = generate_arrival_rate_month(month)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_graph(d)
        else:
            d = generate_arrival_rate_event(event)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_graph(d)
    else:
        return dash.no_update, dash.no_update

# Callback for reset all: revert to original settings and carpark state
@callback(
    Output(component_id='cp3',component_property='style'),
    Output(component_id='cp3a',component_property='style'),
    Output(component_id='cp4',component_property='style'),
    Output(component_id='cp5',component_property='style'),
    Output(component_id='cp5b',component_property='style'),
    Output(component_id='cp6b',component_property='style'),
    Output(component_id='cp10',component_property='style'),
    Output(component_id = 'reset-all-modal', component_property = 'is_open'),
    Output(component_id='cp3_modal',component_property='children'),
    Output(component_id='cp3a_modal',component_property='children'),
    Output(component_id='cp4_modal',component_property='children'),
    Output(component_id='cp5_modal',component_property='children'),
    Output(component_id='cp5b_modal',component_property='children'),
    Output(component_id='cp6b_modal',component_property='children'),
    Output(component_id='cp10_modal',component_property='children'),
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
        return {'top':'16%', 'left':'27%','background-color':'green'},{'top':'17%', 'left':'32%','background-color':'green'}, {'top':'32%', 'left':'34%','background-color':'green'},{'top':'34%', 'left':'43%','background-color':'green'},{'top':'25.5%', 'left':'42%','background-color':'green'},{'top':'62%', 'left':'62%','background-color':'green'},{'top':'53%', 'left':'84%','background-color':'green'},True,cp_modal("cp3",0,31,0,212),cp_modal("cp3a",0,14,0,53),cp_modal("cp4",0,21,0,95), cp_modal("cp5",0,17,0,53),cp_modal("cp5b",0,32,0,0),cp_modal("cp6b",0,130,0,43),cp_modal("cp10",0,211,0,164),'None',generate_arrival_graph(default_arrivals),default_button,default_button,default_button,default_button,default_button,default_button,default_button,None,"No Event"
    else:
        return dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,True,dash.no_update,dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


# Callback to close reset all modals:
@callback(
        Output('reset-all-modal','is_open',allow_duplicate = True),
        Input("close-reset-all-modal",'n_clicks'),
        prevent_initial_call=True
)
def toggle_reset_all_modal(n1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "close-reset-all-modal" in changed_id:
        return False
    else:
        return True


'''
@callback(
    Output(component_id='simulation-contents',component_property='children',allow_duplicate=True),
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
        return str(int(hi)+1),str(int(hi)+1),"1","1","1","1","1","1"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update, dash.no_update,dash.no_update, dash.no_update,dash.no_update
    
'''

# Callback for reset cp params: reset params for all callparks only
@callback(
    Output(component_id='reset-cp-modal', component_property='is_open'),
    Output(component_id='cp3_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp3a_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp4_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp5_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp5b_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp6b_modal',component_property='children',allow_duplicate=True),
    Output(component_id='cp10_modal',component_property='children',allow_duplicate=True),
    Input(component_id='reset-cp-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def reset_all_cp_params(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-cp-button' in changed_id:
        return True,cp_modal("cp3",0,31,0,212),cp_modal("cp3a",0,14,0,53),cp_modal("cp4",0,21,0,95), cp_modal("cp5",0,17,0,53),cp_modal("cp5b",0,32,0,0),cp_modal("cp6b",0,130,0,43),cp_modal("cp10",0,211,0,164)
    else:
        return False,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update, dash.no_update

# Callback to close reset cp modals:
@callback(
        Output('reset-cp-modal','is_open',allow_duplicate = True),
        Input("close-reset-cp-modal",'n_clicks'),
        prevent_initial_call=True
)
def toggle_reset_cp_params_modal(n1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "close-reset-cp-modal" in changed_id:
        return False
    else:
        return True


# Callback for reset events: reset event and month selection only
@callback(
    Output(component_id='reset-events-modal', component_property='is_open'),
    Output(component_id='arrival-graph', component_property='figure',allow_duplicate=True),
    Output(component_id='month-picker',component_property='value', allow_duplicate=True),
    Output(component_id='event-picker',component_property='value',allow_duplicate=True),
    Input(component_id='reset-events-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def reset_events(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-events-button' in changed_id:
        return True,generate_arrival_graph(default_arrivals),None,"No Event"
    else:
        return False,dash.no_update,dash.no_update,dash.no_update

# Callback to close reset events modals:
@callback(
        Output('reset-events-modal','is_open',allow_duplicate = True),
        Input("close-reset-events-modal",'n_clicks'),
        prevent_initial_call=True
)
def toggle_reset_events_modal(n1):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "close-reset-events-modal" in changed_id:
        return False
    else:
        return True


'''
Simulation CALLBACKS
'''
# Toggle Simulation Confirmation Modal
@callback(
    Output('simulate-modal','is_open'),
    Input('simulate-button','n_clicks'),
    Input('simulate-modal-no','n_clicks'),
    Input('simulate-modal-yes','n_clicks')
)
def open_simulation_modal(n1,n2,n3):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'simulate-button' in changed_id:
        return True
    else:
        return False

# Callbacks for modal content
@callback(
    Output(component_id='simulate-modal-contents',component_property='children', allow_duplicate=True),
    Input(component_id='simulate-button', component_property='n_clicks'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value'),
    Input('slider_red_cp3','value'),
    Input('slider_red_cp3','max'),
    Input('slider_white_cp3','value'),
    Input('slider_white_cp3','max'),
    Input('slider_red_cp3a','value'),
    Input('slider_red_cp3a','max'),
    Input('slider_white_cp3a','value'),
    Input('slider_white_cp3a','max'),
    Input('slider_red_cp4','value'),
    Input('slider_red_cp4','max'),
    Input('slider_white_cp4','value'),
    Input('slider_white_cp4','max'),
    Input('slider_red_cp5','value'),
    Input('slider_red_cp5','max'),
    Input('slider_white_cp5','value'),
    Input('slider_white_cp5','max'),
    Input('slider_red_cp5b','value'),
    Input('slider_red_cp5b','max'),
    Input('slider_white_cp5b','value'),
    Input('slider_white_cp5b','max'),
    Input('slider_red_cp6b','value'),
    Input('slider_red_cp6b','max'),
    Input('slider_white_cp6b','value'),
    Input('slider_white_cp6b','max'),
    Input('slider_red_cp10','value'),
    Input('slider_red_cp10','max'),
    Input('slider_white_cp10','value'),
    Input('slider_white_cp10','max'),
    Input('slider_0','value'),
    Input('slider_1','value'),
    Input('slider_2','value'),
    Input('slider_3','value'),
    Input('slider_4','value'),
    Input('slider_5','value'),
    Input('slider_6','value'),
    Input('slider_7','value'),
    Input('slider_8','value'),
    Input('slider_9','value'),
    Input('slider_10','value'),
    Input('slider_11','value'),
    Input('slider_12','value'),
    Input('slider_13','value'),
    Input('slider_14','value'),
    Input('slider_15','value'),
    Input('slider_16','value'),
    Input('slider_17','value'),
    Input('slider_18','value'),
    Input('slider_19','value'),
    Input('slider_20','value'),
    Input('slider_21','value'),
    Input('slider_22','value'),
    Input('slider_23','value'),
    prevent_initial_call = True
)
def cp_simulation(clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max, cp5b_white_v, cp5b_white_max,
    cp6b_red_v, cp6b_red_max, cp6b_white_v, cp6b_white_max,
    cp10_red_v, cp10_red_max, cp10_white_v, cp10_white_max,
    *args):
     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
     if 'simulate-button' in changed_id:
        if event == "No Event" and month is None:
            if list(args) == list(default_arrivals.values()):
                first = html.B("Empty Simulation")
            else:
                first = html.B("Custom")
        elif event == "No Event":
            if list(args) == list(generate_arrival_rate_month(month).values()):
                first = html.B(month_dict[month])
            else:
                first = html.B(month_dict[month] + ' - Custom')
        else:
            if list(args) == list(generate_arrival_rate_event(event).values()):
                first = html.B(event)
            else:
                first = html.B(event + ' - Custom')
        
        d = dict(zip(range(24),args))
        graph = html.Div(dcc.Graph(config = {'staticPlot': True},figure = generate_simulate_modal_graph(d)),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})
        cp3 = html.Div([
            html.Span('Carpark 3 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp3_red_v * 100 / cp3_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp3_white_v * 100 / cp3_white_max)) + '%'
        ])
        cp3a = html.Div([
            html.Span('Carpark 3A Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp3a_red_v * 100 / cp3a_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp3a_white_v * 100 / cp3a_white_max)) + '%'
        ])
        cp4 = html.Div([
            html.Span('Carpark 4 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp4_red_v * 100 / cp4_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp4_white_v * 100 / cp4_white_max)) + '%'
        ])
        cp5 = html.Div([
            html.Span('Carpark 5 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp5_red_v * 100 / cp5_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp5_white_v * 100 / cp5_white_max)) + '%'
        ])
        cp5b = html.Div([ 
            html.Span('Carpark 5B Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp5b_red_v * 100 / cp5b_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + '100%'          ##bug??
        ])
        cp6b = html.Div([
            html.Span('Carpark 6B Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp6b_red_v * 100 / cp6b_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp6b_white_v * 100 / cp6b_white_max)) + '%'
        ])

        cp10 = html.Div([
            html.Span('Carpark 10 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
            ' ',
            html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
            ' - ' + str(round(cp10_red_v * 100 / cp10_red_max)) + '%, ',
            html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
            ' - ' + str(round(cp10_white_v * 100 / cp10_white_max)) + '%'
        ])


        return [first,
        html.Br(),
        graph, 
        cp3, 
        html.Br(),
        cp3a,
        html.Br(),
        cp4,
        html.Br(),
        cp5,
        html.Br(),
        cp5b,
        html.Br(),
        cp6b,
        html.Br(),
        cp10]


     else:
         return dash.no_update





# Simulation Callbacks
@callback(
    Output(component_id='simulation-contents',component_property='children', allow_duplicate=True),
    Input(component_id='simulate-modal-yes', component_property='n_clicks'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value'),
    Input('slider_red_cp3','value'),
    Input('slider_red_cp3','max'),
    Input('slider_white_cp3','value'),
    Input('slider_white_cp3','max'),
    Input('slider_red_cp3a','value'),
    Input('slider_red_cp3a','max'),
    Input('slider_white_cp3a','value'),
    Input('slider_white_cp3a','max'),
    Input('slider_red_cp4','value'),
    Input('slider_red_cp4','max'),
    Input('slider_white_cp4','value'),
    Input('slider_white_cp4','max'),
    Input('slider_red_cp5','value'),
    Input('slider_red_cp5','max'),
    Input('slider_white_cp5','value'),
    Input('slider_white_cp5','max'),
    Input('slider_red_cp5b','value'),
    Input('slider_red_cp5b','max'),
    Input('slider_white_cp5b','value'),
    Input('slider_white_cp5b','max'),
    Input('slider_red_cp6b','value'),
    Input('slider_red_cp6b','max'),
    Input('slider_white_cp6b','value'),
    Input('slider_white_cp6b','max'),
    Input('slider_red_cp10','value'),
    Input('slider_red_cp10','max'),
    Input('slider_white_cp10','value'),
    Input('slider_white_cp10','max'),
    Input('slider_0','value'),
    Input('slider_1','value'),
    Input('slider_2','value'),
    Input('slider_3','value'),
    Input('slider_4','value'),
    Input('slider_5','value'),
    Input('slider_6','value'),
    Input('slider_7','value'),
    Input('slider_8','value'),
    Input('slider_9','value'),
    Input('slider_10','value'),
    Input('slider_11','value'),
    Input('slider_12','value'),
    Input('slider_13','value'),
    Input('slider_14','value'),
    Input('slider_15','value'),
    Input('slider_16','value'),
    Input('slider_17','value'),
    Input('slider_18','value'),
    Input('slider_19','value'),
    Input('slider_20','value'),
    Input('slider_21','value'),
    Input('slider_22','value'),
    Input('slider_23','value'),
    prevent_initial_call = True
)
def cp_simulation(clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max, cp5b_white_v, cp5b_white_max,
    cp6b_red_v, cp6b_red_max, cp6b_white_v, cp6b_white_max, 
    cp10_red_v, cp10_red_max, cp10_white_v, cp10_white_max,
    *args):
     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
     if 'simulate-modal-yes' in changed_id:
        if event == "No Event" and month is None:
            if list(args) == list(default_arrivals.values()):
                first = html.B("Empty Simulation")
            else:
                first = html.B("Custom")
        elif event == "No Event":
            if list(args) == list(generate_arrival_rate_month(month).values()):
                first = html.B(month_dict[month])
            else:
                first = html.B(month_dict[month] + ' - Custom')
        else:
            if list(args) == list(generate_arrival_rate_event(event).values()):
                first = html.B(event)
            else:
                first = html.B(event + ' - Custom')
        
        d = dict(zip(range(24),args))
        graph = html.Div(dcc.Graph(config = {'staticPlot': True},figure = generate_simulation_graph(d)),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center','margin-bottom':'2%'})

        cp3 = html.B(['Carpark 3 Capacities:',html.Br(), 'Red - ' + str(round(cp3_red_v*100/cp3_red_max)) + '%, White - ' + str(round(cp3_white_v*100/cp3_white_max)) + '%'], style = {'margin-bottom':'1.5%'})
        cp3a = html.B(['Carpark 3A Capacities:',html.Br(), 'Red - ' + str(round(cp3a_red_v*100/cp3a_red_max)) + '%, White - ' + str(round(cp3a_white_v*100/cp3a_white_max)) + '%'], style = {'margin-bottom':'1.5%'})
        cp4 = html.B(['Carpark 4 Capacities:',html.Br(), 'Red - ' + str(round(cp4_red_v*100/cp4_red_max)) + '%, White - ' + str(round(cp4_white_v*100/cp4_white_max)) + '%'], style = {'margin-bottom':'1.5%'})
        cp5 = html.B(['Carpark 5 Capacities:',html.Br(), 'Red - ' + str(round(cp5_red_v*100/cp5_red_max)) + '%, White - ' + str(round(cp5_white_v*100/cp5_white_max)) + '%'], style = {'margin-bottom':'1.5%'})
        cp5b = html.B(['Carpark 5B Capacities:',html.Br(), 'Red - ' + str(round(cp5b_red_v*100/cp5b_red_max)) + '%, White - ' + '100%'], style = {'margin-bottom':'1.5%'})
        cp6b = html.B(['Carpark 6B Capacities:',html.Br(), 'Red - ' + str(round(cp6b_red_v*100/cp6b_red_max)) + '%, White - ' + str(round(cp6b_white_v*100/cp6b_white_max)) + '%'])
        cp10 = html.B(['Carpark 10 Capacities:',html.Br(), 'Red - ' + str(round(cp10_red_v*100/cp10_red_max)) + '%, White - ' + str(round(cp10_white_v*100/cp10_white_max)) + '%'])

        return [first,
        html.Br(),
        graph,
        html.Div([
        cp3, 
        html.Br(),
        cp3a,
        html.Br(),
        cp4,
        html.Br(),
        cp5,
        html.Br(),
        cp5b,
        html.Br(),
        cp6b,
        html.Br(),
        cp10], style = {'font-size':'15px'})]

     else:
         return dash.no_update



@callback(
    Output(component_id = 'loading-modal',component_property='is_open'),
    Input(component_id='simulate-modal-yes', component_property='n_clicks')
)
def open_loading(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'simulate-modal-yes' in changed_id:
        return True
    else:
        return False

# Callback to update contents of cp modals
@callback(
    Output(component_id = 'loading-modal',component_property='is_open',allow_duplicate=True),
    Output(component_id = 'cp3', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp3', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp3',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp3a', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp3a', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp3a',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp4', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp4', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp4',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp5', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp5', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp5',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp5b', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp5b', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp5b',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp6b', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp6b', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp6b',component_property='children', allow_duplicate=True),
    Output(component_id = 'cp10', component_property = 'style',allow_duplicate=True),
    Output(component_id = 'cp10', component_property = 'children',allow_duplicate=True),
    Output(component_id='occupied_cp10',component_property='children', allow_duplicate=True),
    Input(component_id='simulate-modal-yes', component_property='n_clicks'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value'),
    Input('slider_red_cp3','value'),
    Input('slider_red_cp3','max'),
    Input('slider_white_cp3','value'),
    Input('slider_white_cp3','max'),
    Input('slider_red_cp3a','value'),
    Input('slider_red_cp3a','max'),
    Input('slider_white_cp3a','value'),
    Input('slider_white_cp3a','max'),
    Input('slider_red_cp4','value'),
    Input('slider_red_cp4','max'),
    Input('slider_white_cp4','value'),
    Input('slider_white_cp4','max'),
    Input('slider_red_cp5','value'),
    Input('slider_red_cp5','max'),
    Input('slider_white_cp5','value'),
    Input('slider_white_cp5','max'),
    Input('slider_red_cp5b','value'),
    Input('slider_red_cp5b','max'),
    Input('slider_white_cp5b','value'),
    Input('slider_white_cp5b','max'),
    Input('slider_red_cp6b','value'),
    Input('slider_red_cp6b','max'),
    Input('slider_white_cp6b','value'),
    Input('slider_white_cp6b','max'),
    Input('slider_red_cp10','value'),
    Input('slider_red_cp10','max'),
    Input('slider_white_cp10','value'),
    Input('slider_white_cp10','max'),
    Input('slider_0','value'),
    Input('slider_1','value'),
    Input('slider_2','value'),
    Input('slider_3','value'),
    Input('slider_4','value'),
    Input('slider_5','value'),
    Input('slider_6','value'),
    Input('slider_7','value'),
    Input('slider_8','value'),
    Input('slider_9','value'),
    Input('slider_10','value'),
    Input('slider_11','value'),
    Input('slider_12','value'),
    Input('slider_13','value'),
    Input('slider_14','value'),
    Input('slider_15','value'),
    Input('slider_16','value'),
    Input('slider_17','value'),
    Input('slider_18','value'),
    Input('slider_19','value'),
    Input('slider_20','value'),
    Input('slider_21','value'),
    Input('slider_22','value'),
    Input('slider_23','value'),
    prevent_initial_call = True
)
def cp_simulation(clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max, cp5b_white_v, cp5b_white_max,
    cp6b_red_v, cp6b_red_max, cp6b_white_v, cp6b_white_max, 
    cp10_red_v, cp10_red_max, cp10_white_v, cp10_white_max,
    *args):
    lots_d = {'cp3':(cp3_white_v,cp3_red_v),'cp3a':(cp3a_white_v,cp3a_red_v),'cp4':(cp4_white_v,cp4_red_v),'cp5':(cp5_white_v,cp5_red_v), 
    'cp5b':(cp5b_white_v,cp5b_red_v),'cp6b':(cp6b_white_v,cp6b_red_v),'cp10':(cp10_white_v,cp10_red_v)}
    arrival_rates = args
    outputs = simulate_des(arrival_rates,lots_d)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'simulate-modal-yes' in changed_id:
        cp3_outputs = outputs['cp3']
        cp3_ratio = round((cp3_outputs[4]+cp3_outputs[5])*100/(cp3_red_v+cp3_white_v))
        cp3_style = dash.no_update
        
        if cp3_ratio >= 60 and cp3_ratio < 70:
            cp3_style = {'background-color':'orange', 'top':'16%', 'left':'27%'}
        elif cp3_ratio >= 70:
            cp3_style = {'background-color':'red', 'top':'16%', 'left':'27%'}
        else:
            cp3_style = {'background-color':'green', 'top':'16%', 'left':'27%'}

        occupied_cp3 =  html.Div([
            html.B("Occupied Lots: " + str(cp3_outputs[4]+cp3_outputs[5]) + '/' + str(cp3_red_v+cp3_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp3_outputs[5]) + '/' + str(cp3_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp3_outputs[4]) + '/' + str(cp3_white_v), style = {"color" : "white"})])
        
        cp3a_outputs = outputs['cp3a']
        cp3a_ratio = round((cp3a_outputs[4]+cp3a_outputs[5])*100/(cp3a_red_v+cp3a_white_v))
        cp3a_style = dash.no_update
        
        if cp3a_ratio >= 60 and cp3a_ratio < 70:
            cp3a_style = {'background-color':'orange', 'top':'17%', 'left':'32%'}
        elif cp3a_ratio >= 70:
            cp3a_style = {'background-color':'red', 'top':'17%', 'left':'32%'}
        else:
            cp3a_style = {'background-color':'green', 'top':'17%', 'left':'32%'}

        occupied_cp3a =  html.Div([
            html.B("Occupied Lots: " + str(cp3a_outputs[4]+cp3a_outputs[5]) + '/' + str(cp3a_red_v+cp3a_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp3a_outputs[5]) + '/' + str(cp3a_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp3a_outputs[4]) + '/' + str(cp3a_white_v), style = {"color" : "white"})])

        cp4_outputs = outputs['cp4']
        cp4_ratio = round((cp4_outputs[4]+cp4_outputs[5])*100/(cp4_red_v+cp4_white_v))
        cp4_style = dash.no_update
        
        if cp4_ratio >= 60 and cp4_ratio < 70:
            cp4_style = {'background-color':'orange', 'top':'32%', 'left':'34%'}
        elif cp4_ratio >= 70:
            cp4_style = {'background-color':'red', 'top':'32%', 'left':'34%'}
        else:
            cp4_style = {'background-color':'green', 'top':'32%', 'left':'34%'}

        occupied_cp4 =  html.Div([
            html.B("Occupied Lots: " + str(cp4_outputs[4]+cp4_outputs[5]) + '/' + str(cp4_red_v+cp4_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp4_outputs[5]) + '/' + str(cp4_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp4_outputs[4]) + '/' + str(cp4_white_v), style = {"color" : "white"})])

        cp5_outputs = outputs['cp5']
        cp5_ratio = round((cp5_outputs[4]+cp5_outputs[5])*100/(cp5_red_v+cp5_white_v))
        cp5_style = dash.no_update
        
        if cp5_ratio >= 60 and cp5_ratio < 70:
            cp5_style = {'background-color':'orange', 'top':'34%', 'left':'43%'}
        elif cp5_ratio >= 70:
            cp5_style = {'background-color':'red', 'top':'34%', 'left':'43%'}
        else:
            cp5_style = {'background-color':'green', 'top':'34%', 'left':'43%'}

        occupied_cp5 =  html.Div([
            html.B("Occupied Lots: " + str(cp5_outputs[4]+cp5_outputs[5]) + '/' + str(cp5_red_v+cp5_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp5_outputs[5]) + '/' + str(cp5_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp5_outputs[4]) + '/' + str(cp5_white_v), style = {"color" : "white"})])

        cp5b_outputs = outputs['cp5b']
        cp5b_ratio = round((cp5b_outputs[4]+cp5b_outputs[5])*100/(cp5b_red_v+cp5b_white_v))
        cp5b_style = dash.no_update
        
        if cp5b_ratio >= 60 and cp5b_ratio < 70:
            cp5b_style = {'background-color':'orange', 'top':'25.5%', 'left':'42%'}
        elif cp5b_ratio >= 70:
            cp5b_style = {'background-color':'red', 'top':'25.5%', 'left':'42%'}
        else:
            cp5b_style = {'background-color':'green', 'top':'25.5%', 'left':'42%'}

        occupied_cp5b =  html.Div([
            html.B("Occupied Lots: " + str(cp5b_outputs[4]+cp5b_outputs[5]) + '/' + str(cp5b_red_v+cp5b_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp5b_outputs[5]) + '/' + str(cp5b_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp5b_outputs[4]) + '/' + str(cp5b_white_v), style = {"color" : "white"})])

        cp6b_outputs = outputs['cp6b']
        cp6b_ratio = round((cp6b_outputs[4]+cp6b_outputs[5])*100/(cp6b_red_v+cp6b_white_v))
        cp6b_style = dash.no_update
        
        if cp6b_ratio >= 60 and cp6b_ratio < 70:
            cp6b_style = {'background-color':'orange', 'top':'62%', 'left':'62%'}
        elif cp6b_ratio >= 70:
            cp6b_style = {'background-color':'red', 'top':'62%', 'left':'62%'}
        else:
            cp6b_style = {'background-color':'green', 'top':'62%', 'left':'62%'}

        occupied_cp6b =  html.Div([
            html.B("Occupied Lots: " + str(cp6b_outputs[4]+cp6b_outputs[5]) + '/' + str(cp6b_red_v+cp6b_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp6b_outputs[5]) + '/' + str(cp6b_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp6b_outputs[4]) + '/' + str(cp6b_white_v), style = {"color" : "white"})])

        cp10_outputs = outputs['cp10']
        cp10_ratio = round((cp10_outputs[4]+cp10_outputs[5])*100/(cp10_red_v+cp10_white_v))
        cp10_style = dash.no_update
        
        if cp10_ratio >= 60 and cp10_ratio < 70:
            cp10_style = {'background-color':'orange', 'top':'53%', 'left':'84%'}
        elif cp10_ratio >= 70:
            cp10_style = {'background-color':'red', 'top':'53%', 'left':'84%'}
        else:
            cp10_style = {'background-color':'green', 'top':'53%', 'left':'84%'}

        occupied_cp10 =  html.Div([
            html.B("Occupied Lots: " + str(cp10_outputs[4]+cp10_outputs[5]) + '/' + str(cp10_red_v+cp10_white_v), style = {"color" : "white"}),
            html.Div("Occupied Red Lots: " + str(cp10_outputs[5]) + '/' + str(cp10_red_v), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp10_outputs[4]) + '/' + str(cp10_white_v), style = {"color" : "white"})])

        time.sleep(10)
        return False,cp3_style,cp3_ratio,occupied_cp3,cp3a_style,cp3a_ratio,occupied_cp3a,cp4_style,cp4_ratio,occupied_cp4,cp5_style,cp5_ratio,occupied_cp5,cp5b_style,cp5b_ratio,occupied_cp5b,cp6b_style,cp6b_ratio,occupied_cp6b, cp10_style,cp10_ratio,occupied_cp10
    
    else:
        return dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update