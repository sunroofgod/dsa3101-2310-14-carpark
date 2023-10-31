import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__) #signifies homepage

campus_events = ['No Event','First Week New AY', 'Well-Being Day', 'Commencement', 'Examinations', 'Staff WFH Day', 'Rag & Flag Day', 'SuperNova', 'Open Day']
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

#html.Div('●', id='cp3', style={'position': 'absolute', 'top': '20px', 'left': '210px', 'color': 'lightgreen', 'font-size': '90px'}),

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div([
                html.B("Currently Simulating:")
            ]
            ),style = {'text-align':'center','background-color':'#003d7c','padding-top':'2vh','color':'#FFFFFF'}
            ),
        dbc.Col(
            html.Div([
            html.Div(html.Img(src=dash.get_asset_url('nus_map.png'), style={'width': '100%', 'height': 'auto'}), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
            html.Div([
                html.Button('100', id='cp3', className = 'cp-button', style = {'top':'16%', 'left':'27%'}),
                html.Div('CP3', style = {'position': 'absolute', 'top': '12%', 'left': '27.7%', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                #html.Div('●', id='cp3a', style={'position': 'absolute', 'top': '40px', 'left': '250px', 'color': 'lightgreen', 'font-size': '90px'}),
                #html.Div('CP3A', style = {'position': 'absolute', 'top': '70px', 'left': '255px', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                #html.Div('●', id='cp4', style={'position': 'absolute', 'top': '110px', 'left': '260px', 'color': 'lightgreen', 'font-size': '90px'}),
                #html.Div('CP4', style = {'position': 'absolute', 'top': '200px', 'left': '270px', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                #html.Div('●', id='cp5', style={'position': 'absolute', 'top': '120px', 'left': '330px', 'color': 'lightgreen', 'font-size': '90px'}),
                #html.Div('CP5', style = {'position': 'absolute', 'top': '210px', 'left': '340px', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                #html.Div('●', id='cp5b', style={'position': 'absolute', 'top': '80px', 'left': '310px', 'color': 'lightgreen', 'font-size': '90px'}),
                #html.Div('CP5B', style = {'position': 'absolute', 'top': '110px', 'left': '315px', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                html.Div('●', id='cp6b', style={'position': 'absolute', 'bottom': '80px', 'right': '250px', 'color': 'lightgreen', 'font-size': '90px'}),
                html.Div('CP6B', style = {'position': 'absolute', 'bottom': '95px', 'right': '255px', 'font-weight': 'bold'}),
                ]
                ),
            html.Div([
                html.Div('●', id='cp10', style={'position': 'absolute', 'bottom': '162px', 'right': '130px', 'color': 'lightgreen', 'font-size': '90px'}),
                html.Div('CP10', style = {'position': 'absolute', 'bottom': '240px', 'right': '135px', 'font-weight': 'bold'}),
                ]
                ),
                ],
                style={'position': 'relative'}
            ),
            width=8,
            style= {'padding': '0px'}
            ),
        dbc.Col([
            html.Div([html.Div(html.B("Select Month")),
            html.Div(dcc.Dropdown(id = 'event-picker', options=months, value = "January", clearable = False ))]),
            html.Br(),
            html.Div([html.Div(html.B("Select Event")),
            html.Div(dcc.Dropdown(id = 'event-picker', options=campus_events, value = "No Event", clearable = False))]),
            html.Br(),
            html.Br(),
            html.Button('Simulate', id='simulate-button'),
            html.Br(),
            html.Br(),
            html.Button('Reset Parameters', id='reset-button')
            ], 
            style = {'text-align':'center','padding-top':'12%', 'background-color':'#ef7c00'})
            ])
    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})