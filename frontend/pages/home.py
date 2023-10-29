import dash
from dash import html

dash.register_page(__name__, path = '/') #signifies homepage

layout = html.Div(
    [
    html.H1("PARKitect: Designing Smart Parking Solutions"),
    html.H2("Your one-stop NUS parking simulation system"),
    html.Br(),
    html.P("*Red Lots - Strictly for staff only", style = {'margin-bottom':'0px', "color": "red"}),
    html.P("*White Lots - For everybody", style= {'margin-bottom':'0px'})
    ], 
    # Centralise text chunk vertically and horizontally
    style={'font-family': 'Open Sans','text-align':'center','position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)','white-space': 'nowrap'}
    )

