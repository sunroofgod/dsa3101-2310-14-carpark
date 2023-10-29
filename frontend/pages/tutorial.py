import dash
from dash import html

dash.register_page(__name__) #signifies homepage

layout = html.Div([
    html.H1("Tutorial page")
])