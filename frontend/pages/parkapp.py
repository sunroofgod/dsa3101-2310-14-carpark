import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import random
import time
import io
from dash_extensions.enrich import FileSystemCache, Trigger

import os
path = os.getcwd()

import sys
sys.path.append(path + r'\backend\des')

from params import get_month_arrival_rate, get_day_arrival_rate
from DES import run_nsim, stats_mean

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
sample_results = {'cp3': [467, 44, 239, 75, 34, 16], 'cp3a': [309, 157, 229, 75, 45, 13], 'cp4': [331, 124, 167, 125, 39, 14], 'cp5': [422, 179, 58, 25, 35, 13], 'cp5b': [165, 60, 165, 126, 0, 16], 'cp6b': [422, 194, 245, 50, 38, 13], 'cp10': [335, 53, 229, 25, 39, 18]}
results_body = []

count = 0

fsc = FileSystemCache("cache_dir")
fsc.set("progress", 0)

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
    d = {}
    for key in lots_d.keys():
        if key != 'cp5b':
            d[key] = [random.randint(50, 500), random.randint(20, 250), random.randint(50, 250),random.randint(20, 125), random.randint(30,50), random.randint(10,20)]
        else:
            d[key] = [165, random.randint(20, 250), 165,random.randint(20, 150), 0, random.randint(10,20)]

    return d


#Helper function to generate plots from dictionary representation
def generate_arrival_rate_graph(d,w,h): #w is width, h is height
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates to Simulate</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width=w, height=h)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(rangemode='nonnegative')
    return fig

def generate_simulation_graph(d): #w is width, h is height
    df = pd.DataFrame({'hour':d.keys(),'arrivals':d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width = 300 , height = 300)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(rangemode='nonnegative')
    return fig

def vert_slider(hour, val):
    return dbc.Col([html.Div(html.Div(str(val), id = "value_" + str(hour)), style= {'font-size':'16px','text-align':'center', 'margin-right':'50%'}),
                    html.Div(dcc.Slider(id = "slider_" + str(hour),min = 0, max = 500, step = 1, value = val, vertical = True,marks = None), style={'padding':'0px','margin-left':'10%'}), 
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
    if cp != "cp5b":
        return dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(cp.upper() + ": " + cp_names[cp], style = {"color" : "white"}), close_button= False, style = {"background-color": "#003d7c"}),
            dbc.ModalBody([
                html.Div([
                html.B("Occupied Lots: " + str(a+c) + '/' + str(b+d), style = {"color" : "black"}),
                html.Div("Occupied Red Lots: " + str(a) + '/' + str(b), style = {'color':'red'}),
                html.Div("Occupied White Lots: " + str(c) + '/' + str(d), style = {"color" : "black"})], id = 'occupied_'+cp),
                html.Br(),
                html.H4('Simulation Parameters:', style = {"color" : "black"}),
                html.B('Carpark Status:', style = {"color" : "black"}),
                html.Div(dcc.Dropdown(options=['Open','Closed'], id = 'cp_status_'+cp, value = "Open", clearable = False), style={'margin-bottom':'3%'}),
                html.Div([
                html.Div(html.B('Adjust Red Lot Capacity:'),style= {'text-align':'center', 'color' : 'red'}),
                html.Div(dcc.Slider(id = "slider_red_"+cp,min = 0, max = b, step = 1, value = b, marks = None)),
                html.Div(html.B('Adjust White Lot Capacity:'),style= {'text-align':'center', 'color' : 'black'}),
                html.Div(dcc.Slider(id = "slider_white_"+cp,min = 0, max = d, step = 1, value = d, marks = None)),
                html.Div(
                    [html.B("Red Lot Capacity to Simulate: " + str(b) + " (100% Capacity)",id = 'to_simulate_red_'+cp, style = {'font-size':'15px', 'color':'red'}),
                    html.Br(),
                    html.B("White Lot Capacity to Simulate: " + str(d) + " (100% Capacity)",id = 'to_simulate_white_'+cp, style = {'font-size':'15px', "color" : "white"})]
                )
                ])

            ], style= {'text-align':'center', 'font-size':'19px', "background-color": "white"}),
            dbc.ModalFooter([
                        dbc.Button('Reset Parameters', id = 'reset-modal-'+cp,style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
                        dbc.Button(
                            "Save and Exit", id="close-modal", style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}
                        )]
                        , style = {"background-color" : "#003d7c"})
        ], id = 'modal-'+cp, is_open= False, backdrop = False, centered = True)
    
    else:
        return dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(cp.upper() + ": " + cp_names[cp], style = {"color" : "white"}), close_button= False, style = {"background-color": "#003d7c"}),
            dbc.ModalBody([
                html.Div([
                html.B("Occupied Lots: " + str(a+c) + '/' + str(b+d), style = {"color" : "black"}),
                html.Div("Occupied Red Lots: " + str(a) + '/' + str(b), style = {'color':'red'}),], id = 'occupied_'+cp),
                html.Br(),
                html.H4('Simulation Parameters:', style = {"color" : "black"}),
                html.B('Carpark Status:', style = {"color" : "black"}),
                html.Div(dcc.Dropdown(options=['Open','Closed'], id = 'cp_status_'+cp, value = "Open", clearable = False), style={'margin-bottom':'3%'}),
                html.Div([
                html.Div(html.B('Adjust Red Lot Capacity:'),style= {'text-align':'center', 'color' : 'red'}),
                html.Div(dcc.Slider(id = "slider_red_"+cp,min = 0, max = b, step = 1, value = b, marks = None)),
                #html.Div(html.Div('Adjust White Lot Capacity:'),style= {'text-align':'center', 'color' : 'black'}),
                #html.Div(dcc.Slider(id = "slider_white_"+cp,min = 0, max = d, step = 1, value = d, marks = None)),
                html.Div(
                    [html.B("Red Lot Capacity to Simulate: " + str(b) + " (100% Capacity)",id = 'to_simulate_red_'+cp, style = {'font-size':'15px', 'color':'red'}),
                    html.Br(),
                    ]
                )
                ])

            ], style= {'text-align':'center', 'font-size':'19px', "background-color": "white"}),
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
         dbc.ModalHeader(dbc.ModalTitle('Initializing Simulation:'), close_button= False, style={'border':'navy 3px solid', 'font-family' : 'Open Sans', 'font-size':'20px','font-weight' : 'bold', 'background-color':'navy','color' : 'white'}),
         dbc.ModalBody(id = 'simulate-modal-contents', style = {'text-align':'center', 'font-size':'15px', 'border': ' black 3px solid'}),
         dbc.ModalFooter(children = [
            html.H5("Confirm Simulation?", style = {'color':'white'}),
            dbc.Button('Yes', id = 'simulate-modal-yes' ,style = {'background-color':'#06a11b', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
            dbc.Button('No', id = 'simulate-modal-no' ,style = {'background-color':'red', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
         ], style ={'border': 'navy 3px solid','background-color':'navy'})
    ], id = 'simulate-modal', is_open = False, backdrop = False, centered = True)


# Helper function to create results modal, input is results dict
def generate_results_modal(results):
    if results == {}:
        body = dbc.ModalBody(html.H4('No Simulations have been run'), id = 'results-modal-contents', style = {'text-align':'center'})
    else:
        # Creating results data frame
        carparks = list(results.keys())
        white_entered = list([result[0][-1] for result in results.values()])
        red_entered = list([result[1][-1] for result in results.values()])
        white_rej = list([result[2][-1] for result in results.values()])
        red_rej = list([result[3][-1] for result in results.values()])
        df = pd.DataFrame({'carpark':carparks, 'white_entered':white_entered, 'red_entered':red_entered, 'white_rej':white_rej, 'red_rej':red_rej}).sort_values('carpark')
        df['order'] = [6,0,1,2,3,4,5]
        df.sort_values('order',inplace = True)
        
        print(df)

        df['total_entered'] = df["red_entered"] + df["white_entered"]
        df['total_rej'] = df["red_rej"] + df["white_rej"]
        df['white_rej_percent'] = (df['white_rej'] / df['white_entered']).fillna(0) * 100
        df['red_rej_percent'] = (df['red_rej'] / df['red_entered']).fillna(0) * 100
        df['total_rej_percent'] = (df['total_rej'] / df['total_entered']).fillna(0) * 100

        # Enter Graph
        fig1 = px.bar(df, x = 'carpark', y = ['white_entered','red_entered','total_entered'],
        title = 'Total Cars Entered by Carpark', barmode = 'group', labels = {'value':'Number Entries','variable':'Entry Type'})
        fig1.update_traces(name='White', selector=dict(name='white_entered'))
        fig1.update_traces(name='Red', selector=dict(name='red_entered'))
        fig1.update_traces(name='Total', selector=dict(name='total_entered'))
        fig1.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig1.update_yaxes(rangemode='nonnegative')
        fig1.update_layout(xaxis_title="Carpark")

        # Reject Graph
        fig2 = px.bar(df, x = 'carpark', y = ['white_rej','red_rej','total_rej'],
        title = 'Total Cars Rejected by Carpark', barmode = 'group', labels = {'value':'Number Rejected','variable':'Entry Type'})
        fig2.update_traces(name='White', selector=dict(name='white_rej'))
        fig2.update_traces(name='Red', selector=dict(name='red_rej'))
        fig2.update_traces(name='Total', selector=dict(name='total_rej'))
        fig2.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig2.update_yaxes(rangemode='nonnegative')
        fig2.update_layout(xaxis_title="Carpark")

        fig3 = px.bar(df, x = 'carpark', y = ['white_rej_percent','red_rej_percent','total_rej_percent'],
        title = 'Percent Cars Rejected by Carpark', barmode = 'group', labels = {'value':'Percent Rejected (%)','variable':'Entry Type'})
        fig3.update_traces(name='White', selector=dict(name='white_rej_percent'))
        fig3.update_traces(name='Red', selector=dict(name='red_rej_percent'))
        fig3.update_traces(name='Total', selector=dict(name='total_rej_percent'))
        fig3.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig3.update_yaxes(rangemode='nonnegative')
        fig3.update_layout(xaxis_title="Carpark")

        
        current_graphs = dbc.Col(
            [dbc.Row(dcc.Graph(figure = fig1)),
            dbc.Row(dcc.Graph(figure = fig2)),
            dbc.Row(dcc.Graph(figure = fig3))],
            )
        
        global results_body
        results_body.append(current_graphs)

        if len(results_body) > 2:
            results_body.pop(0)

        if len(results_body) == 1:
            header = dbc.Row(dbc.Col(html.H4("Current Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'}))
        else:
            header = dbc.Row([dbc.Col(html.H4("Previous Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'}),
            dbc.Col(html.H4("Current Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'})])

        body = dbc.ModalBody(
            [
                header,
                dbc.Row(results_body) 
            ], style = {'border':'black 3px solid'}
        )

        #body = dbc.ModalBody('No Simulations have been run', id = 'results-modal-contents', style = {'text-align':'center', 'font-size':'15px'})

    return dbc.Modal([
         dbc.ModalHeader(dbc.ModalTitle('Simulation Results:'), close_button= False, style = {'border': 'navy 3px solid', 'background-color':'navy','color' : 'white'}),
         body,
         dbc.ModalFooter([
            dbc.Button('Download Current Statistics', id = 'results-download-button', disabled = True, style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}),
            dbc.Button('Close', id = 'results-modal-close' ,style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}),
         ], style = {'border': 'navy', 'background-color':'navy','color' : 'white', 'border':'navy 3px solid'})
    ], id = 'results-modal', is_open = False, backdrop = False, centered = True, size = 'xl')



# layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col( # Left partition
            html.Div([
                html.H4("Currently Simulating:", style={'font-weight':'bold'}),
                html.Div("None",id = "simulation-contents"),
                html.Br(),
                html.Div('Unavailable, run simulations first', id = 'hour-slider-show'),
                dcc.Slider(min = 0, max = 23, step = 1,  value = 23, id = 'results-slider', disabled = True, marks = None),
                html.Br(),
                dbc.Button('View Simulation Results', id='results-button', style={'display':'inline-block', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'15px', 'font-weight': 'bold'})
            ]
            ),
            width={'size': 2, 'order': 1},
            style = {'text-align':'center','background-color':'#003d7c','padding-top':'1%','color':'#FFFFFF', 'align-items': 'center'}
            ),
        dbc.Col( # Center partition
            html.Div([
            html.Div(html.Img(src=dash.get_asset_url('nus_map.png'), style={'width': '100%', 'height': 'auto'}), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),

            html.Div([
                html.Div([
                    html.H3('Occupancy Rate Legend:', style={'color': '#003D7C', 'font-weight':'bold'}),
                    html.Div("● - Green: 0-60%", style={'color': 'green', 'font-size': '1em'}),
                    html.Div("● - Orange: 60-70%", style={'color': 'orange', 'font-size': '1em'}),
                    html.Div("● - Red: 70-100%", style={'color': 'red', 'font-size': '1em'}),
                    html.Br(),
                    html.Div("*Click on the circles on the map to adjust carpark parameters and view occupancy*", style = {'color':'#003D7C', 'font-weight':'bold', 'font-style':'italic','font-size':'0.6em'})
                ])
            ], style = {'border' : '2px solid black', 'padding-left':'5px', 'border-radius':'5px', 'margin':'3px', 'align-text':'center', 'background-color':'#f3f3f3',
                        'position':'absolute', 'top':'4%', 'left':'75%'}),

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
            dbc.Button('Reset Events and Months', id='reset-events-button', style={'display':'inline-block', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
            html.Br(),
            html.Div(dcc.Graph(id = "arrival-graph",config = {'staticPlot': True},figure = generate_arrival_rate_graph(default_arrivals,300,300)), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'width': '100%'}),
            html.Br(),
            dbc.Button('Refine Arrival Rate', id='refine-button', style={'margin-bottom':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
            dbc.Button('Reset CP Params', id='reset-cp-button', style={'display':'inline-block','margin-bottom':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),            
            dbc.Button('Reset All', id='reset-button', style={'margin-bottom':'2%','display':'inline-block','margin-right':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            dbc.Button('Simulate', id='simulate-button', style={'margin-bottom':'2%','display':'inline-block', 'background-color':'#000000', 'color' : '#FFFFFF' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            html.Br(),
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
            html.Div(generate_results_modal({}), id = 'results-div'),
            html.Div(dcc.Download(id="download-results")),
            html.Div(dbc.Modal([
                dbc.ModalBody([
                html.B("Simulation in Progress! Please wait...     ", style={'font-family' : 'Open Sans', 'font-size':'20px', 'color' : 'white', 
                                                                        'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height':'100%'}), 
                html.Br(),
                html.Div([dbc.Progress(value = 0, id = 'progress-bar', color = 'success', label = '🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗'),dcc.Interval(id="interval", interval=500)]),
                html.Br(),
                html.Div(dbc.Spinner(color="white", type="border"), style = {'float':'right'})
                ] , style = {'border':'navy 3px solid', 'background-color' : 'navy'}), #change this line after deciding color another day
                ],id="loading-modal",is_open=False,backdrop = False,centered = True
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
    #Output('slider_white_cp5b','disabled'),
    Input('cp_status_cp5b','value')
)
def show_cp_params(status):
    if status == "Open":
        return False
    else:
        return True
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp5b','children'),
    #Output('to_simulate_white_cp5b','children'),
    Input('cp_status_cp5b','value'),
    Input('slider_red_cp5b','value'),
    #Input('slider_white_cp5b','value'),
    State('slider_red_cp5b', 'max'),
    #State('slider_white_cp5b', 'max'),
)
def params_to_simulate(status,red,red_max):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/red_max)) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp5b','value'),
    #Output('slider_white_cp5b','value'),
    Output('cp_status_cp5b','value'),
    Input('reset-modal-cp5b','n_clicks'),
    State('slider_red_cp5b','max'),
    #State('slider_white_cp5b','max')
)
def reset_cp_params(clicks,max_red):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp5b' in changed_id:
        return max_red, "Open"
    else:
        return dash.no_update,dash.no_update



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
        return refine_modal("No Event (Custom Arrivals)", default_arrivals),generate_arrival_rate_graph(default_arrivals,300,300)
    elif month is not None and event == "No Event":
        d = generate_arrival_rate_month(month)
        return refine_modal(month_dict[month], d),generate_arrival_rate_graph(d,300,300)
    else:
        d = generate_arrival_rate_event(event)
        return refine_modal(event, d),generate_arrival_rate_graph(d,300,300) 

    
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
    return generate_arrival_rate_graph(d,300,300), *args

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
            return [vert_slider(i, default_arrivals[i]) for i in range(24)],generate_arrival_rate_graph(default_arrivals,300,300)
        elif month is not None and event == "No Event":
            d = generate_arrival_rate_month(month)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_rate_graph(d,300,300)
        else:
            d = generate_arrival_rate_event(event)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_rate_graph(d,300,300)
    else:
        return dash.no_update, dash.no_update

# Callback for reset all: revert to original settings and carpark state
@callback(
    Output(component_id = 'results-slider', component_property = 'disabled'),
    Output(component_id = 'results-slider', component_property = 'value'),
    Output(component_id = 'results-div', component_property = 'children'),
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
        results_body.clear()
        return True, 23, generate_results_modal({}),{'top':'16%', 'left':'27%','background-color':'green'},{'top':'17%', 'left':'32%','background-color':'green'}, {'top':'32%', 'left':'34%','background-color':'green'},{'top':'34%', 'left':'43%','background-color':'green'},{'top':'25.5%', 'left':'42%','background-color':'green'},{'top':'62%', 'left':'62%','background-color':'green'},{'top':'53%', 'left':'84%','background-color':'green'},True,cp_modal("cp3",0,31,0,212),cp_modal("cp3a",0,14,0,53),cp_modal("cp4",0,21,0,95), cp_modal("cp5",0,17,0,53),cp_modal("cp5b",0,32,0,0),cp_modal("cp6b",0,130,0,43),cp_modal("cp10",0,211,0,164),'None',generate_arrival_rate_graph(default_arrivals,300,300),default_button,default_button,default_button,default_button,default_button,default_button,default_button,None,"No Event"
    else:
        return dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,dash.no_update,True,dash.no_update,dash.no_update,dash.no_update,dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


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
        return True,generate_arrival_rate_graph(default_arrivals,300,300),None,"No Event"
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
    Input('cp_status_cp3','value'),
    Input('cp_status_cp3a','value'),
    Input('cp_status_cp4','value'),
    Input('cp_status_cp5','value'),
    Input('cp_status_cp5b','value'),
    Input('cp_status_cp6b','value'),
    Input('cp_status_cp10','value'),
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
    #Input('slider_white_cp5b','value'),
    #Input('slider_white_cp5b','max'),
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

def cp_simulation_modal(cp3_status,cp3a_status,cp4_status,cp5_status,cp5b_status,cp6b_status,cp10_status,clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max, 
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
        graph = html.Div(dcc.Graph(config = {'staticPlot': True},figure = generate_arrival_rate_graph(d,300,300)), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})

        cp3_red_string = "0"
        cp3_white_string = "0"
        if cp3_status == "Open":
            cp3_red_string = str(round(cp3_red_v * 100 / cp3_red_max))
            cp3_white_string = str(round(cp3_white_v * 100 / cp3_white_max))

        # cp3 = html.Div([
        #     html.Span('Carpark 3 Capacities:  ', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp3_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp3_white_string + '%'
        # ])

        cp3a_red_string = "0"
        cp3a_white_string = "0"
        if cp3a_status == "Open":
            cp3a_red_string = str(round(cp3a_red_v * 100 / cp3a_red_max))
            cp3a_white_string = str(round(cp3a_white_v * 100 / cp3a_white_max))

        # cp3a = html.Div([
        #     html.Span('Carpark 3A Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp3a_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp3a_white_string + '%'
        # ], style={'text-align':'center','position': 'relative','left': '1%'})

        cp4_red_string = "0"
        cp4_white_string = "0"
        if cp4_status == "Open":
            cp4_red_string = str(round(cp4_red_v * 100 / cp4_red_max))
            cp4_white_string = str(round(cp4_white_v * 100 / cp4_white_max))

        # cp4 = html.Div([
        #     html.Span('Carpark 4 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp4_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp4_white_string + '%'
        # ])

        cp5_red_string = "0"
        cp5_white_string = "0"
        if cp5_status == "Open":
            cp5_red_string = str(round(cp5_red_v * 100 / cp5_red_max))
            cp5_white_string = str(round(cp5_white_v * 100 / cp5_white_max))


        # cp5 = html.Div([
        #     html.Span('Carpark 5 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp5_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp5_white_string + '%'
        # ])

        cp5b_red_string = "0"
        if cp5b_status == "Open":
            cp5b_red_string = str(round(cp5b_red_v * 100 / cp5b_red_max))


        # cp5b = html.Div([ 
        #     html.Span('Carpark 5B Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp5b_red_string + '%',
        #     #html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     #' - ' + '100%'          ##bug??
        # ], style={'text-align':'center','position': 'relative','right': '10%'})

        cp6b_red_string = "0"
        cp6b_white_string = "0"
        if cp6b_status == "Open":
            cp6b_red_string = str(round(cp6b_red_v * 100 / cp6b_red_max))
            cp6b_white_string = str(round(cp6b_white_v * 100 / cp6b_white_max))


        # cp6b = html.Div([
        #     html.Span('Carpark 6B Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold'}),
        #     ' - ' + cp6b_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp6b_white_string + '%'
        # ], style={'text-align':'center','position': 'relative','left': '1%'})

        cp10_red_string = "0"
        cp10_white_string = "0"
        if cp10_status == "Open":
            cp10_red_string = str(round(cp10_red_v * 100 / cp10_red_max))
            cp10_white_string = str(round(cp10_white_v * 100 / cp10_white_max))

        # cp10 = html.Div([
        #     html.Span('Carpark 10 Capacities:', style={'background-color': '#003D7C', 'padding': '2px 4px', 'border-radius': '4px', 'color': 'white'}),
        #     ' ',
        #     html.Span('Red', style={'color': 'red', 'font-weight': 'bold', 'margin-right': '1%'}),
        #     ' - ' + cp10_red_string + '%, ',
        #     html.Span('White', style={'color': 'green', 'font-weight': 'bold'}),
        #     ' - ' + cp10_white_string + '%'
        # ], style={'text-align':'center','position': 'relative','left': '1%'})
        
        data = {
            'Carparks':['Carpark 3','Carpark 3A','Carpark 4','Carpark 5','Carpark 5B','Carpark 6B','Carpark 10'],
            'Red Lot Capacity' : [cp3_red_string + "%", cp3a_red_string + "%", cp4_red_string + "%", cp5_red_string + "%", cp5b_red_string + "%", cp6b_red_string + "%", cp10_red_string + "%"], 
            'White Lot Capacity' : [cp3_white_string + "%", cp3a_white_string + "%", cp4_white_string + "%", cp5_white_string + "%", "No White Lots", cp6b_white_string + "%", cp10_white_string + "%"]
            }
        df = pd.DataFrame(data)

        table = dash_table.DataTable(
            columns = [{"name":'Carparks', "id":'Carparks'},{"name":'Red Lot Capacity', "id":'Red Lot Capacity'},{"name":'White Lot Capacity', "id":'White Lot Capacity'}],
            data=df.to_dict('records'),
            editable = False,
            #sort_action = 'native',
            #sort_mode="multi",
            style_header = {'background-color':'navy', 'color':'white', 'font-weght':'bold', 'font-size':'20px'},
            style_cell = {'textAlign': 'center', 'font-family':'Open Sans', 'border':'3px solid black'},
            style_data_conditional = [
                {
                    'if': {'row_index': 4, 'column_id': 'White Lot Capacity'},
                    'color': 'white',
                    'backgroundColor': 'black',
                    'fontWeight': 'bold'
                    }
            ],  
        )

        layout = html.Div(
            children = [first,
                html.Br(),
                graph, 
                html.Br(),
                table], 
                style={'font-family':'Open Sans', 'align-items':'center', 'justify-content':'center', 'text-align':'center', 'width':'100%'})
        
        return layout

     else:
         return dash.no_update





# Simulation Callbacks
@callback(
    #Output('results-slider','value',allow_duplicate=True),
    Output(component_id='simulation-contents',component_property='children', allow_duplicate=True),
    Input('cp_status_cp3','value'),
    Input('cp_status_cp3a','value'),
    Input('cp_status_cp4','value'),
    Input('cp_status_cp5','value'),
    Input('cp_status_cp5b','value'),
    Input('cp_status_cp6b','value'),
    Input('cp_status_cp10','value'),
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
    #Input('slider_white_cp5b','value'),
    #Input('slider_white_cp5b','max'),
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

def cp_simulation_side(cp3_status,cp3a_status,cp4_status,cp5_status,cp5b_status,cp6b_status,cp10_status,clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max,
    cp6b_red_v, cp6b_red_max, cp6b_white_v, cp6b_white_max, 
    cp10_red_v, cp10_red_max, cp10_white_v, cp10_white_max,
    *args):
     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
     if 'simulate-modal-yes' in changed_id:
        cp3_status,cp3a_status,cp4_status,cp5_status,cp5b_status,cp6b_status
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
        

        graph = html.Div(dcc.Graph(config = {'staticPlot': True}, figure = generate_simulation_graph(d)),
                        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}) 
            
        cp3_red_string = "0"
        cp3_white_string = "0"
        cp3a_red_string = "0"
        cp3a_white_string = "0"
        cp4_red_string = "0"
        cp4_white_string = "0" 
        cp5_red_string = "0"
        cp5_white_string = "0"  
        cp5b_red_string = "0"
        cp6b_red_string = "0"
        cp6b_white_string = "0" 
        cp10_red_string = "0"
        cp10_white_string = "0"

        if cp3_status == "Open":
            cp3_red_string = str(round(cp3_red_v * 100 / cp3_red_max)) 
            cp3_white_string = str(round(cp3_white_v * 100 / cp3_white_max)) 

        if cp3a_status == "Open":
            cp3a_red_string = str(round(cp3a_red_v * 100 / cp3a_red_max)) 
            cp3a_white_string = str(round(cp3a_white_v * 100 / cp3a_white_max)) 
    
        if cp4_status == "Open":
            cp4_red_string = str(round(cp4_red_v * 100 / cp4_red_max)) 
            cp4_white_string = str(round(cp4_white_v * 100 / cp4_white_max)) 

        if cp5_status == "Open":
            cp5_red_string = str(round(cp5_red_v * 100 / cp5_red_max)) 
            cp5_white_string = str(round(cp5_white_v * 100 / cp5_white_max))

        if cp5b_status == "Open":
            cp5b_red_string = str(round(cp5b_red_v * 100 / cp5b_red_max))
        
        if cp6b_status == "Open":
            cp6b_red_string = str(round(cp6b_red_v * 100 / cp6b_red_max))
            cp6b_white_string = str(round(cp6b_white_v * 100 / cp6b_white_max))
        
        if cp10_status == "Open":
            cp10_red_string = str(round(cp10_red_v * 100 / cp10_red_max))
            cp10_white_string = str(round(cp10_white_v * 100 / cp10_white_max))

        data = {
            'Carparks':['Carpark 3','Carpark 3A','Carpark 4','Carpark 5','Carpark 5B','Carpark 6B','Carpark 10'],
            'Red Lot Capacity' : [cp3_red_string + "%", cp3a_red_string + "%", cp4_red_string + "%", cp5_red_string + "%", cp5b_red_string + "%", cp6b_red_string + "%", cp10_red_string + "%"], 
            'White Lot Capacity' : [cp3_white_string + "%", cp3a_white_string + "%", cp4_white_string + "%", cp5_white_string + "%", "No White Lots", cp6b_white_string + "%", cp10_white_string + "%"]
            }
        
        df = pd.DataFrame(data)

        table = dash_table.DataTable(
            columns = [{"name":'Carparks', "id":'Carparks'},{"name":'Red Lot', "id":'Red Lot Capacity'},{"name":'White Lot', "id":'White Lot Capacity'}],
            data=df.to_dict('records'),
            editable = False,
            #sort_action = 'native',
            #sort_mode="multi",
            style_cell = {'textAlign': 'center', 'font-family':'Open Sans', 'border':'3px solid black', 'color':'black', 'back-ground-color':'white', 'font-size':'14px'},
            style_header = {'background-color':'grey', 'color':'white', 'font-weght':'bold', 'font-size':'18px'},
            style_data_conditional=[
                {
                    'if': {'row_index': 4 , 'column_id': 'White Lot Capacity'},
                    'color':'white',
                    'backgroundColor': 'black',
                    'fontWeight': 'bold'
                }
            ]
        )

        layout = html.Div(
            children = [first,
                html.Br(),
                graph,
                html.Br(),
                table])
        
        return layout    

     else:
         return dash.no_update
     
@callback(
    Output(component_id = 'hour-slider-show', component_property = 'children'),
    Input(component_id = 'results-slider', component_property = 'value'),
    Input(component_id = 'results-slider',component_property = 'disabled')
)
def show_hour(hour,disabled):
    if disabled or hour is None:
        return ["Unavailable, run simulation first"]
    else:
        hour_dict = {0:'12 am', 1: '1 am', 2: '2 am', 3: '3 am', 4: '4 am', 5: '5 am', 6: '6 am', 7: '7 am', 8: '8 am', 9: '9 am', 10: '10 am', 11: '11 am', 12: '12 pm',
        13: '1 pm', 14: '2 pm', 15: '3 pm', 16: '4 pm', 17: '5 pm', 18: '6 pm', 19: '7 pm', 20: '8 pm', 21: '9 pm', 22: '10 pm', 23: '11 pm'}
        return ["Displaying carpark occupancies at " + hour_dict[hour]]



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
    Output('results-slider','disabled',allow_duplicate = True),
    Output(component_id = 'results-div',component_property = 'children', allow_duplicate=True),
    Output(component_id = 'loading-modal',component_property='is_open',allow_duplicate=True),
    Input('results-slider','value'),
    Input('cp_status_cp3','value'),
    Input('cp_status_cp3a','value'),
    Input('cp_status_cp4','value'),
    Input('cp_status_cp5','value'),
    Input('cp_status_cp5b','value'),
    Input('cp_status_cp6b','value'),
    Input('cp_status_cp10','value'),
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
def cp_simulation_model(hour,cp3_status,cp3a_status,cp4_status,cp5_status,cp5b_status,cp6b_status,cp10_status,clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
    cp3a_red_v, cp3a_red_max, cp3a_white_v, cp3a_white_max,
    cp4_red_v, cp4_red_max, cp4_white_v, cp4_white_max,
    cp5_red_v, cp5_red_max, cp5_white_v, cp5_white_max,
    cp5b_red_v, cp5b_red_max, 
    cp6b_red_v, cp6b_red_max, cp6b_white_v, cp6b_white_max, 
    cp10_red_v, cp10_red_max, cp10_white_v, cp10_white_max,
    *args):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'simulate-modal-yes' in changed_id:
        global lots_d
        lots_d = {'cp3':(cp3_white_v,cp3_red_v),'cp3a':(cp3a_white_v,cp3a_red_v),'cp4':(cp4_white_v,cp4_red_v),'cp5':(cp5_white_v,cp5_red_v), 
        'cp5b':(0,cp5b_red_v),'cp6b':(cp6b_white_v,cp6b_red_v),
        'cp10':(cp10_white_v,cp10_red_v)
        }

        lots_d_input = lots_d.copy()
        #del lots_d_input['cp10']

        list_carparks = list(lots_d.keys())

        status_d = {'cp3':cp3_status, 'cp3a':cp3a_status, 'cp4':cp4_status,'cp5':cp5_status,'cp5b':cp5b_status,'cp6b':cp6b_status, 'cp10':cp10_status}

        keys_to_remove = []

        for key, value in status_d.items():
            if value == "Closed":
                lots_d[key] = (0,0)

        for key, value in lots_d.items():
            if value == (0,0):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del lots_d_input[key]
        
        global non_empty_cps
        non_empty_cps = list(lots_d_input.keys())

        arrival_rates = args
        
        #print(run_nsim(cap_dict = lots_d_input, lambdas = arrival_rates, n = 1))

        init_time = time.time()

        #outputs = simulate_des(arrival_rates,lots_d_input)
        global outputs
        outputs = {}
        n = 10
        for i in range(n):
            current = run_nsim(cap_dict = lots_d_input, lambdas = arrival_rates, n = 1) #adjust n for number of simulations, remove n after done
            outputs = stats_mean(outputs, current)
            global fsc
            fsc.set('progress',(i+1)*100/n)

        for key in list_carparks:
            if key not in outputs.keys():
                outputs[key] = [[0 for i in range(24)] for j in range(6)]

        
        ## Round off overall output
        for cp, val_list in outputs.items():
            for i in range(len(val_list)):
                outputs[cp][i] = [int(val) for val in val_list[i]]
        
        duration = (time.time() - init_time) / 60 # convert to minutes
        print(f"--- Total running time {duration:.2f} minutes ---")

        
        #print("Arrival rates", arrival_rates)
        #print("CP capacity:", lots_d)
        #print("Model Inputs:",lots_d_input)
        print("Statistics:",outputs)
        print()

        global results_dict
        results_dict = {}
        for key, value in outputs.items():
            white_info = value[4]
            red_info = value[5]
            results_dict[key] = [white_info, red_info]
        
        time.sleep(2)
        return False,generate_results_modal(outputs),False
    
    else:
        return dash.no_update,dash.no_update,dash.no_update

'''
Results Modal
'''
#Toggling results modal
# Toggle Simulation Confirmation Modal
@callback(
    Output('results-modal','is_open'),
    Input('results-button','n_clicks'),
    Input('results-modal-close','n_clicks')
)
def open_simulation_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'results-button' in changed_id:
        return True
    else:
        return False

# Callback to get carpark saturation for each hour
@callback(
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
    Input('results-slider','disabled'),
    Input('results-slider','value'),
    prevent_initial_call = True
)
def change_saturation(disabled,hour):
    if disabled == False:
        outputs = results_dict
        cp3_outputs = outputs['cp3']
        cp3_ratio = 0
        if lots_d['cp3'][1]+lots_d['cp3'][0] != 0:
            cp3_ratio = round((cp3_outputs[0][hour]+cp3_outputs[1][hour])*100/(lots_d['cp3'][1]+lots_d['cp3'][0]))

        cp3_style = dash.no_update
        
        if 'cp3' not in non_empty_cps:
            cp3_ratio = "-"
            cp3_style = {'background-color':'gray', 'top':'16%', 'left':'27%'}
        elif cp3_ratio >= 60 and cp3_ratio < 70:
            cp3_style = {'background-color':'orange', 'top':'16%', 'left':'27%'}
        elif cp3_ratio >= 70:
            cp3_style = {'background-color':'red', 'top':'16%', 'left':'27%'}
        else:
            cp3_style = {'background-color':'green', 'top':'16%', 'left':'27%'}

        cp3_ratio_string = "-"
        if 'cp3' in non_empty_cps:
            cp3_ratio_string = str(cp3_outputs[0][hour]+cp3_outputs[1][hour]) + "/" + str(lots_d['cp3'][1]+lots_d['cp3'][0])

        occupied_cp3 =  html.Div([
            html.B("Occupied Lots: " + str(cp3_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp3_outputs[1][hour]) + '/' + str(lots_d['cp3'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp3_outputs[0][hour]) + '/' + str(lots_d['cp3'][0]), style = {"color" : "black"})])
        
        cp3a_outputs = outputs['cp3a']
        cp3a_ratio = 0
        if lots_d['cp3a'][1]+lots_d['cp3a'][0] != 0:
            cp3a_ratio = round((cp3a_outputs[0][hour]+cp3a_outputs[1][hour])*100/(lots_d['cp3a'][1]+lots_d['cp3a'][0]))
        cp3a_style = dash.no_update
        
        if 'cp3a' not in non_empty_cps:
            cp3a_ratio = "-"
            cp3a_style = {'background-color':'gray', 'top':'17%', 'left':'32%'}
        elif cp3a_ratio >= 60 and cp3a_ratio < 70:
            cp3a_style = {'background-color':'orange', 'top':'17%', 'left':'32%'}
        elif cp3a_ratio >= 70:
            cp3a_style = {'background-color':'red', 'top':'17%', 'left':'32%'}
        else:
            cp3a_style = {'background-color':'green', 'top':'17%', 'left':'32%'}

        cp3a_ratio_string = "-"
        if 'cp3a' in non_empty_cps:
            cp3a_ratio_string = str(cp3a_outputs[0][hour]+cp3a_outputs[1][hour]) + "/" + str(lots_d['cp3a'][1]+lots_d['cp3a'][0])

        occupied_cp3a =  html.Div([
            html.B("Occupied Lots: " + str(cp3a_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp3a_outputs[1][hour]) + '/' + str(lots_d['cp3a'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp3a_outputs[0][hour]) + '/' + str(lots_d['cp3a'][0]), style = {"color" : "black"})])

        cp4_outputs = outputs['cp4']
        cp4_ratio = 0
        if lots_d['cp4'][1]+lots_d['cp4'][0] != 0:
            cp4_ratio = round((cp4_outputs[0][hour]+cp4_outputs[1][hour])*100/(lots_d['cp4'][1]+lots_d['cp4'][0]))
        cp4_style = dash.no_update
        

        if 'cp4' not in non_empty_cps:
            cp4_ratio = "-"
            cp4_style = {'background-color':'gray', 'top':'32%', 'left':'34%'}
        elif cp4_ratio >= 60 and cp4_ratio < 70:
            cp4_style = {'background-color':'orange', 'top':'32%', 'left':'34%'}
        elif cp4_ratio >= 70:
            cp4_style = {'background-color':'red', 'top':'32%', 'left':'34%'}
        else:
            cp4_style = {'background-color':'green', 'top':'32%', 'left':'34%'}

        cp4_ratio_string = "-"
        if 'cp4' in non_empty_cps:
            cp4_ratio_string = str(cp4_outputs[0][hour]+cp4_outputs[1][hour]) + "/" + str(lots_d['cp4'][1]+lots_d['cp4'][0])

        occupied_cp4 =  html.Div([
            html.B("Occupied Lots: " + str(cp4_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp4_outputs[1][hour]) + '/' + str(lots_d['cp4'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp4_outputs[0][hour]) + '/' + str(lots_d['cp4'][0]), style = {"color" : "black"})])

        cp5_outputs = outputs['cp5']
        cp5_ratio = 0
        if lots_d['cp5'][1]+lots_d['cp5'][1] != 0:
            cp5_ratio = round((cp5_outputs[0][hour]+cp5_outputs[1][hour])*100/(lots_d['cp5'][1]+lots_d['cp5'][0]))
        cp5_style = dash.no_update
        
        if 'cp5' not in non_empty_cps:
            cp5_ratio = "-"
            cp5_style = {'background-color':'gray', 'top':'34%', 'left':'43%'}
        elif cp5_ratio >= 60 and cp5_ratio < 70:
            cp5_style = {'background-color':'orange', 'top':'34%', 'left':'43%'}
        elif cp5_ratio >= 70:
            cp5_style = {'background-color':'red', 'top':'34%', 'left':'43%'}
        else:
            cp5_style = {'background-color':'green', 'top':'34%', 'left':'43%'}

        cp5_ratio_string = "-"
        if 'cp5' in non_empty_cps:
            cp5_ratio_string = str(cp5_outputs[0][hour] + cp5_outputs[1][hour]) + "/" + str(lots_d['cp5'][1]+lots_d['cp5'][0])

        occupied_cp5 =  html.Div([
            html.B("Occupied Lots: " + str(cp5_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp5_outputs[1][hour]) + '/' + str(lots_d['cp5'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp5_outputs[0][hour]) + '/' + str(lots_d['cp5'][0]), style = {"color" : "black"})])

        cp5b_outputs = outputs['cp5b']
        cp5b_ratio = 0
        if lots_d['cp5b'][1] != 0:
            cp5b_ratio = round((cp5b_outputs[1][hour])*100/(lots_d['cp5b'][1]))
        cp5b_style = dash.no_update
        
        if 'cp5b' not in non_empty_cps:
            cp5b_ratio = "-"
            cp5b_style = {'background-color':'gray', 'top':'25.5%', 'left':'42%'}
        elif cp5b_ratio >= 60 and cp5b_ratio < 70:
            cp5b_style = {'background-color':'orange', 'top':'25.5%', 'left':'42%'}
        elif cp5b_ratio >= 70:
            cp5b_style = {'background-color':'red', 'top':'25.5%', 'left':'42%'}
        else:
            cp5b_style = {'background-color':'green', 'top':'25.5%', 'left':'42%'}

        cp5b_ratio_string = "-"
        if 'cp5b' in non_empty_cps:
            cp5b_ratio_string = str(cp5b_outputs[1][hour]) + "/" + str(lots_d['cp5b'][1])

        occupied_cp5b =  html.Div([
            html.B("Occupied Lots: " + str(cp5b_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp5b_outputs[1][hour]) + '/' + str(lots_d['cp5b'][1]), style = {'color':'#FF2800'}),
            #html.Div("Occupied White Lots: " + str(cp5b_outputs[0]) + '/' + str(0), style = {"color" : "white"})
            ])

        cp6b_outputs = outputs['cp6b']
        cp6b_ratio = 0
        if lots_d['cp6b'][1]+lots_d['cp6b'][0] != 0:
            cp6b_ratio = round((cp6b_outputs[0][hour]+cp6b_outputs[1][hour])*100/(lots_d['cp6b'][1]+lots_d['cp6b'][0]))
        cp6b_style = dash.no_update
        
        if 'cp6b' not in non_empty_cps:
            cp6b_ratio = "-"
            cp6b_style = {'background-color':'gray', 'top':'62%', 'left':'62%'}
        elif cp6b_ratio >= 60 and cp6b_ratio < 70:
            cp6b_style = {'background-color':'orange', 'top':'62%', 'left':'62%'}
        elif cp6b_ratio >= 70:
            cp6b_style = {'background-color':'red', 'top':'62%', 'left':'62%'}
        else:
            cp6b_style = {'background-color':'green', 'top':'62%', 'left':'62%'}

        cp6b_ratio_string = "-"
        if 'cp6b' in non_empty_cps:
            cp6b_ratio_string = str(cp6b_outputs[0][hour]+cp6b_outputs[1][hour]) + "/" + str(lots_d['cp6b'][1]+lots_d['cp6b'][0])

        occupied_cp6b =  html.Div([
            html.B("Occupied Lots: " + str(cp6b_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp6b_outputs[1][hour]) + '/' + str(lots_d['cp6b'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp6b_outputs[0][hour]) + '/' + str(lots_d['cp6b'][0]), style = {"color" : "black"})])

        cp10_outputs = outputs['cp10']
        cp10_ratio = 0
        if lots_d['cp10'][1]+lots_d['cp10'][0] != 0:
            cp10_ratio = round((cp10_outputs[0][hour]+cp10_outputs[1][hour])*100/(lots_d['cp10'][1]+lots_d['cp10'][0]))
        cp10_style = dash.no_update

        if 'cp10' not in non_empty_cps:
            cp10_ratio = "-"
            cp10_style = {'background-color':'gray', 'top':'53%', 'left':'84%'}
        elif cp10_ratio >= 60 and cp10_ratio < 70:
            cp10_style = {'background-color':'orange', 'top':'53%', 'left':'84%'}
        elif cp10_ratio >= 70:
            cp10_style = {'background-color':'red', 'top':'53%', 'left':'84%'}
        else:
            cp10_style = {'background-color':'green', 'top':'53%', 'left':'84%'}

        cp10_ratio_string = "-"
        if 'cp10' in non_empty_cps:
            cp10_ratio_string = str(cp10_outputs[0][hour]+cp10_outputs[1][hour]) + "/" + str(lots_d['cp10'][1]+lots_d['cp10'][0])

        occupied_cp10 =  html.Div([
            html.B("Occupied Lots: " + str(cp10_ratio_string), style = {"color" : "black"}),
            html.Div("Occupied Red Lots: " + str(cp10_outputs[1][hour]) + '/' + str(lots_d['cp10'][1]), style = {'color':'#FF2800'}),
            html.Div("Occupied White Lots: " + str(cp10_outputs[0][hour]) + '/' + str(lots_d['cp10'][0]), style = {"color" : "black"})])

        return cp3_style,cp3_ratio,occupied_cp3,cp3a_style,cp3a_ratio,occupied_cp3a,cp4_style,cp4_ratio,occupied_cp4,cp5_style,cp5_ratio,occupied_cp5,cp5b_style,cp5b_ratio,occupied_cp5b,cp6b_style,cp6b_ratio,occupied_cp6b, cp10_style,cp10_ratio,occupied_cp10
    else:
        return dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update,dash.no_update, dash.no_update, dash.no_update

@callback(
    Output('results-download-button','disabled'),
    Input('results-slider','disabled')
)
def allow_downloads(disabled):
    return disabled


@callback(
    Output("download-results","data"),
    Input('results-download-button', 'n_clicks'),
    prevent_initial_call = True
)
def download_data(clicks):
    if clicks:    
        hour = list(range(24))
        cp = list(outputs.keys())

        # Generate White Enter Df
        white_entered_df = pd.DataFrame()
        white_entered_df['hour'] = hour
        for carpark in cp:
            white_entered_df[carpark+'_white_entered'] = outputs[carpark][0]

        columns_to_reverse = white_entered_df.columns[1:]
        for column in columns_to_reverse:
            white_entered_df[column] = white_entered_df[column].diff().fillna(white_entered_df[column])

        
        # Generate Red Enter Df
        red_entered_df = pd.DataFrame()
        red_entered_df['hour'] = hour
        for carpark in cp:
            red_entered_df[carpark+'_red_entered'] = outputs[carpark][1]
        
        columns_to_reverse = red_entered_df.columns[1:]
        for column in columns_to_reverse:
            red_entered_df[column] = red_entered_df[column].diff().fillna(red_entered_df[column])

        # Generate White Rejected Df
        white_rejected_df = pd.DataFrame()
        white_rejected_df['hour'] = hour
        for carpark in cp:
            white_rejected_df[carpark+'_white_rejected'] = outputs[carpark][2]
        
        columns_to_reverse = white_rejected_df.columns[1:]
        for column in columns_to_reverse:
            white_rejected_df[column] = white_rejected_df[column].diff().fillna(white_rejected_df[column])
        
        # Generate Red Rejected Df
        red_rejected_df = pd.DataFrame()
        red_rejected_df['hour'] = hour
        for carpark in cp:
            red_rejected_df[carpark+'_white_rejected'] = outputs[carpark][3]
        
        columns_to_reverse = red_rejected_df.columns[1:]
        for column in columns_to_reverse:
            red_rejected_df[column] = red_rejected_df[column].diff().fillna(red_rejected_df[column])

        # Generate White Occupancies Df
        white_occupancies_df = pd.DataFrame()
        white_occupancies_df['hour'] = hour
        for carpark in cp:
            white_occupancies_df[carpark+'_white_occupied'] = outputs[carpark][4]

        # Generate Red Occupancies Df
        red_occupancies_df = pd.DataFrame()
        red_occupancies_df['hour'] = hour
        for carpark in cp:
            red_occupancies_df[carpark+'_red_occupied'] = outputs[carpark][5]
        
        
        excel_writer = pd.ExcelWriter("simulation_statistics.xlsx", engine="xlsxwriter")

        # List of dataframes
        dataframes = [white_entered_df, red_entered_df, white_rejected_df, red_rejected_df, white_occupancies_df, red_occupancies_df]
        sheet_names = ["White Cars Entered By Hour", "Red Cars Entered By Hour", "White Cars Rejected By Hour", "Red Cars Rejected By Hour",
        "White Car Occupancies By Hour", "Red Car Occupancies By Hour"]

        # Save each dataframe to a separate sheet
        for i, df in enumerate(dataframes):
            sheet_name = sheet_names[i]
            df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

        # Save and close the Excel file
        excel_writer.save()


        return dcc.send_file(excel_writer,"simulation_statistics.xlsx")
    else:
        return None

@callback(Output("progress-bar", "value"), Trigger("interval", "n_intervals"))
def update_progress(trig):
    global fsc
    value = fsc.get("progress")  # get progress
    return value

@callback(
    Output("progress-bar","value", allow_duplicate=True),
    Input("loading-modal","is_open"),
    prevent_initial_call=True
)
def reset_progress(is_open):
    if not is_open:
        fsc.set('progress',0)
        return 0
    else:
        return dash.no_update
