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
                poster="https://images.unsplash.com/photo-1554080353-a576cf803bda?auto=format&fit=crop&q=80&w=1000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8cGhvdG98ZW58MHx8MHx8fDA%3D",
                style={'max-width': '100%', 'height': '500px', 'width': '75%', 'display': 'block', 'margin': '0 auto'}
            ),
            href="https://www.youtube.com/watch?v=GsLsBs4oW30",  # Add the actual YouTube video URL
            target="_blank",  # Open the link in a new tab
        )
    ], style={'border': '1px solid #003D7C', 'padding': '10px', 'border-radius': '5px'})
], style={'background-color': 'white', 'padding': '20px'}),

    # Simulation Legend (Centered)
    html.Div([
        html.Div([
            html.H2("Occupancy Rate Legend", style={'color': '#003D7C'}),
            html.Div([
                html.Span("Green: 0-60%: ", style={'color': 'green'}),
                html.Span("Orange: 60-70%: ", style={'color': 'orange'}),
                html.Span("Red: 70-100%", style={'color': 'red'}),
            ]),
            html.Div([
                html.Span("●", style={'color': 'green', 'font-size': '2.2em'}),
                html.Span("●", style={'color': 'orange', 'font-size': '2.2em'}),
                html.Span("●", style={'color': 'red', 'font-size': '2.2em'}),
            ], style={'text-align': 'center'}),
        ], style={'background-color': 'white', 'padding': '20px', 'text-align': 'center'}),
    ]),
    
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
