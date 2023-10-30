import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

dash.register_page(__name__) #signifies homepage

campus_events = ['No Event','First Week New AY', 'Well-Being Day', 'Commencement', 'Examinations', 'Staff WFH Day', 'Rag & Flag Day', 'SuperNova', 'Open Day']

layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div([
                html.B("Currently Simulating:")
            ]
            ),style = {'text-align':'center','background-color':'#003d7c','padding-top':'10px','color':'#FFFFFF'}
            ),
        dbc.Col(html.Img(src=dash.get_asset_url('nus_map.png'), style = {'width':'95%','height':'auto'}),width = 8 ,style = {'display': 'flex', 'justify-content': 'center', 'align-items':'center', 'padding':'10px 0px'}),
        dbc.Col([
            html.Div([html.Div(html.B("Select Date")),
            html.Div(dcc.DatePickerSingle(id='date-picker', date='2023-01-01'))]),
            html.Br(),
            html.Div([html.Div(html.B("Select Time")),
            html.Div(dcc.Input(id="time-picker", type="text", placeholder="hh:mm:ss", style={'text-align':'center', 'width':'150px'}))]),
            html.Br(),
            html.Div([html.B("Select Event"),
            dcc.Dropdown(id = 'event-picker', options=campus_events, value = "No Event", clearable = False, style = {'font-size':'15px'})]),
            html.Br(),
            html.Br(),
            html.Button('Simulate', id='simulate-button'),
            html.Br(),
            html.Br(),
            html.Button('Reset Parameters', id='reset-button')
            ], 
            style = {'text-align':'center','padding-top':'100px', 'background-color':'#ef7c00'})
            ])
    ], fluid=True,  style = {'font-family': 'Open Sans', 'font-size':'19px'})