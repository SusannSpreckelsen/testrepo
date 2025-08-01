# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in spacex_df['Launch Site'].unique():
    dropdown_options.append({'label': site, 'value': site})


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('V2 - SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                #dcc.Dropdown(id='site-dropdown',  options=[{'label': 'All Sites', 'value': 'ALL'},{'label': 'site1', 'value': 'site1'}, ...])
                                dcc.Dropdown(id='site-dropdown',
                                    options=dropdown_options,
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True
                                ),
                                
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                # NEU: Range Slider zur Auswahl des Payload-Bereichs
                                html.Div([
                                html.H2("Payload Mass (kg)", style={'textAlign': 'center'}),
                                dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        value=[min_payload, max_payload], # Startwerte: min und max aus den Daten
                                        marks={i: f'{i}' for i in range(0, 10001, 1000)} # Beschriftungen für den Schieberegler
                                    ),
                                ], style={'width': '80%', 'padding': '20px', 'margin': 'auto'}), # Zentriert den Slider



                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    """
    Diese Funktion generiert ein Pie Chart basierend auf der ausgewählten Startseite.
    Wenn 'ALL' ausgewählt ist, zeigt sie die Erfolgsraten für alle Starts.
    Wenn ein spezifischer Startplatz ausgewählt ist, zeigt sie die Erfolgsraten nur für diesen Platz.
    """
    if entered_site == 'ALL':
        # Wenn 'ALL' ausgewählt ist, verwenden wir das gesamte DataFrame.
        # px.pie zählt standardmäßig die Vorkommen der Werte in der 'names'-Spalte.
        # Hier ist 'class' die Spalte, die 0 (Failed) oder 1 (Success) enthält.
        fig = px.pie(spacex_df,
                     names='class',
                     title='Total Success and Failed Launches (All Sites)',
                     # Beschriftungen für die Segmente des Pie Charts
                     labels={0: 'Failed Launches', 1: 'Successful Launches'},
                     color='class', # Farbgebung basierend auf der Klasse
                     color_discrete_map={0: 'lightcoral', 1: 'mediumseagreen'} # Spezifische Farben
                    )
        return fig
    else:
        # Wenn ein spezifischer Startplatz ausgewählt ist, filtern wir das DataFrame.
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Erstelle ein Pie Chart für diesen spezifischen Startplatz
        # Zeige die Anzahl der erfolgreichen (class=1) und fehlgeschlagenen (class=0) Starts für den gefilterten Datensatz.
        fig = px.pie(filtered_df,
                     names='class',
                     title=f'Success and Failed Launches for {entered_site}',
                     labels={0: 'Failed Launches', 1: 'Successful Launches'},
                     color='class', # Farbgebung basierend auf der Klasse
                     color_discrete_map={0: 'lightcoral', 1: 'mediumseagreen'} # Spezifische Farben
                    )
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    """
    Diese Funktion generiert ein Scatter Plot basierend auf der ausgewählten Startseite
    und dem ausgewählten Nutzlastbereich.
    """
    low, high = payload_range # Entpackt den Bereich aus dem Slider-Wert

    # Filtert das DataFrame basierend auf dem Nutzlastbereich
    # Wir filtern immer zuerst nach Payload, egal ob ALL oder spezifischer Site
    payload_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                                    (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        # Wenn 'ALL' ausgewählt ist, verwenden wir das nach Payload gefilterte DataFrame.
        fig = px.scatter(
            payload_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category', # Farbt die Punkte nach Booster-Version
            title=f'Payload vs. Outcome for All Sites (Payload: {low}-{high} kg)',
            labels={'class': 'Mission Outcome (0=Failed, 1=Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
        return fig
    else:
        # Wenn ein spezifischer Startplatz ausgewählt ist, filtern wir zusätzlich nach diesem Platz.
        filtered_df_by_site_and_payload = payload_filtered_df[payload_filtered_df['Launch Site'] == entered_site]

        fig = px.scatter(
            filtered_df_by_site_and_payload,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category', # Farbt die Punkte nach Booster-Version
            title=f'Payload vs. Outcome for {entered_site} (Payload: {low}-{high} kg)',
            labels={'class': 'Mission Outcome (0=Failed, 1=Success)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
        )
        return fig





# Run the app
if __name__ == '__main__':
    app.run(port = 8080)

