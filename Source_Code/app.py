import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


df = pd.read_csv('merged_data.csv')
df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

# Create derived features
df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
df['pickup_date'] = df['tpep_pickup_datetime'].dt.date

# Define categorical and numerical columns
categorical_columns = ['VendorID', 'RatecodeID', 'payment_type']
numerical_columns = [
    'passenger_count', 'trip_distance', 'fare_amount',
    'extra', 'mta_tax', 'tip_amount', 'tolls_amount',
    'total_amount', 'PRCP'
]


LIGHT_THEME = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'card': '#ffffff',
    'subcontainer': '#ecf0f1',
    'header': '#ffffff'
}

DARK_THEME = {
    'background': '#2c3e50',
    'text': '#ecf0f1',
    'card': '#34495e',
    'subcontainer': '#34495e',
    'header': '#34495e'
}


app = dash.Dash(__name__)
app.title = "NYC Taxi Analysis Dashboard"

app.layout = html.Div([
    # Header with Title and Theme Toggle
    html.Div(
        id='header',
        children=[
            html.H1("NYC Taxi Trip Analysis Dashboard", style={'textAlign': 'center'}),
            html.Div([
                html.Label("Theme: ", style={'marginRight': '10px'}),
                dcc.RadioItems(
                    id='theme-toggle',
                    options=[
                        {'label': 'Light', 'value': 'light'},
                        {'label': 'Dark', 'value': 'dark'}
                    ],
                    value='light',
                    labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                )
            ], style={'textAlign': 'center', 'padding': '10px'})
        ]
    ),

    
    dcc.Tabs(
        id='tabs',
        value='overview',
        children=[
            # --------------- OVERVIEW TAB ---------------
            dcc.Tab(label='Overview', value='overview', children=[
                html.Div(
                    id='overview-container',
                    children=[
                        # Key Metrics Row
                        html.Div([
                            html.Div([
                                html.H4("Total Trips"),
                                html.H2(id='total-trips')
                            ], className='metric-card'),
                            html.Div([
                                html.H4("Average Fare"),
                                html.H2(id='avg-fare')
                            ], className='metric-card'),
                            html.Div([
                                html.H4("Average Trip Distance"),
                                html.H2(id='avg-distance')
                            ], className='metric-card')
                        ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),

                        # Hour Slider Filter
                        html.Div([
                            html.Label('Filter by Pickup Hour:', style={'fontSize': '18px', 'fontWeight': 'bold'}),
                            dcc.RangeSlider(
                                id='hour-slider',
                                min=0,
                                max=23,
                                step=1,
                                value=[0, 23],
                                marks={i: str(i) for i in range(0, 24, 2)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], style={'width': '90%', 'padding': '20px', 'margin': 'auto'}),

                        # Single Variable Analysis
                        html.Div([
                            html.Div([
                                html.Label('Select Variable for Analysis:', style={'fontSize': '18px'}),
                                dcc.Dropdown(
                                    id='variable-selector',
                                    options=[
                                        {'label': col, 'value': col} 
                                        for col in categorical_columns + numerical_columns
                                    ],
                                    value='fare_amount',
                                    style={'width': '100%', 'marginBottom': '20px'}
                                ),
                                html.Label('Chart Orientation:', style={'fontSize': '18px'}),
                                dcc.RadioItems(
                                    id='orientation-selector',
                                    options=[
                                        {'label': 'Vertical', 'value': 'v'},
                                        {'label': 'Horizontal', 'value': 'h'}
                                    ],
                                    value='v',
                                    labelStyle={'display': 'inline-block', 'marginRight': '10px'},
                                    style={'marginBottom': '20px'}
                                )
                            ], style={'width': '25%', 'padding': '20px'}),
                            
                            html.Div([
                                dcc.Graph(id='single-variable-chart'),
                                html.Div(id='single-variable-description', style={'padding': '10px', 'fontSize': '16px'})
                            ], style={'width': '70%', 'padding': '20px'})
                        ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start', 'marginBottom': '40px'}),

                        # Key Insights / Data Storytelling
                        html.Div([
                            html.H3("Key Insights", style={'marginTop': '20px'}),
                            html.Ul([
                                html.Li("Peak pickup hours might be around late afternoon and early evening."),
                                html.Li("When precipitation (PRCP) is higher, trip distances or fares may vary."),
                                html.Li("The average fare hovers around $14, but a majority of trips remain below $25."),
                                html.Li("VendorID distribution suggests that the majority of trips come from one major provider."),
                            ], style={'fontSize': '16px', 'lineHeight': '1.8'})
                        ], id='insights-container', style={'margin': '20px'})
                    ]
                )
            ]),

            # --------------- RELATIONSHIP ANALYSIS TAB ---------------
            dcc.Tab(label='Relationship Analysis', value='relationship', children=[
                html.Div(
                    id='relationship-container',
                    children=[
                        html.H2("Relationship Analysis", style={'textAlign': 'center', 'margin': '20px'}),
                        
                        # Scatter Plot Controls
                        html.Div([
                            html.Div([
                                html.Label('Select Variable A:', style={'fontSize': '18px'}),
                                dcc.Dropdown(
                                    id='var-a-selector',
                                    options=[{'label': col, 'value': col} for col in numerical_columns],
                                    value='trip_distance',
                                    style={'width': '100%', 'marginBottom': '20px'}
                                )
                            ], style={'width': '30%', 'padding': '10px'}),
                            
                            html.Div([
                                html.Label('Select Variable B:', style={'fontSize': '18px'}),
                                dcc.Dropdown(
                                    id='var-b-selector',
                                    options=[{'label': col, 'value': col} for col in numerical_columns],
                                    value='fare_amount',
                                    style={'width': '100%', 'marginBottom': '20px'}
                                )
                            ], style={'width': '30%', 'padding': '10px'}),
                            
                            html.Div([
                                html.Label('Assign Variable A to:', style={'fontSize': '18px'}),
                                dcc.RadioItems(
                                    id='axis-assignment',
                                    options=[
                                        {'label': 'X-Axis', 'value': 'x'},
                                        {'label': 'Y-Axis', 'value': 'y'}
                                    ],
                                    value='x',
                                    labelStyle={'display': 'block', 'marginBottom': '5px'}
                                )
                            ], style={'width': '30%', 'padding': '10px'})
                        ], style={'display': 'flex', 'justifyContent': 'space-around'}),
                        
                        # Scatter Plot
                        dcc.Graph(id='scatter-plot'),
                        html.Div(
                            "This scatter plot shows the relationship between the selected variables. "
                            "Hover over the points to see detailed information, and note the color coding that "
                            "indicates precipitation (PRCP) levels, which may impact trip characteristics.",
                            style={'padding': '20px', 'fontSize': '16px', 'textAlign': 'center'}
                        )
                    ]
                )
            ]),

            # --------------- TIME SERIES ANALYSIS TAB ---------------
            dcc.Tab(label='Time Series Analysis', value='timeseries', children=[
                html.Div(
                    id='timeseries-container',
                    children=[
                        html.H2("Time Series Analysis", style={'textAlign': 'center', 'margin': '20px'}),
                        
                        # Dropdown to select metric to plot over time
                        html.Div([
                            html.Label('Select Metric:', style={'fontSize': '18px'}),
                            dcc.Dropdown(
                                id='timeseries-metric',
                                options=[
                                    {'label': 'Total Trips', 'value': 'trips'},
                                    {'label': 'Average Fare', 'value': 'fare'},
                                    {'label': 'Average Trip Distance', 'value': 'distance'}
                                ],
                                value='trips',
                                style={'width': '50%', 'margin': 'auto', 'marginBottom': '20px'}
                            )
                        ]),
                        
                        # Time Series Chart
                        dcc.Graph(id='timeseries-chart'),
                        html.Div(
                            "The time series analysis above shows how the selected metric changes over days. "
                            "This helps identify trends, peak days, or anomalies in the data.",
                            style={'padding': '20px', 'fontSize': '16px', 'textAlign': 'center'}
                        )
                    ]
                )
            ])
        ]
    )
], id='main-div')



@app.callback(
    [
        Output('main-div', 'style'),
        Output('header', 'style'),
        Output('overview-container', 'style'),
        Output('relationship-container', 'style'),
        Output('timeseries-container', 'style')
    ],
    [Input('theme-toggle', 'value')]
)
def update_theme(theme):
    """
    Dynamically updates the CSS for the main container, header,
    and each tab container to reflect the chosen theme.
    """
    if theme == 'dark':
        main_style = {
            'fontFamily': 'Arial',
            'backgroundColor': DARK_THEME['background'],
            'color': DARK_THEME['text']
        }
        header_style = {
            'backgroundColor': DARK_THEME['header'],
            'color': DARK_THEME['text'],
            'padding': '10px'
        }
        container_style = {
            'backgroundColor': DARK_THEME['subcontainer'],
            'color': DARK_THEME['text'],
            'borderRadius': '10px',
            'padding': '10px'
        }
    else:
        main_style = {
            'fontFamily': 'Arial',
            'backgroundColor': LIGHT_THEME['background'],
            'color': LIGHT_THEME['text']
        }
        header_style = {
            'backgroundColor': LIGHT_THEME['header'],
            'color': LIGHT_THEME['text'],
            'padding': '10px'
        }
        container_style = {
            'backgroundColor': LIGHT_THEME['subcontainer'],
            'color': LIGHT_THEME['text'],
            'borderRadius': '10px',
            'padding': '10px'
        }
    
    return main_style, header_style, container_style, container_style, container_style



@app.callback(
    [Output('tabs', 'style'), Output('tabs', 'colors')],
    [Input('theme-toggle', 'value')]
)
def update_tabs_style(theme):
    """
    Dynamically style the Tabs. 
    - 'style' controls the outer tab container's appearance (text color, background).
    - 'colors' controls the border, primary (selected tab), and background colors.
    """
    if theme == 'dark':
        # Dark mode
        tabs_style = {
            'height': '44px',
            'backgroundColor': DARK_THEME['header'],   # or #2c3e50
            'color': DARK_THEME['text']
        }
        tabs_colors = {
            'border': DARK_THEME['header'],  # border color
            'primary': '#2980b9',            # highlight color for selected tab
            'background': DARK_THEME['header']
        }
    else:
        # Light mode
        tabs_style = {
            'height': '44px',
            'backgroundColor': LIGHT_THEME['header'],
            'color': LIGHT_THEME['text']
        }
        tabs_colors = {
            'border': LIGHT_THEME['header'],
            'primary': '#3498db',
            'background': LIGHT_THEME['header']
        }
    
    return tabs_style, tabs_colors


@app.callback(
    [
        Output('variable-selector', 'style'),
        Output('var-a-selector', 'style'),
        Output('var-b-selector', 'style'),
        Output('timeseries-metric', 'style')
    ],
    [Input('theme-toggle', 'value')]
)
def update_all_dropdown_styles(theme):
    """
    Ensures dropdown backgrounds and text are visible in both light and dark modes.
    """
    if theme == 'dark':
        dropdown_style = {'backgroundColor': '#34495e', 'color': '#ecf0f1'}
        return (dropdown_style, dropdown_style, dropdown_style, dropdown_style)
    else:
        dropdown_style = {'backgroundColor': '#ffffff', 'color': '#2c3e50'}
        return (dropdown_style, dropdown_style, dropdown_style, dropdown_style)



@app.callback(
    [Output('total-trips', 'children'),
     Output('avg-fare', 'children'),
     Output('avg-distance', 'children')],
    [Input('hour-slider', 'value')]
)
def update_metrics(hour_range):
    """
    Updates the summary metrics (Total Trips, Average Fare, and Average Distance)
    based on the current pickup hour filter.
    """
    filtered_df = df[(df['pickup_hour'] >= hour_range[0]) & (df['pickup_hour'] <= hour_range[1])]
    total_trips = len(filtered_df)
    avg_fare = f"${filtered_df['fare_amount'].mean():.2f}" if total_trips > 0 else "$0.00"
    avg_distance = f"{filtered_df['trip_distance'].mean():.2f} mi" if total_trips > 0 else "0.00 mi"
    return total_trips, avg_fare, avg_distance



@app.callback(
    [Output('single-variable-chart', 'figure'),
     Output('single-variable-description', 'children')],
    [
        Input('variable-selector', 'value'),
        Input('orientation-selector', 'value'),
        Input('hour-slider', 'value'),
        Input('theme-toggle', 'value')
    ]
)
def update_single_variable_chart(selected_var, orientation, hour_range, theme):
    """
    Displays either a bar chart (for categorical variables) or a histogram (for numerical variables),
    with orientation toggle and the current theme for styling.
    """
    filtered_df = df[(df['pickup_hour'] >= hour_range[0]) & (df['pickup_hour'] <= hour_range[1])]
    if selected_var is None or filtered_df.empty:
        return go.Figure(), "No data available for the selected range."
    
    # Prepare the figure
    if selected_var in categorical_columns:
        value_counts = filtered_df[selected_var].value_counts()
        if orientation == 'v':
            fig = go.Figure(go.Bar(
                x=value_counts.index,
                y=value_counts.values,
                marker_color='#3498db'
            ))
        else:
            fig = go.Figure(go.Bar(
                y=value_counts.index,
                x=value_counts.values,
                orientation='h',
                marker_color='#3498db'
            ))
        description = f"This bar chart shows the frequency distribution of '{selected_var}'."
    else:
        # For numerical variable, create a histogram
        if orientation == 'v':
            fig = px.histogram(filtered_df, x=selected_var, nbins=30, color_discrete_sequence=['#2ecc71'])
        else:
            fig = px.histogram(filtered_df, y=selected_var, nbins=30, color_discrete_sequence=['#2ecc71'])
        description = f"This histogram displays the distribution of '{selected_var}' over 30 equi-width bins."
    
    # Set chart template based on theme
    if theme == 'dark':
        fig.update_layout(template='plotly_dark')
    else:
        fig.update_layout(template='plotly_white')
    
    fig.update_layout(
        title=f'Distribution of {selected_var}',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig, description



@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('var-a-selector', 'value'),
        Input('var-b-selector', 'value'),
        Input('axis-assignment', 'value'),
        Input('hour-slider', 'value'),
        Input('theme-toggle', 'value')
    ]
)
def update_scatter_plot(var_a, var_b, axis_assignment, hour_range, theme):
    """
    Creates a scatter plot with color-coded PRCP and a trendline.
    Users choose which variable is on the x-axis vs y-axis.
    """
    filtered_df = df[(df['pickup_hour'] >= hour_range[0]) & (df['pickup_hour'] <= hour_range[1])]
    if var_a is None or var_b is None or filtered_df.empty:
        return go.Figure()
    
    if axis_assignment == 'x':
        x_var, y_var = var_a, var_b
    else:
        x_var, y_var = var_b, var_a
    
    fig = px.scatter(
        filtered_df, 
        x=x_var, 
        y=y_var, 
        color='PRCP',
        opacity=0.7,
        trendline="ols",
        trendline_color_override="red",
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_data={x_var: True, y_var: True, 'PRCP': True}
    )
    
    # Update layout for theme
    if theme == 'dark':
        fig.update_layout(template='plotly_dark')
    else:
        fig.update_layout(template='plotly_white')
    
    fig.update_layout(
        title=f'Relationship between {x_var} and {y_var}',
        margin=dict(l=40, r=40, t=40, b=40),
        coloraxis_colorbar=dict(title="Precipitation (PRCP)")
    )
    return fig


@app.callback(
    Output('timeseries-chart', 'figure'),
    [
        Input('timeseries-metric', 'value'),
        Input('theme-toggle', 'value')
    ]
)
def update_timeseries(metric, theme):
    """
    Plots a line chart of the chosen metric (Total Trips, Average Fare, or Average Distance)
    grouped by pickup_date.
    """
    # Group by pickup_date
    df_daily = df.groupby('pickup_date').agg({
        'fare_amount': 'mean',
        'trip_distance': 'mean',
        'tpep_pickup_datetime': 'count'
    }).rename(columns={'tpep_pickup_datetime': 'trips'}).reset_index()
    
    # Choose the appropriate metric
    if metric == 'trips':
        fig = px.line(df_daily, x='pickup_date', y='trips', markers=True,
                      color_discrete_sequence=['#e74c3c'])
        y_title = "Total Trips"
    elif metric == 'fare':
        fig = px.line(df_daily, x='pickup_date', y='fare_amount', markers=True,
                      color_discrete_sequence=['#27ae60'])
        y_title = "Average Fare ($)"
    else:  # metric == 'distance'
        fig = px.line(df_daily, x='pickup_date', y='trip_distance', markers=True,
                      color_discrete_sequence=['#2980b9'])
        y_title = "Average Trip Distance (mi)"
    
    # Update layout for theme
    if theme == 'dark':
        fig.update_layout(template='plotly_dark')
    else:
        fig.update_layout(template='plotly_white')
    
    fig.update_layout(
        title=f"{y_title} Over Time",
        xaxis_title="Date",
        yaxis_title=y_title,
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig



app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>NYC Taxi Analysis</title>
        {%favicon%}
        {%css%}
        <style>
            /* Metric cards styling */
            .metric-card {
                background-color: inherit;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                width: 200px;
                margin: 10px;
            }
            .metric-card h4 {
                margin: 0;
                font-weight: normal;
            }
            .metric-card h2 {
                margin: 10px 0 0 0;
                font-size: 28px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server()