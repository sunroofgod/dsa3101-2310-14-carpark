import dash
from dash import html, dcc

dash.register_page(__name__) #signifies homepage

layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Carpark Simulation Tutorial", style={'text-align': 'center', 'color': 'white'}),
        ], style={'background-image': 'radial-gradient(circle, #EF7C00, #003D7C)', 'padding': '20px'}),
    ], style={'position': 'relative', 'z-index': '1', 'margin-bottom': '-20px'}),
    
    html.Br(),
    
    
    # Video Tutorial Space
    html.Div([
    html.H2("Tutorial Video", style={'color': '#003D7C', 'text-align': 'center'}),
    # Include your tutorial video here with a preview image and poster
    html.Div([
        html.A(
            html.Video(
                src="https://www.youtube.com/embed/GsLsBs4oW30",
                controls=True,
                poster="assets/tutorial_pic.png",
                style={'max-width': '100%', 'height': '500px', 'width': '75%', 'display': 'block', 'margin': '0 auto'}
            ),
            href="https://www.youtube.com/watch?v=GsLsBs4oW30",  # Add the actual YouTube video URL
            target="_blank",  # Open the link in a new tab
        )
    ], style={'border': '1px solid #003D7C', 'padding': '10px', 'border-radius': '5px'})
], style={'background-color': 'white', 'padding': '20px'}),

    
    # Additional Content (Centered)
    html.Div([
        html.Div([
            html.H2("Carpark Simulation Information", style={'color': '#003D7C'}),
            html.P("In this tutorial, you will learn about carpark simulation and related concepts..."),
          
        ], style={'background-color': 'white', 'padding': '20px', 'text-align': 'center'}),
    ]),
    
    # Footer
    html.Div([
        html.P("For any questions or feedback, please contact us at hanehneh@gmail.com", style={'color': 'white'}),
    ], style={'background-color': '#003D7C', 'padding': '20px', 'text-align': 'center'}),
])