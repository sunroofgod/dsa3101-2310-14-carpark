import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

#Create Navigation Bar
navbar = dbc.Navbar(
            dbc.Container(
                [
                    # Create Logo and Brand flushed to the left
                    dbc.Row(
                        dbc.Col([
                            html.Img(src=dash.get_asset_url('nus_logo.svg'), height="72px", style={"padding":"10px", 'vertical-align':'middle'}),
                            dbc.NavbarBrand("Parkitect", style = {'font-weight':'bold','font-size':'36px', 'color':'#3A3B3C','padding':'30px','vertical-align':'middle'})
                                ])

                    ),

                    # Create navigation buttons flushed to the right
                    dbc.Row(      
                        dbc.Col(
                            dbc.Nav([
                                dbc.NavItem(dbc.NavLink("Home", href = "/",style ={'color':'#3A3B3C'})),
                                dbc.NavItem(dbc.NavLink("App", href = "/parkapp",style={'color':'#3A3B3C'})),
                                dbc.NavItem(dbc.NavLink("Tutorial", href = "/tutorial",style ={'color':'#3A3B3C'}))
                            ])
                        )
                    )
                ], 
            style = {'font-family': 'Open Sans', 'font-size': '36px'},
            fluid=True
            )
)




app.layout = html.Div(children=[
    navbar,
    dash.page_container
])


if __name__ == '__main__':
    app.run(debug=True)