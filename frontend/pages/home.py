import dash
from dash import html

dash.register_page(__name__, path = '/') #signifies homepage

container = html.Div(
    [
        html.H1("PARKitect:", style={'font-weight': 'bold', 'color': 'blue', 'display': 'inline'}),
        html.H1(" Designing Smart Parking Solutions", style={'font-weight': 'bold', 'color': 'orange', 'display': 'inline'}),
        html.H2("Your one-stop NUS parking simulation system", style={'font-weight': 'bold'}),
        html.Br(),
        html.P("*Red Lots - Strictly for staff only", style={'margin-bottom': '0px', "color": "red"}),
        html.P("*White Lots - For everybody", style={'margin-bottom': '0px'})
    ],
    style={
        'text-align': 'center',
        'border': '5px none',  # Rectangular border
        'border-radius': '15px',  # Adjust the border-radius to make the corners rounded
        'padding': '20px'  # Add some padding for spacing between the text and the border
    }
)

layout = html.Div(
    [
        container
    ],
    # Centralize the container vertically and horizontally
    style={'position': 'absolute', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)', 'white-space': 'nowrap'}
)

