import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import plotly.express as px
import pandas as pd
import random

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

# Sample Data for Months
month_data_values = [dict(zip(range(0,24),[random.randint(1, 1000) for _ in range(24)])) for i in range(12)]
month_data_keys = range(1,13)
month_data = dict(zip(month_data_keys,month_data_values))

# Sample Data Events
events_data_values = [dict(zip(range(0,24),[random.randint(1, 1000) for _ in range(24)])) for i in range(10)]
events_data = dict(zip(campus_events,events_data_values))

#Helper function to generate arrival rates given month
def generate_arrival_rate_month(x):
    #keys = range(0,24)
    #random_numbers = [random.randint(1, 1000) for _ in range(24)]
    #d = dict(zip(keys,random_numbers))
    #temp = sample_data[sample_data["month"] == x]
    #d = temp.set_index("hour")["delta_nett"].to_dict()
    return month_data[x]

def generate_arrival_rate_event(x):
    #keys = range(0,24)
    #random_numbers = [random.randint(1, 500) for _ in range(24)]
    #d = dict(zip(keys,random_numbers))
    return events_data[x] 

#Helper function to generate plots from dictionary representation
def generate_arrival_graph(d):
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

def cp_modal(cp,a,b,c,d):
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(cp), close_button= False),
        dbc.ModalBody([
            html.B("Occuipied Lots: " + str(a+c) + '/' + str(b+d), id = 'occupied_cp'),
            html.Div("Occuipied Red Lots: " + str(a) + '/' + str(b), style = {'color':'red'}, id = 'occupied_red_cp'),
            html.Div("Occuipied White Lots: " + str(c) + '/' + str(d), id = 'occupied_white_cp'),
            html.Br(),
            html.H4('Simulation Parameters:'),
            html.Div('Carpark Status:'),
            html.Div(dcc.Dropdown(options=['Open','Closed'], id = 'cp-status', value = "Open", clearable = False), style={'margin-bottom':'3%'}),
            html.Div([
            html.Div(html.Div('Adjust Red Lot Capacity:'),style= {'text-align':'center'}),
            html.Div(dcc.Slider(id = "slider_red_cp",min = 0, max = b, step = 1, value = b, marks = None)),
            html.Div(html.Div('Adjust White Lot Capacity:'),style= {'text-align':'center'}),
            html.Div(dcc.Slider(id = "slider_white_cp",min = 0, max = d, step = 1, value = d, marks = None)),
            html.Div(
                [html.B(id = 'to_simulate_red_cp'),
                 html.Br(),
                html.B(id = 'to_simulate_white_cp')]
            )
            ])

        ], style= {'text-align':'center', 'font-size':'19px'}),
        dbc.ModalFooter([
                    dbc.Button('Reset Parameters', id = 'cp-modal-reset',style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}),
                    dbc.Button(
                        "Save and Exit", id="close-cp-modal", style = {'background-color':'#333333', 'border-color':'#000000', 'border-width':'medium', 'font-size':'19px'}
                    )])
    ], id = 'cp-modal', is_open= False, backdrop = False, centered = True)



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
            html.Div(dcc.Graph(id = "arrival-graph",config = {'staticPlot': True},figure = generate_arrival_graph(default_arrivals)),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
            html.Br(),
            dbc.Button('Refine Arrival Rate', id='refine-button', style={'margin-bottom':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            dbc.Button('Reset Parameters', id='reset-button', style={'display':'inline-block','margin-right':'2%', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'}),
            dbc.Button('Simulate', id='simulate-button', style={'display':'inline-block', 'background-color':'#a9a9a9', 'color' : '#000000' ,'border-color':'#000000', 'border-width':'medium', 'font-size':'19px', 'font-weight': 'bold'})
            ], 
            width={'size': 2, 'order': 3},
            style = {'text-align':'center','padding-top':'2%', 'background-color':'#ef7c00'})
            ]),
            html.Div(refine_modal('No Event', default_arrivals), id = 'refine-modal-block'),
            html.Div(cp_modal("CP3",0,100,0,70))
    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})


# Callback for carpark status - determines if users can adjust carpark params
@callback(
    Output('slider_red_cp','disabled'),
    Output('slider_white_cp','disabled'),
    Input('cp-status','value')
)
def show_cp_params(status):
    if status == "Open":
        return False, False
    else:
        return True,True 
    

# Callback for simulation numbers cp
@callback(
    Output('to_simulate_red_cp','children'),
    Output('to_simulate_white_cp','children'),
    Input('cp-status','value'),
    Input('slider_red_cp','value'),
    Input('slider_white_cp','value')
)
def params_to_simulate(status,red,white):
    if status == "Closed":
        return ["Red Lot Occupancy to Simulate: 0"], ["White Lot Occupancy to Simulate: 0"]
    else:
        return ["Red Lot Occupancy to Simulate: " + str(red)], ["White Lot Occupancy to Simulate: " + str(white)]

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


# Callback to toggle cp modal
@callback(
        Output('cp-modal','is_open'),
        Input('cp3','n_clicks'),
        Input("close-cp-modal",'n_clicks')
)
def toggle_refine_modal(n1,n2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if "cp3" in changed_id:
        return True
    else:
        return False
    

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

# Callback to reset modal
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
# Simulation Callbacks
@callback(
    Output(component_id='simulation-contents',component_property='children', allow_duplicate=True),
    Input(component_id='simulate-button', component_property='n_clicks'),
    Input(component_id = 'month-picker', component_property = 'value'),
    Input(component_id = 'event-picker',component_property = 'value'),
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
def cp_simulation(clicks, month, event, *args):
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
        graph = html.Div(dcc.Graph(config = {'staticPlot': True},figure = generate_simulation_graph(d)),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'})

        return [first,html.Br(),graph]
     else:
         return dash.no_update

