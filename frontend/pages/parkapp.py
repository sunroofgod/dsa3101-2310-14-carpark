import dash
from dash import html

dash.register_page(__name__) #signifies homepage

layout = html.Div([
    html.Img(src=dash.get_asset_url('nus_map.png'), style = {'width':'65%','height':'auto'})
], style = {'display': 'flex', 'justify-content': 'center', 'align-items':'center','padding':'10px'})