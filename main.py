# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:16:33 2021
@author: linds
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import geojson
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

with open('data/pa_counties.json') as f:
    gj = geojson.load(f)

df = pd.read_csv('data/2020_2022_counties_results.csv')

available_parties = list(df['Party'].unique())
available_parties.remove('All')
available_indicators = df['Office'].unique()
available_years = df['Year'].unique()

df_graph_empty = pd.DataFrame(columns=['DistrictNumber', 'x_votes', 'y_votes'])
df_second=pd.DataFrame(columns=['first', 'second'])

row= html.Div([
    html.Div(children=[
        html.H6("First set of results"),
        html.Label("Select Office:"),
        dcc.Dropdown(
            id='office_id',
            options=[{'label': i, 'value': i} for i in available_indicators]
            ),
        html.Br(),
        html.Label("Select Party:"),
        dcc.Dropdown(
            id='party_id',
            options=[{'label': i, 'value': i} for i in available_parties]
            ),
        html.Br(),
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year_id',
            options=[{'label': i, 'value': i} for i in available_years]
            )
        ], style={'width': '20%', 'display': 'inline-block', 'padding':10, 'flex':1}),
    html.Div([
        html.Label("Comparison?"),
        dcc.RadioItems(
            id='comparator',
            options=['Yes', 'No'],
            value='No'
            )
        ], style={'width': '20%', 'display': 'inline-block', 'padding':10, 'flex':1, 'align':'center'}),
    html.Div(children=[
        html.H6("Second set of results"),
        html.Label("Select Office:"),
        dcc.Dropdown(
            id='office_id2',
            options=[{'label': i, 'value': i} for i in available_indicators]
        ),
        html.Br(),
        html.Label("Select Party:"),
        dcc.Dropdown(
            id='party_id2',
            options=[{'label': i, 'value': i} for i in available_parties]
        ),
        html.Br(),
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year_id2',
            options=[{'label': i, 'value': i} for i in available_years]
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding': 10, 'flex': 1}),
    html.Hr(),

    dcc.Graph(id='indicator_graphic'),

    dcc.Graph(id='second_graphic')], style={'width': '60%', 'display': 'block', 'padding': 10, 'flex': 1})

app.layout = dbc.Container(row, fluid=True)

### Update the Party options after selecting an office on the left.
@app.callback(Output('party_id', 'options'),
              Input('office_id', 'value'))
def update_available_parties(office_id):
    available_parties_current=df.loc[df.Office==office_id]["Party"].unique()
    return [{'label': i, 'value': i} for i in available_parties_current]

### Update the Year options after selecting an office on the left.
@app.callback(Output('year_id', 'options'),
              Input('office_id', 'value'))
def update_available_years(office_id):
    available_years_current=df.loc[df.Office==office_id]["Year"].unique()
    return [{'label': i, 'value': i} for i in available_years_current]

### Update the right column if comparison selected
@app.callback(Output('office_id2', 'options'),
              Output('party_id2', 'options'),
              Output('year_id2', 'options'),
              Input('comparator', 'value'),
              Input('office_id2', 'value'))
def update_comparator_column (comparator, office_id2):
    if comparator=='Yes':
        available_parties_current = available_parties
        available_indicators_current = df['Office'].unique()
        available_years_current=df.loc[df.Office==office_id2]["Year"].unique()
        return [{'label': i, 'value': i} for i in available_indicators_current], [{'label': i, 'value': i} for i in available_parties_current], [{'label': i, 'value': i} for i in available_years_current]
    else:
        return {'label': "N/A"}, {'label': "N/A"}, {'label': "N/A"}



@app.callback(Output('indicator_graphic', 'figure'),
              Output('second_graphic', 'figure'),
              Input('office_id', 'value'),
              Input('party_id', 'value'),
              Input('year_id', 'value'),
              Input('comparator', 'value'),
              Input('office_id2', 'value'),
              Input('party_id2', 'value'),
              Input('year_id2', 'value'),
              )

def update_graph(office_id, party_id, year_id,
                 comparator,
                 office_id2, party_id2, year_id2
                ):
    # setup a dataframe that will be graphed
    df_graph = df[df['Party'] ==
                              party_id].loc[df['Office'] ==
                                               office_id].loc[df['Year'] ==
                                                                      year_id]
    if comparator=='Yes':
        df_graph2=df[df['Party'] ==
                              party_id2].loc[df['Office'] ==
                                               office_id2].loc[df['Year'] ==
                                                                      year_id2]
        GeoIds = list(df_graph2['GEOID20'].unique())
        value=[]
        for num in GeoIds:
            value.append(df_graph[df_graph["GEOID20"] == num]['Percent'].values[0] -
                        df_graph2[df_graph2["GEOID20"] == num]['Percent'].values[0])
        df_graph_comp=pd.DataFrame(list(zip(value, GeoIds)), columns = ['Percent', "GEOID20"])
        fig = px.choropleth_mapbox(df_graph_comp, geojson=gj, color="Percent", color_continuous_scale="Viridis",
                               locations="GEOID20", featureidkey="properties.GEOID20",
                               range_color=(df_graph_comp["Percent"].min(), df_graph_comp["Percent"].max()),
                               center={"lat": 41.2033, "lon": -77.1945},
                               mapbox_style="carto-positron", zoom=6, title=f"Percent vote share of {year_id} {office_id} ({party_id}) minus that of {year_id2}  {office_id2} ({party_id2})")
        x_values=df[df['Party'] ==party_id2].loc[df['Office'] ==office_id2].loc[df['Year'] ==year_id2]['Percent'].values
        y_values=df[df['Party'] ==party_id].loc[df['Office'] ==office_id].loc[df['Year'] ==year_id]['Percent'].values
        second_fig=px.scatter(df, x=x_values, y=y_values,
                              title=f"Comparison of the Percent of the vote shares")
        second_fig.update_xaxes(title_text=f"Percent vote share of {year_id} {office_id} ({party_id})", range=[0,100])
        second_fig.update_yaxes(title_text=f"Percent vote share of {year_id2} {office_id2} ({party_id2})", range=[0,100])
        second_fig.add_scatter(x=[0, 100], y=[0, 100])

    else:
        fig = px.choropleth_mapbox(df_graph, geojson=gj, color="Percent", color_continuous_scale="Viridis",
                               locations="GEOID20", featureidkey="properties.GEOID20",
                               range_color=(0, 100),
                               center={"lat": 41.2033, "lon": -77.1945},
                               mapbox_style="carto-positron", zoom=6, title=f"Percent vote share of {year_id} {office_id} ({party_id})")
        second_fig=px.bar(df_graph, x='County', y='Percent')
        #                  hover_name="County", hover_data='Votes',
#                          title=f"Percent vote share of {year_id} {office_id} ({party_id})",
#                          category_orders='total descending')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, title={'y':.98})

#    fig.show()
#    fig.update_xaxes(title=xaxis_label)



    return fig, second_fig


if __name__ == '__main__':
    app.run_server(debug=True)