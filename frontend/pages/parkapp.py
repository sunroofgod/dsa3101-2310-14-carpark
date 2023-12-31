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
sys.path.append(os.path.join(path, "backend", "des"))

# Importing Helper Functions from Backend
from params import get_month_arrival_rate, get_day_arrival_rate, get_carpark_capacity
from DES import run_nsim, stats_mean

dash.register_page(__name__) 

'''
Section 1: Global Variables
'''
'''1.1 Inputs'''
# Campus Events and Corresponding Dates
campus_events = ['No Event','Week 0 New AY', 'Well-Being Day', 'Commencement', 'Examinations', 'Staff WFH Day', 'Rag & Flag Day', 'SuperNova', 'Open Day', 'Public Holiday']
events_date_values = ['','2022-08-01','2022-10-21','2022-07-16','2022-11-21','2023-04-06','2022-08-06','2022-08-12','2023-03-04','2023-01-01']
event_dates = dict(zip(campus_events,events_date_values)) #Key is event, value is date of event

# Options for Select Month Dropdown
months = [{'label':'January','value':1},{'label':'February','value':2},{'label':'March','value':3},{'label':'April','value':4},
          {'label':'May','value':5},{'label':'June','value':6},{'label':'July','value':7},{'label':'August','value':8},
          {'label':'September','value':9},{'label':'October','value':10},{'label':'November','value':11},{'label':'December','value':12}]

# Recover alphabetical representation of Month from month number
month_dict = {1: 'January', 2: 'Februrary', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 
                      8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December' }

# Initial Arrival Rates (Clean State)
# Format for all arrival rate dictionaries {int:int} where key is hour and value is arrival rate for hour
default_arrivals = {0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0,18:0,19:0,20:0,21:0,22:0,23:0}

# Available Carparks
all_carparks = ['cp3','cp3a','cp4','cp5','cp5b','cp6b','cp10']

# Initial Carpark Capacities
carpark_cap = get_carpark_capacity(all_carparks)

# Current setting of capark capacity, initialized to be default carpark capacities
lots_d = get_carpark_capacity(all_carparks)

# Settings for carpark button position
# settings list: [button_top, button_left, text_top, text_left], CSS style settings in percentage
button_settings = {
    'cp3': ['16%', '27%', '12%', '27.7%'],
    'cp3a': ['17%', '32%', '13%', '32.3%'],
    'cp4': ['32%', '34%', '39%', '34.8%'],
    'cp5': ['34%', '43%', '41%', '43.8%'],
    'cp5b': ['25.5%', '42%', '21.5%', '42.3%'],
    'cp6b': ['62%', '62%', '69%', '62.3%'],
    'cp10': ['53%', '84%', '60%', '84.3%'],
}


# Full Name of Carparks
cp_names = {'cp3':'UCC/YST Conservatory of Music', 'cp3a':'LKCNHM', 'cp4':'Raffles Hall/CFA', 'cp5':'University Sports Centre', 'cp5b':'NUS Staff Club', 'cp6b':'University Hall', 'cp10':'S17'} 

'''1.2 Outputs'''
# Initial Display for Carpark Occupancies
default_button = "0"

# Most Recent Simulation Result, Initialised as empty dict
results = {}

# Children for the results modal to store up to two recent student simulations, initialized as empty list
results_body = []

"""1.3 Misc"""
# Object to store progress bar Percentage
fsc = FileSystemCache("cache_dir")
fsc.set("progress", 0)

'''1.4 CSS Styles"'''
# Styling Options for Non-Carpark Buttons, buggy results when implmenting this through .css
grey_buttons_left = style={'display':'inline-block', 'background-color':'#a9a9a9', 'color' : '#000000' 
,'border-color':'#000000', 'border-width':'medium', 'font-size':'15px', 'font-weight': 'bold'}
grey_buttons_right = {'display':'inline-block','margin-bottom':'2%','display':'inline-block', 
'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'} 
grey_buttons_right_2 = {'display':'inline-block','margin-bottom':'2%','margin-right':'2%','display':'inline-block', 
'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'} 
black_button_right = {'margin-bottom':'2%','display':'inline-block', 'background-color':'#000000', 'color' : '#FFFFFF' ,
'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}


'''
Section 2: Frontend Helper Functions
'''

'''2.1 Inputs'''
'''2.1.1 Arrival Rates'''
# Helper function to generate arrival rates given month
# Input event: string representing event e.g. "Open Day"
# Output: dict, {int:int} , keys: integers 0-23 representing hour of day, values: arrivals for that hour
def get_event_arrival_rate(event): 
    date = event_dates[event]
    d = get_day_arrival_rate(date) # Using backend helper function to obtain arrival rates for historical arrivals for events
    nd = {}

    for i in range(24):
        if i in d.keys():
            nd[i] = d[i]
        else:
            nd[i] = 0

    return nd

# Helper Function to create dash slider components
# Inputs:
# hour: integer representing hour, val: integer representing current arrival rate for that hour
# Output: dash component containing dash vertical slider component to adjust arrival rate for that hour and html div to display the value of the slider
# id for slider will be slider_hournumber e.g. 'slider_1' for slider adjusting arrival rates for 1 am.
# id for html div that displays value is value_hournumber e.g. 'value_1'
def vert_slider(hour, val):
    return dbc.Col([html.Div(html.Div(str(val), id = "value_" + str(hour)), style= {'font-size':'16px','text-align':'center', 'margin-right':'50%'}),
                    html.Div(dcc.Slider(id = "slider_" + str(hour),min = 0, max = 500, step = 1, value = val, vertical = True,marks = None), style={'padding':'0px','margin-left':'10%'}), 
                    html.Div(html.Div(str(hour)), style= {'text-align':'center', 'margin-right':'50%'})],style={'padding':'0px'})


# Helper function create refine graph modal
# Inputs: 
# base: string representing month/event being simulated
# arrival_d: dictionary of arrival rates {int:int}, key is hour 0-23, value is arrival rate for that hour
# Output: modal that would pop up when users click on the refine arrival rates button 
# id for this component is 'refine-modal' 
def refine_modal(base, arrival_d):
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Current Base: "+ base), close_button= False),
        dbc.ModalBody([html.H4("Drag Sliders to Modify Number of Cars arriving in NUS at each hour"),
                        dbc.Row([vert_slider(i, arrival_d[i]) for i in range(24)], id = 'row_slider', style={'padding-left':'2%'}), # makes use of vert_slider function
                        html.B('Enter Hour')
                        ], style= {'text-align':'center', 'font-size':'19px'}),
                        
        dbc.ModalFooter([
                    dbc.Button('Reset to Base', id = 'refine-modal-reset',style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
                    dbc.Button(
                        "Save and Exit", id="close-refine-modal", style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}
                    )])
    ], id = 'refine-modal', is_open= False, backdrop = False, centered = True, size = 'xl', style = {'zoom':'75%'})


# Helper function to generate line plot from arrival rates dictionary
# Inputs:
# arrival_d: dictionary of arrival rates {int:int}, key is hour 0-23, value is arrival rate for that hour
# width: integer representing width of plot
# height: integer representing height of plot
# Output: plotly time series line graph displaying arrival rates across time
def generate_arrival_rate_graph(arrival_d,width,height): 
    df = pd.DataFrame({'hour':arrival_d.keys(),'arrivals':arrival_d.values()})
    fig = px.line(df, x = 'hour', y = 'arrivals', title = '<b>Arrival Rates</b>',
                  labels = {'hour':'Hour of Day', 'arrivals': 'Number of Entries'},width=width, height=height)
    fig.update_layout(margin = dict(l=50,r=20,b=20,t=40), font_family = "Open Sans", title_x = 0.5)
    fig.update_yaxes(rangemode='nonnegative')
    return fig

'''2.1.2 Carpark Capacities'''
# Function to generate carpark buttons for each carpark
# Inputs:
# cp: string of carpark e.g. 'cp3'
# rate: string displaying occupancy rate
# background_col: css option for background-color of button
# Output:
# html Div containing the button with the id equal to the cp input, and text label of carpark
def cp_button(cp,rate,background_col):
    settings_list = button_settings[cp]
    children = html.Div([
                html.Button(rate, id=cp, className = 'cp-button', style = {'top':settings_list[0], 'left':settings_list[1], 'background-color': background_col}),
                html.Div(cp.upper(), style = {'position': 'absolute', 'top': settings_list[2], 'left': settings_list[3], 'font-weight': 'bold'})
                ]
                )
    return children


# Helper function to initialize carpark modal, i.e. popups when each carpark button is clicked
# Inputs:
# cp: string representing carpark e.g. 'cp3'
# Output:
# dash modal for carpark with id modal-cp_num e.g. 'modal-cp3' 
def cp_modal(cp):
    white_cap = carpark_cap[cp][0] #Optain Default white lot capacity for carpark
    red_cap = carpark_cap[cp][1] #Optain Default red lot capacity for carpark

    # if else is to have different adjustment options for carpark 5b and other carparks.
    # Carpark 5b only has red lots since it is a staff carpark, so that is the only capacity that can be adjusted
    # Rest of the carparks can adjust white:red lot ratio, white lot capacity and red lot capacity
    if cp != "cp5b":
        display_child = [
                html.B("Occupied Lots: 0/" + str(white_cap + red_cap), style = {"color" : "black"}),
                html.Div("Occupied Red Lots: 0/" + str(red_cap), style = {'color':'red'}),
                html.Div("Occupied White Lots: 0/" + str(white_cap), style = {"color" : "black"})]
        adjustment_child = [
                html.Div(html.B('Adjust Ratio of White:Red Lots:'),style= {'text-align':'center', 'color' : 'navy'}),
                html.Div(dcc.Slider(id = "slider_ratio_"+cp,min = 0, max = white_cap+red_cap, step = 1, value = white_cap, marks = None)),
                html.Div(html.B('Adjust Red Lot Capacity:'),style= {'text-align':'center', 'color' : 'red'}),
                html.Div(dcc.Slider(id = "slider_red_"+cp,min = 0, max = red_cap, step = 1, value = red_cap, marks = None)),
                html.Div(html.B('Adjust White Lot Capacity:'),style= {'text-align':'center', 'color' : 'black'}),
                html.Div(dcc.Slider(id = "slider_white_"+cp,min = 0, max = white_cap, step = 1, value = white_cap, marks = None)),
                html.Div(
                    [html.B("Red Lot Capacity to Simulate: " + str(red_cap) + " (100% Capacity)",id = 'to_simulate_red_'+cp, style = {'font-size':'15px', 'color':'red'}),
                    html.Br(),
                    html.B("White Lot Capacity to Simulate: " + str(white_cap) + " (100% Capacity)",id = 'to_simulate_white_'+cp, style = {'font-size':'15px', "color" : "black"})]
                )
                ]
    else:
        display_child = [
                html.B("Occupied Lots: 0/" + str(white_cap + red_cap), style = {"color" : "black"}),
                html.Div("Occupied Red Lots: 0/" + str(red_cap), style = {'color':'red'})]
        adjustment_child = [
                html.Div(html.B('Adjust Red Lot Capacity:'),style= {'text-align':'center', 'color' : 'red'}),
                html.Div(dcc.Slider(id = "slider_red_"+cp,min = 0, max = red_cap, step = 1, value = red_cap, marks = None)),
                html.Div(
                    [html.B("Red Lot Capacity to Simulate: " + str(red_cap) + " (100% Capacity)",id = 'to_simulate_red_'+cp, style = {'font-size':'15px', 'color':'red'}),
                    html.Br(),
                    ]
                )
                ]
    
    modal = dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(cp.upper() + ": " + cp_names[cp], style = {"color" : "white"}), close_button= False, style = {"background-color": "#003d7c"}),
            dbc.ModalBody([
                html.Div(display_child, id = 'occupied_'+cp),
                html.Br(),
                html.H4('Simulation Parameters:', style = {"color" : "black"}),
                html.B('Carpark Status:', style = {"color" : "black"}),
                html.Div(dcc.Dropdown(options=['Open','Closed'], id = 'cp_status_'+cp, value = "Open", clearable = False), style={'margin-bottom':'3%'}),
                html.Div(adjustment_child) # Different whether is carpark 5b or not
            ], style= {'text-align':'center', 'font-size':'19px', "background-color": "white"}),
            dbc.ModalFooter([
                        dbc.Button('Reset Parameters', id = 'reset-modal-'+cp,style = grey_buttons_right),
                        dbc.Button(
                            "Save and Exit", id="close-modal", style = grey_buttons_right
                        )]
                        , style = {"background-color" : "#003d7c"})
        ], id = 'modal-'+cp, is_open= False, backdrop = False, centered = True,style = {'zoom':'75%'})
    return modal



'''2.2 Simulate'''
# Helper function for confirmation of simulation modal, i.e. when user clicks on the simulate button
# Output:
# dash modal showing the input parameters with id 'simulate-modal'
def simulate_modal():
    return dbc.Modal([
         dbc.ModalHeader(dbc.ModalTitle('Initializing Simulation:'), close_button= False, style={'border':'navy 3px solid', 'font-family' : 'Open Sans', 
         'font-size':'20px','font-weight' : 'bold', 'background-color':'navy','color' : 'white'}),
         dbc.ModalBody(id = 'simulate-modal-contents', style = {'text-align':'center', 'font-size':'15px', 'border': ' black 3px solid'}),
         dbc.ModalFooter(children = [
            html.H5("Confirm Simulation?", style = {'color':'white'}),
            dbc.Button('Yes', id = 'simulate-modal-yes' ,style = {'background-color':'#06a11b', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
            dbc.Button('No', id = 'simulate-modal-no' ,style = {'background-color':'red', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
         ], style ={'border': 'navy 3px solid','background-color':'navy'})
    ], id = 'simulate-modal', is_open = False, backdrop = False, centered = True,style = {'zoom':'75%'})

'''2.3 Output'''
# Helper function to create results modal
# Inputs:
# results: dictionary
# Format of dictionary {string: list of 4 lists}
# keys are carpark strings e.g. 'cp3'
# values are list of lists. 
# [list of cummsum cars entered by hour, list of cummsum number of rejected cars by hour, list absolute occupancy of white lots, list absolute occupancy of red lots]
# Each sublist consists of 24 values with index representing hour of that statistic
# Function creates 4 plotly plots and displays them in a modal. 
# 4 plots display statistics for total cars entered, total cars rejected, percentage cars rejected, maximum occupancy rate
# Also saves the most recent set of plots to the global variable results_body, allowing for users to view the most recent 2 simulations in the results modal
# Output of this function:
# dash modal object that displays summary statistics, id of this modal is 'results-modal'
def generate_results_modal(results):
    if results == {}:
        # Case when app is just initialised and no simulations have been run
        body = dbc.ModalBody(html.H4('No Simulations have been run'), id = 'results-modal-contents', style = {'text-align':'center'})
    else:
        # Creating results data frame
        carparks = list(results.keys())

        # for total cars entered
        white_entered = list([result[0][-1] for result in results.values()])
        red_entered = list([result[1][-1] for result in results.values()])

        # for total cars rejected
        white_rej = list([result[2][-1] for result in results.values()])
        red_rej = list([result[3][-1] for result in results.values()])

        # for maximum occupancy
        max_white = list([max(result[4]) for result in results.values()])
        max_red = list([max(result[5]) for result in results.values()])
        white_cap = list([lots[0] for lots in lots_d.values()])
        red_cap = list([lots[1] for lots in lots_d.values()])
        
        # Arranging the dataframe in carpark order
        df = pd.DataFrame({'carpark':carparks, 'white_entered':white_entered, 'red_entered':red_entered, 'white_rej':white_rej, 'red_rej':red_rej, 'max_white':max_white, 'max_red':max_red}).sort_values('carpark')
        df['order'] = [6,0,1,2,3,4,5]
        df.sort_values('order',inplace = True)
                
        # Obtaining total entered statistic for each carpark
        df['total_entered'] = df["red_entered"] + df["white_entered"]

        # Obtaining rejection statistic for each carpark
        df['total_rej'] = df["red_rej"] + df["white_rej"]
        df['white_rej_percent'] = (df['white_rej'] / df['white_entered']).fillna(0) * 100
        df['red_rej_percent'] = (df['red_rej'] / df['red_entered']).fillna(0) * 100
        df['total_rej_percent'] = (df['total_rej'] / df['total_entered']).fillna(0) * 100
        
        # Obtaining max occupancy statistic for each carpark
        df['white_cap'] = white_cap
        df['red_cap'] = red_cap
        df['max_white'] = round(df['max_white']/df['white_cap'] * 100)
        df['max_red'] = round(df['max_red']/df['red_cap'] * 100)

        # Total Enter Graph
        fig1 = px.bar(df, x = 'carpark', y = ['white_entered','red_entered','total_entered'],
        title = 'Total Cars Entered by Carpark', barmode = 'group', labels = {'value':'Number Entries','variable':'Entry Type'})
        fig1.update_traces(name='White', selector=dict(name='white_entered'))
        fig1.update_traces(name='Red', selector=dict(name='red_entered'))
        fig1.update_traces(name='Total', selector=dict(name='total_entered'))
        fig1.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig1.update_yaxes(rangemode='nonnegative')
        fig1.update_layout(xaxis_title="Carpark")

        # Total Reject Graph
        fig2 = px.bar(df, x = 'carpark', y = ['white_rej','red_rej','total_rej'],
        title = 'Total Cars Rejected by Carpark', barmode = 'group', labels = {'value':'Number Rejected','variable':'Entry Type'})
        fig2.update_traces(name='White', selector=dict(name='white_rej'))
        fig2.update_traces(name='Red', selector=dict(name='red_rej'))
        fig2.update_traces(name='Total', selector=dict(name='total_rej'))
        fig2.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig2.update_yaxes(rangemode='nonnegative')
        fig2.update_layout(xaxis_title="Carpark")

        # Rejection Percentage Graph
        fig3 = px.bar(df, x = 'carpark', y = ['white_rej_percent','red_rej_percent','total_rej_percent'],
        title = 'Percent Cars Rejected by Carpark', barmode = 'group', labels = {'value':'Percent Rejected (%)','variable':'Entry Type'})
        fig3.update_traces(name='White', selector=dict(name='white_rej_percent'))
        fig3.update_traces(name='Red', selector=dict(name='red_rej_percent'))
        fig3.update_traces(name='Total', selector=dict(name='total_rej_percent'))
        fig3.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig3.update_yaxes(rangemode='nonnegative')
        fig3.update_layout(xaxis_title="Carpark")

        # Maximum Occupancy Rate Graph
        fig4 = px.bar(df, x = 'carpark', y = ['max_white','max_red'],
        title = 'Maximum Percentage Occupancy by Carpark', barmode = 'group', labels = {'value':'Percent Occupied (%)','variable':'Entry Type'})
        fig4.update_traces(name='White', selector=dict(name='max_white'))
        fig4.update_traces(name='Red', selector=dict(name='max_red'))
        fig4.update_xaxes(tickvals=[0, 1, 2, 3,4,5,6], ticktext=['CP3', 'CP3A', 'CP4', 'CP5','CP5B','CP6B','CP10'])
        fig4.update_yaxes(rangemode='nonnegative')
        fig4.update_layout(xaxis_title="Carpark")

        # Store most recent graphs globaly
        current_graphs = dbc.Col(
            [dbc.Row(dcc.Graph(figure = fig1)),
            dbc.Row(dcc.Graph(figure = fig2)),
            dbc.Row(dcc.Graph(figure = fig3)),
            dbc.Row(dcc.Graph(figure = fig4))],
            )
        global results_body
        results_body.append(current_graphs)

        # Ensuring that only the two most recent simulation graphs will be displayed
        if len(results_body) > 2:
            results_body.pop(0)

        # Setting headers
        if len(results_body) == 1: # Case when one simulation
            header = dbc.Row(dbc.Col(html.H4("Current Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'}))
        else: # Case when more than two simulations have been run
            header = dbc.Row([dbc.Col(html.H4("Previous Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'}),
            dbc.Col(html.H4("Current Simulation Statistics", style = {'text-decoration':'underline'}),style = {'text-align':'center'})])

        body = dbc.ModalBody(
            [
                header,
                dbc.Row(results_body) # Different contents for body depending on how many simulations have been run
            ], style = {'border':'black 3px solid'}
        )

    modal = dbc.Modal([
         dbc.ModalHeader(dbc.ModalTitle('Simulation Results:'), close_button= False, style = {'border': 'navy 3px solid', 'background-color':'navy','color' : 'white'}),
         body,
         dbc.ModalFooter([
            dbc.Button('Download Current Statistics', id = 'results-download-button', disabled = True, style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}),
            dbc.Button('Close', id = 'results-modal-close' ,style = {'background-color':'#a9a9a9', 'border-color':'#000000', 'color' : '#000000', 'border-width':'medium', 'font-size':'19px','font-weight': 'bold'}),
         ], style = {'border': 'navy', 'background-color':'navy','color' : 'white', 'border':'navy 3px solid'})
    ], id = 'results-modal', is_open = False, backdrop = False, centered = True, size = 'xl', style = {'zoom':'75%'})

    return modal


'''
Section 3: Page Layout
'''
layout = dbc.Container([
    dbc.Row([
        # Left partition
        dbc.Col( 
            html.Div([
                html.H4("Currently Simulating:", style={'font-weight':'bold'}),
                html.Div("None",id = "simulation-contents"),
                html.Br(),
                html.Div('Unavailable, run simulations first', id = 'hour-slider-show', style = {'font-size':'15px'}),
                dcc.Slider(min = 0, max = 23, step = 1,  value = 23, id = 'results-slider', disabled = True, marks = None),
                dbc.Button('View Simulation Results', id='results-button', style = grey_buttons_left)
            ]
            ),
            width={'size': 2, 'order': 1},
            style = {'text-align':'center','background-color':'#003d7c','padding-top':'1%','color':'#FFFFFF', 'align-items': 'center'}
            ),
        
        # Center partition
        dbc.Col( 
            html.Div([
            html.Div(html.Img(src=dash.get_asset_url('nus_map.png'), style={'width': '100%', 'height': 'auto'}), 
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),

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

            cp_button('cp3',"0",'green'),
            cp_button('cp3a',"0",'green'),
            cp_button('cp4',"0",'green'),
            cp_button('cp5',"0",'green'),
            cp_button('cp5b',"0",'green'),
            cp_button('cp6b',"0",'green'),
            cp_button('cp10',"0",'green'),
                ],
                style={'position': 'relative', 'font-size': '22.8px'}
            ),
            width={'size': 8, 'order': 2},
            style= {'padding': '0px'}
            ),

        # Right partition
        dbc.Col([ 
            html.Div([html.Div(html.B("Select Event")),
            html.Div(dcc.Dropdown(id = 'event-picker', options=campus_events, value = "No Event", clearable = False))]),
            html.Br(),
            html.Div([html.Div(html.B("Select Month")),
            html.Div(dcc.Dropdown(id = 'month-picker', options=months))]),
            html.Br(),
            dbc.Button('Reset Events and Months', id='reset-events-button', style=grey_buttons_right),
            html.Br(),
            html.Br(),
            html.Div(dcc.Graph(id = "arrival-graph",config = {'staticPlot': True},
            figure = generate_arrival_rate_graph(default_arrivals,300,300)), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'width': '100%'}),
            html.Br(),
            dbc.Button('Refine Arrival Rate', id='refine-button', style = grey_buttons_right),
            html.Br(),
            dbc.Button('Reset CP Params', id='reset-cp-button', style = grey_buttons_right),
            html.Br(),            
            dbc.Button('Reset All', id='reset-button', style= grey_buttons_right_2),
            dbc.Button('Simulate', id='simulate-button', style= black_button_right),
            html.Br(),
            ], 
            width={'size': 2, 'order': 3},
            style = {'text-align':'center','padding-top':'2%', 'background-color':'#ef7c00'})
            ]),
        
        ### Hidden Components

        # Arrival Rate Modal
        html.Div(refine_modal('No Event', default_arrivals), id = 'refine-modal-block'), 
        
        # Carpark Modals
        html.Div(cp_modal("cp3"), id = 'cp3_modal'),
        html.Div(cp_modal("cp3a"), id = 'cp3a_modal'),
        html.Div(cp_modal("cp4"), id = 'cp4_modal'),
        html.Div(cp_modal("cp5"), id = 'cp5_modal'),
        html.Div(cp_modal("cp5b"), id = 'cp5b_modal'),
        html.Div(cp_modal("cp6b"), id = 'cp6b_modal'),
        html.Div(cp_modal("cp10"), id = 'cp10_modal'),

        # Reset Modals
        html.Div(dbc.Modal([dbc.ModalBody("All Carpark Parameters have been reset!"), 
            dbc.ModalFooter(dbc.Button("Close", id="close-reset-cp-modal"))],
            id="reset-cp-modal",is_open=False, style = {'zoom':'75%'})),
        html.Div(dbc.Modal([dbc.ModalBody("All Events and Months have been reset!"),
            dbc.ModalFooter(dbc.Button("Close", id="close-reset-events-modal"))],
            id="reset-events-modal",is_open=False, style = {'zoom':'75%'})),
        html.Div(dbc.Modal([dbc.ModalBody("All simulations and settings have been reset!"),
            dbc.ModalFooter(dbc.Button("Close", id="close-reset-all-modal"))],
            id="reset-all-modal",is_open=False, style = {'zoom':'75%'})),

        html.Div(simulate_modal()), # Confirmation Modal
        html.Div(generate_results_modal({}), id = 'results-div'), # Results Modal
        html.Div(dcc.Download(id="download-results")), # Trigger Downloading of results

        # Loading Modal for Simulation
        html.Div(dbc.Modal([ 
            dbc.ModalBody([
            html.B("Simulation in Progress! Please wait...     ", style={'font-family' : 'Open Sans', 'font-size':'20px', 'color' : 'white', 
                                                                    'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height':'100%'}), 
            html.Br(),
            html.Div([dbc.Progress(value = 0, id = 'progress-bar', color = 'success', 
            label = '🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗 🚗'),dcc.Interval(id="interval", interval=500)]),
            html.Br(),
            html.Div(dbc.Spinner(color="white", type="border"), style = {'float':'right'})
            ] , style = {'border':'navy 3px solid', 'background-color' : 'navy'}), 
            ],id="loading-modal",is_open=False,backdrop = False,centered = True, style = {'zoom':'75%'}))

    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})

'''
Section 4: Callbacks
'''
'''4.1 Inputs'''
'''4.1.1 Arrival Rates'''
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


# Callback to display graph of arrival rates on right partition
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
        d = get_month_arrival_rate(month)
        return refine_modal(month_dict[month], d),generate_arrival_rate_graph(d,300,300)
    else:
        d = get_event_arrival_rate(event)
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

# Callback to reset refine modal to the base arrival rates of the user's event/month choice
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
            d = get_month_arrival_rate(month)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_rate_graph(d,300,300)
        else:
            d = get_event_arrival_rate(event)
            return [vert_slider(i, d[i]) for i in range(24)],generate_arrival_rate_graph(d,300,300)
    else:
        return dash.no_update, dash.no_update



'''4.1.2 Carpark Parameters'''
# Callback to toggle cp modal
@callback(
        Output('modal-cp3','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp3','n_clicks')
        
)
def toggle_refine_modal_cp3(n1,n2):
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
def show_cp_params_cp3(status):
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
)
def params_to_simulate_cp3(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp3'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp3'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp3','value',allow_duplicate = True),
    Output('slider_white_cp3','value',allow_duplicate = True),
    Output('slider_red_cp3','max'),
    Output('slider_white_cp3','max'),
    Input('slider_ratio_cp3','value'),
    State('slider_red_cp3','value'),
    State('slider_white_cp3','value'),
    prevent_initial_call = True
)
def change_ratio_cp3(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp3'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp3'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white


# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp3','value'),
    Output('slider_red_cp3','value'),
    Output('slider_white_cp3','value'),
    Output('cp_status_cp3','value'),
    Input('reset-modal-cp3','n_clicks'),
)
def reset_cp_params_cp3(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp3' in changed_id:
        return carpark_cap['cp3'][0],carpark_cap['cp3'][1], carpark_cap['cp3'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update


# Callback to toggle cp modal
@callback(
        Output('modal-cp3a','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp3a','n_clicks')
        
)
def toggle_refine_modal_cp3a(n1,n2):
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
def show_cp_params_cp3a(status):
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
)
def params_to_simulate_cp3a(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp3a'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp3a'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp3a','value',allow_duplicate = True),
    Output('slider_white_cp3a','value',allow_duplicate = True),
    Output('slider_red_cp3a','max'),
    Output('slider_white_cp3a','max'),
    Input('slider_ratio_cp3a','value'),
    State('slider_red_cp3a','value'),
    State('slider_white_cp3a','value'),
    prevent_initial_call = True
)
def change_ratio_cp3a(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp3a'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp3a'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white

# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp3a','value'),
    Output('slider_red_cp3a','value'),
    Output('slider_white_cp3a','value'),
    Output('cp_status_cp3a','value'),
    Input('reset-modal-cp3a','n_clicks'),
)
def reset_cp_params_cp3a(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp3a' in changed_id:
        return carpark_cap['cp3a'][0],carpark_cap['cp3a'][1], carpark_cap['cp3a'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp4','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp4','n_clicks')
        
)
def toggle_refine_modal_cp4(n1,n2):
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
def show_cp_params_cp4(status):
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
)
def params_to_simulate_cp4(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp4'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp4'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp4','value',allow_duplicate = True),
    Output('slider_white_cp4','value',allow_duplicate = True),
    Output('slider_red_cp4','max'),
    Output('slider_white_cp4','max'),
    Input('slider_ratio_cp4','value'),
    State('slider_red_cp4','value'),
    State('slider_white_cp4','value'),
    prevent_initial_call = True
)
def change_ratio_cp4(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp4'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp4'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white

# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp4','value'),
    Output('slider_red_cp4','value'),
    Output('slider_white_cp4','value'),
    Output('cp_status_cp4','value'),
    Input('reset-modal-cp4','n_clicks'),
)
def reset_cp_params_cp4(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp4' in changed_id:
        return carpark_cap['cp4'][0],carpark_cap['cp4'][1], carpark_cap['cp4'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp5','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp5','n_clicks')
        
)
def toggle_refine_modal_cp5(n1,n2):
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
def show_cp_params_cp5(status):
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
    #State('slider_red_cp5', 'max'),
    #State('slider_white_cp5', 'max'),
)
def params_to_simulate_cp5(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp5'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp5'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp5','value',allow_duplicate = True),
    Output('slider_white_cp5','value',allow_duplicate = True),
    Output('slider_red_cp5','max'),
    Output('slider_white_cp5','max'),
    Input('slider_ratio_cp5','value'),
    State('slider_red_cp5','value'),
    State('slider_white_cp5','value'),
    prevent_initial_call = True
)
def change_ratio_cp5(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp5'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp5'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white

# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp5','value'),
    Output('slider_red_cp5','value'),
    Output('slider_white_cp5','value'),
    Output('cp_status_cp5','value'),
    Input('reset-modal-cp5','n_clicks'),
)
def reset_cp_params_cp5(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp5' in changed_id:
        return carpark_cap['cp5'][0],carpark_cap['cp5'][1], carpark_cap['cp5'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp5b','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp5b','n_clicks')
        
)
def toggle_refine_modal_cp5b(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp5b" in changed_id:
        return True
    else:
        return False

# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp5b','disabled'),
    Input('cp_status_cp5b','value')
)
def show_cp_params_cp5b(status):
    if status == "Open":
        return False
    else:
        return True 
    
# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp5b','children'),
    Input('cp_status_cp5b','value'),
    Input('slider_red_cp5b','value'),
)
def params_to_simulate_cp5b(status,red):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp5b'][1])) + "% Capacity)"]

# Callback to reset simulation numbers
@callback(
    Output('slider_red_cp5b','value'),
    Output('cp_status_cp5b','value'),
    Input('reset-modal-cp5b','n_clicks'),
)
def reset_cp_params_cp5b(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp5b' in changed_id:
        return carpark_cap['cp5b'][1], "Open"
    else:
        return dash.no_update,dash.no_update

# Callback to toggle cp modal
@callback(
        Output('modal-cp6b','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp6b','n_clicks')
        
)
def toggle_refine_modal_cp6b(n1,n2):
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
def show_cp_params_cp6b(status):
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
    #State('slider_red_cp6b', 'max'),
    #State('slider_white_cp6b', 'max'),
)
def params_to_simulate_cp6b(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp6b'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp6b'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp6b','value',allow_duplicate = True),
    Output('slider_white_cp6b','value',allow_duplicate = True),
    Output('slider_red_cp6b','max'),
    Output('slider_white_cp6b','max'),
    Input('slider_ratio_cp6b','value'),
    State('slider_red_cp6b','value'),
    State('slider_white_cp6b','value'),
    prevent_initial_call = True
)
def change_ratio_cp6b(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp6b'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp6b'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white

# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp6b','value'),
    Output('slider_red_cp6b','value'),
    Output('slider_white_cp6b','value'),
    Output('cp_status_cp6b','value'),
    Input('reset-modal-cp6b','n_clicks'),
)
def reset_cp_params_cp6b(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp6b' in changed_id:
        return carpark_cap['cp6b'][0],carpark_cap['cp6b'][1], carpark_cap['cp6b'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update


# Callback to toggle cp modal
@callback(
        Output('modal-cp10','is_open'),
        Input("close-modal",'n_clicks'),
        Input('cp10','n_clicks')
        
)
def toggle_refine_modal_cp10(n1,n2):
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
def show_cp_params_cp10(status):
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
    #State('slider_red_cp10', 'max'),
    #State('slider_white_cp10', 'max'),
)
def params_to_simulate_cp10(status,red,white):
    if status == "Closed":
        return ["Red Lot Capacity to Simulate: 0 (0% Capacity)"], ["White Lot Capacity to Simulate: 0 (0% Capacity)"]
    else:
        return ["Red Lot Capacity to Simulate: " + str(red) + " (" + str(round(red*100/carpark_cap['cp10'][1])) + "% Capacity)"], ["White Lot Capacity to Simulate: " + str(white) + " (" + str(round(white*100/carpark_cap['cp10'][0])) + "% Capacity)"]

# Callback to Adjust Red/White Ratio
@callback(
    Output('slider_red_cp10','value',allow_duplicate = True),
    Output('slider_white_cp10','value',allow_duplicate = True),
    Output('slider_red_cp10','max'),
    Output('slider_white_cp10','max'),
    Input('slider_ratio_cp10','value'),
    State('slider_red_cp10','value'),
    State('slider_white_cp10','value'),
    prevent_initial_call = True
)
def change_ratio_cp10(ratio,red_val,white_val):
    to_add_white = ratio - carpark_cap['cp10'][0]
    new_max_white = ratio
    new_max_red = carpark_cap['cp10'][1] - to_add_white

    return new_max_red,new_max_white,new_max_red, new_max_white

# Callback to reset simulation numbers
@callback(
    Output('slider_ratio_cp10','value'),
    Output('slider_red_cp10','value'),
    Output('slider_white_cp10','value'),
    Output('cp_status_cp10','value'),
    Input('reset-modal-cp10','n_clicks'),
)
def reset_cp_params_cp10(clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'reset-modal-cp3' in changed_id:
        return carpark_cap['cp10'][0],carpark_cap['cp10'][1], carpark_cap['cp10'][0], "Open"
    else:
        return dash.no_update,dash.no_update, dash.no_update,dash.no_update

'''4.2 Simulate'''
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

# Callbacks for Simulation Modal Content, Display Arrival Rate Graph for simulation and also the carpark capacities to simulate in percentage
@callback(
    Output(component_id='simulate-modal-contents',component_property='children'),
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
        # Change Header
        if event == "No Event" and month is None:
            if list(args) == list(default_arrivals.values()):
                first = html.B("Empty Simulation")
            else:
                first = html.B("Custom")
        elif event == "No Event":
            if list(args) == list(get_month_arrival_rate(month).values()):
                first = html.B(month_dict[month])
            else:
                first = html.B(month_dict[month] + ' - Custom')
        else:
            if list(args) == list(get_event_arrival_rate(event).values()):
                first = html.B(event)
            else:
                first = html.B(event + ' - Custom')
        
        d = dict(zip(range(24),args))
        graph = html.Div(dcc.Graph(config = {'staticPlot': True},figure = generate_arrival_rate_graph(d,300,300)), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})


        # Compute Capacities for Simulation
        cp3_red_string = "0"
        cp3_white_string = "0"
        if cp3_status == "Open":
            cp3_red_string = str(round(cp3_red_v * 100 / carpark_cap['cp3'][1]))
            cp3_white_string = str(round(cp3_white_v * 100 / carpark_cap['cp3'][0]))

        cp3a_red_string = "0"
        cp3a_white_string = "0"
        if cp3a_status == "Open":
            cp3a_red_string = str(round(cp3a_red_v * 100 / carpark_cap['cp3a'][1]))
            cp3a_white_string = str(round(cp3a_white_v * 100 / carpark_cap['cp3a'][0]))

        cp4_red_string = "0"
        cp4_white_string = "0"
        if cp4_status == "Open":
            cp4_red_string = str(round(cp4_red_v * 100 / carpark_cap['cp4'][1]))
            cp4_white_string = str(round(cp4_white_v * 100 / carpark_cap['cp4'][0]))

        cp5_red_string = "0"
        cp5_white_string = "0"
        if cp5_status == "Open":
            cp5_red_string = str(round(cp5_red_v * 100 / carpark_cap['cp5'][1]))
            cp5_white_string = str(round(cp5_white_v * 100 / carpark_cap['cp5'][0]))

        cp5b_red_string = "0"
        if cp5b_status == "Open":
            cp5b_red_string = str(round(cp5b_red_v * 100 / carpark_cap['cp5b'][1]))


        cp6b_red_string = "0"
        cp6b_white_string = "0"
        if cp6b_status == "Open":
            cp6b_red_string = str(round(cp6b_red_v * 100 / carpark_cap['cp6b'][1]))
            cp6b_white_string = str(round(cp6b_white_v * 100 / carpark_cap['cp6b'][0]))

        cp10_red_string = "0"
        cp10_white_string = "0"
        if cp10_status == "Open":
            cp10_red_string = str(round(cp10_red_v * 100 / carpark_cap['cp10'][1]))
            cp10_white_string = str(round(cp10_white_v * 100 / carpark_cap['cp10'][0]))

        
        # Creating dataframe for carpark capacities and dash table
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



# Callback to open the loading modal
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

# Callback that updates progress-bar during the simulation based on which simulation number the simulation is currently on
@callback(Output("progress-bar", "value"), Trigger("interval", "n_intervals"))
def update_progress(trig):
    global fsc
    value = fsc.get("progress")  # get progress
    return value

# Callback that sets the progress bar to zero when loading modal is closed
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

# Callback to run simulation given user inputs, updating the necessary output values for each carpark and also statistics for the simulation run
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
def simulate_events(hour,cp3_status,cp3a_status,cp4_status,cp5_status,cp5b_status,cp6b_status,cp10_status,clicks, month, event, cp3_red_v, cp3_red_max, cp3_white_v, cp3_white_max,
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
        

        init_time = time.time()


        global outputs
        outputs = {}


        n = 100 #Set n = 100 for Docker Solution, n = 10 for testing and debugging
        for i in range(n):
            current = run_nsim(cap_dict = lots_d_input, lambdas = arrival_rates, n = 1) 
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

        print(outputs)
        
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
        
        time.sleep(1)
        return False,generate_results_modal(outputs),False
    
    else:
        return dash.no_update,dash.no_update,dash.no_update


'''4.3 Outputs'''
#  Callback to display simulation parameters on the left partition after simulation has been completed
@callback(
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

        # Header
        if event == "No Event" and month is None:
            if list(args) == list(default_arrivals.values()):
                first = html.B("Empty Simulation")
            else:
                first = html.B("Custom")
        elif event == "No Event":
            if list(args) == list(get_month_arrival_rate(month).values()):
                first = html.B(month_dict[month])
            else:
                first = html.B(month_dict[month] + ' - Custom')
        else:
            if list(args) == list(get_event_arrival_rate(event).values()):
                first = html.B(event)
            else:
                first = html.B(event + ' - Custom')
        
        d = dict(zip(range(24),args))
        
        # Arrival Rate Graph
        graph = html.Div(dcc.Graph(config = {'staticPlot': True}, figure = generate_arrival_rate_graph(d,300,300)),
                        style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}) 
            
        
        # Computing capacities to display on table
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
            cp3_red_string = str(round(cp3_red_v * 100 / carpark_cap['cp3'][1])) 
            cp3_white_string = str(round(cp3_white_v * 100 / carpark_cap['cp3'][0])) 

        if cp3a_status == "Open":
            cp3a_red_string = str(round(cp3a_red_v * 100 / carpark_cap['cp3a'][1])) 
            cp3a_white_string = str(round(cp3a_white_v * 100 / carpark_cap['cp3a'][0])) 
    
        if cp4_status == "Open":
            cp4_red_string = str(round(cp4_red_v * 100 / carpark_cap['cp4'][1])) 
            cp4_white_string = str(round(cp4_white_v * 100 / carpark_cap['cp4'][0])) 

        if cp5_status == "Open":
            cp5_red_string = str(round(cp5_red_v * 100 / carpark_cap['cp5'][1])) 
            cp5_white_string = str(round(cp5_white_v * 100 / carpark_cap['cp5'][0]))

        if cp5b_status == "Open":
            cp5b_red_string = str(round(cp5b_red_v * 100 /carpark_cap['cp5b'][1]))
        
        if cp6b_status == "Open":
            cp6b_red_string = str(round(cp6b_red_v * 100 / carpark_cap['cp6b'][1]))
            cp6b_white_string = str(round(cp6b_white_v * 100 / carpark_cap['cp6b'][0]))
        
        if cp10_status == "Open":
            cp10_red_string = str(round(cp10_red_v * 100 / carpark_cap['cp10'][1]))
            cp10_white_string = str(round(cp10_white_v * 100 / carpark_cap['cp10'][0]))

        # Creating dataframe and capacities table
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




# Callback to show user what time they are simulating under the adjustment slider for time
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


# Callback to get carpark saturation for each hour when user adjusts the slider bars, occupancy levels will change for each carpark
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
def change_occupancies(disabled,hour):
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


# Toggling results modal
@callback(
    Output('results-modal','is_open'),
    Input('results-button','n_clicks'),
    Input('results-modal-close','n_clicks')
)
def open_results_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'results-button' in changed_id:
        return True
    else:
        return False

# Disables the option to download results when no simulation has been run
@callback(
    Output('results-download-button','disabled'),
    Input('results-slider','disabled')
)
def allow_downloads(disabled):
    return disabled

# Prepares Excel containing simulation results when user clicks on the download button
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
        excel_writer.close()


        return dcc.send_file(excel_writer,"simulation_statistics.xlsx")
    else:
        return None



'''4.4 Reset'''
# Callback for reset all: revert to original settings and carpark state, all simulation results will be wiped, everything will be in clean state
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
        return True, 23, generate_results_modal({}),{'top':'16%', 'left':'27%','background-color':'green'},{'top':'17%', 'left':'32%','background-color':'green'}, {'top':'32%', 'left':'34%','background-color':'green'},{'top':'34%', 'left':'43%','background-color':'green'},{'top':'25.5%', 'left':'42%','background-color':'green'},{'top':'62%', 'left':'62%','background-color':'green'},{'top':'53%', 'left':'84%','background-color':'green'},True,cp_modal("cp3"),cp_modal("cp3a"),cp_modal("cp4"), cp_modal("cp5"),cp_modal("cp5b"),cp_modal("cp6b"),cp_modal("cp10"),'None',generate_arrival_rate_graph(default_arrivals,300,300),default_button,default_button,default_button,default_button,default_button,default_button,default_button,None,"No Event"
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
        return True,cp_modal("cp3"),cp_modal("cp3a"),cp_modal("cp4"), cp_modal("cp5"),cp_modal("cp5b"),cp_modal("cp6b"),cp_modal("cp10")
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



