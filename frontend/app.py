
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Import Open Sans Font for those that is not using it
app = Dash(__name__, use_pages=True, external_stylesheets=['https://fonts.googleapis.com/css?family=Open+Sans:400,600',dbc.themes.BOOTSTRAP])

# CSS styles for navbar
nav_text_default = {'color':'#3A3B3C', 'text-align':'center'}
nav_text_selected = {'color':'#FFFFFF','text-align':'center'}
nav_button_default = {'border-style': 'solid', 'margin-right':'15px','width':'150px','border-radius': '25px','border-width':'medium'}
nav_button_selected = {'border-style': 'solid','margin-right':'15px','width':'150px','border-radius': '25px','background-color':'#333333', 'border-width':'medium'}

# Create a callback to highlight the active navigation button
@app.callback(
    [Output("home_text", "style"),
     Output("app_text", "style"),
     Output("tutorial_text", "style"),
     Output("home_button", "style"),
     Output("app_button", "style"),
     Output("tutorial_button", "style")
     ],
    [Input("url", "pathname")]
)
def highlight_active_button(pathname):
    if pathname == "/":
        return nav_text_selected,nav_text_default,nav_text_default,nav_button_selected,nav_button_default,nav_button_default
    elif pathname == "/parkapp":
        return nav_text_default,nav_text_selected,nav_text_default,nav_button_default,nav_button_selected,nav_button_default
    elif pathname == "/tutorial":
        return nav_text_default,nav_text_default,nav_text_selected,nav_button_default,nav_button_default,nav_button_selected

#Create Navigation Bar
navbar = dbc.Navbar(
            dbc.Container(
                [
                    # Create Logo and Brand flushed to the left
                    dbc.Row(
                        dbc.Col([
                            html.Img(src=dash.get_asset_url('nus_logo.svg'), height="72px", style={"padding":"10px"}),
                            dbc.NavbarBrand("Parkitect", style = {'font-weight':'bold','font-size':'35px', 
                            'color':'#3A3B3C','padding-left':'30px','vertical-align':'middle'})
                                ])

                    ),

                    # Create navigation buttons flushed to the right
                    dbc.Row(      
                        dbc.Col(
                            dbc.Nav([
                                dbc.NavItem(dbc.NavLink("Home", href = "/", id = "home_text"), id = "home_button"),
                                dbc.NavItem(dbc.NavLink("App", href = "/parkapp", id = "app_text"),id = "app_button"),
                                dbc.NavItem(dbc.NavLink("Tutorial", href = "/tutorial", id="tutorial_text"), id = "tutorial_button")
                            ])
                        )
                    )
                ], 
            style = {'font-family': 'Open Sans', 'font-size': '18px', 'height':'auto','background-color':'#d3d3d3'},
            fluid=True
            ), style = {'padding':'0px'} #set to 0 else will have white space
)


app.layout = html.Div(children=[
    dcc.Location(id = "url"),
    navbar,
    dash.page_container,
], style = {'zoom':'75%'}) # Set zoom to 75% to acommodate small screens


if __name__ == '__main__':
    # Run below line if dockerizing
    app.run(host='0.0.0.0', port="8050", debug=False)
    # Run below line if testing and developing
    #app.run(host='http://127.0.0.1/', port="8050", debug=True)