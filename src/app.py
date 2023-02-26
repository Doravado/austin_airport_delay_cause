# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Create a dash application
app = dash.Dash(__name__)
server = app.server

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read csv file
flight = pd.read_csv('../Airline_Delay_Cause.csv')

# Process data
flight.fillna(1, inplace=True)
flight['date'] = pd.to_datetime(flight[['year', 'month']].assign(DAY=1))
flight[['city', 'state', 'airport_name']] = flight['airport_name'].str.split(',|:', expand=True)
flight['state'] = flight['state'].str.replace(" ", "")
flight['airport_name'] = flight['airport_name'].str[1:]

austin = flight[(flight['city'] == 'Austin') & (flight['state'] == 'TX')]
austin_delay_traffic = austin[['year', 'month', 'carrier_name', 'arr_flights', 'carrier_delay', 'weather_delay',
                               'nas_delay',
                               'security_delay', 'late_aircraft_delay', 'date']]

id_v = ['year', 'month', 'carrier_name', 'arr_flights', 'date']
austin_delay_traffic = pd.melt(austin_delay_traffic,
                               id_vars=id_v,
                               var_name='delay_cause',
                               value_name='delay_minutes')

# Delay cause data
delay_cause_df = austin_delay_traffic[['year', 'carrier_name', 'delay_cause', 'delay_minutes']]

# Annual delay minutes data
annual_delay_df = austin_delay_traffic[['year', 'month', 'carrier_name', 'delay_cause', 'delay_minutes']]

# Holt Winters model data
austin_holt_df = austin[['date', 'carrier_name', 'arr_delay']]


# def plot
def plot_pie(df):
    df['delay_cause'] = df['delay_cause'].map({'late_aircraft_delay': 'Late Aircraft Delay',
                                               'carrier_delay': 'Carrier Delay',
                                               'nas_delay': 'NAS Delay',
                                               'weather_delay': 'Weather_Delay',
                                               'security_delay': 'Security_Delay'})
    pie_chart = px.pie(df, names='delay_cause', values='delay_minutes',
                       labels={'delay_cause': 'Delay Cause', 'delay_minutes': 'Delay Minutes'},
                       color_discrete_sequence=['#2B3856', '#006699', '#0077B5', '#4B9CD3', '#99C1DE'])
    pie_chart.update_layout(title={'text': 'Delay Cause Distribution (Minutes)',
                                   'x': 0.5,
                                   'y': 0.95,
                                   'xanchor': 'center',
                                   'yanchor': 'top'
                                   },
                            legend=dict(title='Delay Cause',
                                        yanchor="top",
                                        y=0.99,
                                        xanchor="left",
                                        x=-0.2
                                        )
                            )
    return pie_chart


def plot_bar(df):
    bar_chart = px.bar(df, x='month', y='delay_minutes',
                       labels={'month': 'Month', 'delay_minutes': 'Delay Minutes'},
                       color_discrete_sequence=['#4B9CD3'])
    bar_chart.update_layout(title={'text': 'Monthly Total Delay Minutes',
                                   'x': 0.5,
                                   'y': 0.95,
                                   'xanchor': 'center',
                                   'yanchor': 'top'
                                   },
                            xaxis=dict(title='Month',
                                       tickmode='linear',
                                       dtick='M1',
                                       tickformat='%b\n%Y'),
                            yaxis_title='Delay Minutes'
                            )
    return bar_chart


def plot_line(df):
    train = df.loc[:'2022']
    model = ExponentialSmoothing(train, seasonal_periods=12, trend='add', seasonal='add')
    fit = model.fit()
    forecast = fit.forecast(12)
    data = pd.concat([train, forecast], axis=1)
    data = data.rename(columns={'arr_delay': 'actual', 0: 'forecast'})

    line_chart = px.line()
    line_chart.add_scatter(x=data.index, y=data['actual'], mode='lines', name='Actual', line_color='#4B9CD3')
    line_chart.add_scatter(x=data.index, y=data['forecast'], mode='lines', name='Forecast')
    line_chart.update_layout(title={'text': 'Total Delay Minutes Over Years & 2023 Forecast',
                                    'x': 0.5,
                                    'y': 0.95,
                                    'xanchor': 'center',
                                    'yanchor': 'top'
                                    },
                             legend=dict(orientation='h',
                                         yanchor='top',
                                         y=0.9,
                                         xanchor='center',
                                         x=0.5
                                         ),
                             xaxis=dict(title='Date',
                                        tickmode='linear',
                                        dtick='M18',
                                        tickformat='%b\n%Y'
                                        ),
                             yaxis_title='Delay Minutes',
                             width=1400,
                             height=500
                             )
    return line_chart


# Create year list
year_list = [{'label': 'All Years', 'value': 'All Years'}]
for item in range(2003, 2023, 1):
    year_list.append({'label': item, 'value': item})

# Create airline list
airline_list = [{'label': 'All Airlines', 'value': 'All Airlines'}]
for item in austin["carrier_name"].value_counts().index:
    airline_list.append({'label': item, 'value': item})

# logo image
logo_src = 'https://dehayf5mhw1h7.cloudfront.net/wp-content/uploads/sites/1304/2020/06/10113836/abia.png'

# Build dashboard layout
app.layout = html.Div(style={'margin': 'auto'},
                      children=[html.Div([html.Img(src=logo_src, alt='Austin Airport Logo',
                                                   style={'vertical-align': 'middle',
                                                          'display': 'inline-block',
                                                          'width': '8%',
                                                          'height': '8%'}
                                                   ),
                                          html.Div([html.H1('Austin Airport Delay Cause Dashboard',
                                                            style={'textAlign': 'center',
                                                                   'color': '#000000',
                                                                   'font-size': 40
                                                                   }
                                                            ),
                                                    html.H3('(Data source: Federal Aviation Administration (2003-2022)',
                                                            style={'textAlign': 'center',
                                                                   'color': '#000000',
                                                                   'font-size': 20
                                                                   }
                                                            )
                                                    ], style={'display': 'inline-block',
                                                              'margin-left': '10px',
                                                              'vertical-align': 'middle'}
                                                   )
                                          ], style={'display': 'flex',
                                                    'align-items': 'center',
                                                    'justify-content': 'center'}
                                         ),
                                html.Br(),
                                html.Br(),
                                html.Div([html.Div([html.Div([html.H2('Year:', style={'margin-right': '2em'})
                                                              ]),
                                                    dcc.Dropdown(id='input-year',
                                                                 options=year_list,
                                                                 placeholder='Select a year',
                                                                 style={'width': '100%', 'text-align': 'center',
                                                                        'padding': '3px',
                                                                        'font-size': '20px'},
                                                                 value='All Years'
                                                                 )
                                                    ], style={'display': 'flex'}
                                                   ),

                                          html.Div([html.Div([html.H2('Airline:', style={'margin-right': '2em'})
                                                              ]),
                                                    dcc.Dropdown(id='input-airline',
                                                                 options=airline_list,
                                                                 placeholder="Select an airline",
                                                                 style={'width': '100%', 'padding': '3px',
                                                                        'font-size': '20px',
                                                                        'text-align-last': 'center'},
                                                                 value='All Airlines'
                                                                 ),
                                                    ], style={'display': 'flex'}
                                                   ),
                                          ]),
                                html.Br(),
                                html.Div([html.Div(dcc.Graph(id='plot1')),  # pie chart, delay cause
                                          html.Div(dcc.Graph(id='plot2'))  # annual delay minutes
                                          ],
                                         style={'display': 'flex'}
                                         ),
                                html.Div(dcc.Graph(id='plot3'))  # holt winters model
                                ],
                      )


@app.callback([Output(component_id='plot1', component_property='figure'),
               Output(component_id='plot2', component_property='figure'),
               Output(component_id='plot3', component_property='figure')
               ],
              [Input(component_id='input-year', component_property='value'),
               Input(component_id='input-airline', component_property='value')
               ]
              )
def get_graph(entered_year, airline_name):
    if (entered_year == 'All Years') and (airline_name == 'All Airlines'):
        pie_data = delay_cause_df.groupby(['delay_cause'], as_index=False)['delay_minutes'].sum()
        bar_data = annual_delay_df.groupby(['month'], as_index=False)['delay_minutes'].sum()
        line_data = austin_holt_df.groupby(['date'])['arr_delay'].sum().resample('MS').mean()

    elif (entered_year == 'All Years') and (airline_name != 'All Airlines'):
        pie_data = delay_cause_df[delay_cause_df['carrier_name'] == airline_name].groupby(
            ['delay_cause'], as_index=False)['delay_minutes'].sum()
        bar_data = annual_delay_df[annual_delay_df['carrier_name'] == airline_name].groupby(
            ['month'], as_index=False)['delay_minutes'].sum()
        line_data = austin_holt_df[austin_holt_df['carrier_name'] == airline_name].groupby(
            ['date'])['arr_delay'].sum().resample('M').mean()

    elif (entered_year != 'All Years') and (airline_name == 'All Airlines'):
        pie_data = delay_cause_df[delay_cause_df['year'] == entered_year].groupby(
            ['delay_cause'], as_index=False)['delay_minutes'].sum()
        bar_data = annual_delay_df[annual_delay_df['year'] == entered_year].groupby(
            ['month'], as_index=False)['delay_minutes'].sum()
        line_data = austin_holt_df.groupby(['date'])['arr_delay'].sum().resample('MS').mean()

    else:
        pie_data = delay_cause_df[
            (delay_cause_df['year'] == entered_year) & (delay_cause_df['carrier_name'] == airline_name)].groupby(
            ['delay_cause'], as_index=False)['delay_minutes'].sum()
        bar_data = annual_delay_df[
            (annual_delay_df['year'] == entered_year) & (annual_delay_df['carrier_name'] == airline_name)].groupby(
            ['month'], as_index=False)['delay_minutes'].sum()
        line_data = austin_holt_df[austin_holt_df['carrier_name'] == airline_name].groupby(
            ['date'])['arr_delay'].sum().resample('M').mean()

    pie_fig = plot_pie(pie_data)
    bar_fig = plot_bar(bar_data)
    line_fig = plot_line(line_data)
    return [pie_fig, bar_fig, line_fig]


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
