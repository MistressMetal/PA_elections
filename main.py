# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 18:16:33 2021
@author: linds
"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import geojson
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server
app.config.suppress_callback_exceptions = True

with open('data/pa_counties.json') as f:
    gj = geojson.load(f)

df = pd.read_csv('data/2020_2022_counties_results.csv')

available_parties = list(df['Party'].unique())
available_parties.remove('All')
#available_indicators = df['Office'].unique()
available_indicators = ['Governor', 'US Senator', 'Attorney General', 'Auditor', 'US President']
available_years = df['Year'].unique()

df_graph_empty = pd.DataFrame(columns=['DistrictNumber', 'x_votes', 'y_votes'])
df_second=pd.DataFrame(columns=['first', 'second'])

row= html.Div([
    html.Div([
        html.Div(children="", style={'display': 'inline-block', 'width':"10%"}),
        html.Div(children=[
            html.H6("First set of results"),
            html.Label("Select Office:"),
            dcc.Dropdown(
                id='office_id',
                options=[{'label': i, 'value': i} for i in available_indicators],
                style={'width':"100%"}),
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
            ], style={'display': 'inline-block', 'padding': 10, 'width':"80%"})
        ], style={'display': 'inline-block', 'padding': 10, 'width':"30%"}),
    html.Div([
        html.Label("Comparison?"),
        dcc.RadioItems(
            id='comparator',
            options=['Yes', 'No'],
            value='No'
            ),
        html.Br(),
        html.Button("Create Map", id='create_button', n_clicks=0)
        ], style={'display': 'inline-block', 'padding':30, 'flex':1, 'align':'top', 'width':"10%"}),
    html.Div([
        html.Div(id='second_set', children=[
            html.H6(id="second_set_title"),# "Second set of results"),
            html.Label(id="second_set_office_label"),#, "Select Office:"),
            html.Div(id='second_set_office_dropdown', children=[dcc.Dropdown(
                id='office_id2',
                options=[{'label': i, 'value': i} for i in available_indicators])]),
            html.Br(),
            html.Label(id='second_set_party_label', children="Select Party:"),
            html.Div(id="second_set_party_dropdown", children=[dcc.Dropdown(
                id='party_id2',
                options=[{'label': i, 'value': i} for i in available_parties])]
            ),
            html.Br(),
            html.Label(id='second_set_year_label', children="Select Year:"),
            html.Div(id='second_set_year_dropdown', children=[dcc.Dropdown(
                id='year_id2',
                options=[{'label': i, 'value': i} for i in available_years])]
            )
            ], style={'display': 'inline-block', 'padding': 10, 'width':"80%"}),
#        html.Div(children="", style={'display': 'inline-block', 'width': "10%"})
        ],
        style={'display': 'inline-block', 'padding': 10, 'width':"30%"}),
        html.Hr(),
    html.Div(children=html.Div([html.H2("")], style={'width':"80%"}), id='indicator_graphic'),
    html.Div(id="indicator_explaination", children=""),
    html.Hr(),
    html.Div(children=html.Div([html.H2("")]), id='second_graphic'),
    html.Div(id="second_explaination", children="")], style={'padding': 10, 'align':'center'}

)

app.layout = dbc.Container(row, fluid=True)

### Update the Party options after selecting an office on the left.
@app.callback(Output('party_id', 'options'),
              Input('office_id', 'value'))
def update_available_parties(office_id):
    available_parties_current=list(df.loc[df.Office==office_id]["Party"].unique())
    if ('All' in available_parties_current):  available_parties_current.remove('All')

    return [{'label': i, 'value': i} for i in available_parties_current]

@app.callback(Output('party_id2', 'options'),
              Input('office_id2', 'value'))
def update_available_parties(office_id2):
    available_parties_current=list(df.loc[df.Office==office_id2]["Party"].unique())
    if ('All' in available_parties_current):  available_parties_current.remove('All')
    return [{'label': i, 'value': i} for i in available_parties_current]

### Update the Year options after selecting an office on the left.
@app.callback(Output('year_id', 'options'),
              Input('office_id', 'value'))
def update_available_years(office_id):
    available_years_current=df.loc[df.Office==office_id]["Year"].unique()
    return [{'label': i, 'value': i} for i in available_years_current]

@app.callback(Output('year_id2', 'options'),
              Input('office_id2', 'value'))
def update_available_years(office_id2):
    available_years_current=df.loc[df.Office==office_id2]["Year"].unique()
    return [{'label': i, 'value': i} for i in available_years_current]

@app.callback(Output('second_set', 'children'),
              Input('comparator', 'value'))
def add_remove_second_set (comparator_value):
    if comparator_value=="Yes":
        return [
            html.H6(id="second_set_title", children="Second set of results"),
            html.Label(id="second_set_office_label", children="Select Office:"),
            html.Div(id='second_set_office_dropdown', children=[dcc.Dropdown(
                id='office_id2',
                options=[{'label': i, 'value': i} for i in available_indicators]
            )]),
            html.Br(),
            html.Label(id='second_set_party_label', children="Select Party:"),
            html.Div(id="second_set_party_dropdown", children=[dcc.Dropdown(
                id='party_id2',
                options=[{'label': i, 'value': i} for i in available_parties])]
            ),
            html.Br(),
            html.Label(id='second_set_year_label', children="Select Year:"),
            html.Div(id='second_set_year_dropdown', children=[dcc.Dropdown(
                id='year_id2',
                options=[{'label': i, 'value': i} for i in available_years])]
            )
        ]
    else:

        return [
            html.H6(id="second_set_title", children=""),
            html.Label(id="second_set_office_label", children=""),
            html.Div(id='second_set_office_dropdown', children=[html.Div(id="office_id2")]),
            html.Br(),
            html.Label(id="second_set_party_label", children=""),
            html.Div(id="second_set_party_dropdown", children=[html.Div(id="party_id2")]),
            html.Br(),
            html.Label(id='second_set_year_label', children=""),
            html.Div(id='second_set_year_dropdown', children=[html.Div(id="year_id2")])
        ]

@app.callback(Output(component_id='indicator_graphic', component_property='children'),
              Output(component_id='second_graphic', component_property='children'),
              Output(component_id='indicator_explaination', component_property='children'),
              Output(component_id='second_explaination', component_property='children'),
              Input(component_id='create_button', component_property='n_clicks'),
              State(component_id='office_id', component_property='value'),
              State(component_id='party_id', component_property='value'),
              State(component_id='year_id', component_property='value'),
              State(component_id='comparator', component_property='value'),
              State(component_id='office_id2', component_property='value'),
              State(component_id='party_id2', component_property='value'),
              State(component_id='year_id2', component_property='value')
              )

def update_graph(n_clicks, office_id, party_id, year_id,
                 comparator,
                 office_id2, party_id2, year_id2
                ):
    if n_clicks and n_clicks >0:
        if not (office_id and party_id and year_id):
            return html.Div("Please select an Office, Party, and Year to display results"), html.Div("")
        # setup a dataframe that will be graphed
        df_graph = df[df['Party'] ==
                                  party_id].loc[df['Office'] ==
                                                   office_id].loc[df['Year'] ==
                                                                          year_id]
        if comparator=='Yes':
            if not (office_id2 and party_id2 and year_id2):
                return html.Div("Please select an Office, Party, and Year to compare with"), html.Div("")

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
                                   mapbox_style="carto-positron", zoom=6,
                                   title=f"Percent vote share of {year_id} {office_id} ({party_id}) minus that of {year_id2}  {office_id2} ({party_id2})")
            y_values = df[df['Party'] == party_id2].loc[df['Office'] == office_id2].loc[df['Year'] == year_id2][
                'Percent'].values
            x_values = df[df['Party'] == party_id].loc[df['Office'] == office_id].loc[df['Year'] == year_id][
                'Percent'].values
            if x_values.max() + 10 > 100:
                x_max = 100
            else:
                x_max = x_values.max() + 10
            if y_values.max() + 10 > 100:
                y_max = 100
            else:
                y_max = y_values.max() + 10

            second_fig = px.scatter(df, x=x_values, y=y_values,
                                    title=f"Comparison of the Percent of the vote shares")
            second_fig.update_xaxes(title_text=f"{year_id} {office_id} ({party_id})", range=[0, x_max])
            second_fig.update_yaxes(title_text=f"{year_id2} {office_id2} ({party_id2})", range=[0, y_max])
            second_fig.add_scatter(x=[0, 100], y=[0, 100], line={'color': "#BBBBBB"}, showlegend=False)
            second_fig.update_layout(template='simple_white')
            indicator_explain=f"Areas with positive values where the {year_id} {office_id} ({party_id}) out performed the {year_id2} {office_id2} ({party_id2})"
            second_explain=f"Points above and to the left of the gray line represent counties where the {year_id2} {office_id2} ({party_id2}) performed better. Points below and to the right of the gray line represent counties where the {year_id} {office_id} ({party_id}) performed better. "

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
            second_fig.update_layout(template='simple_white')
            indicator_explain=""
            second_explain = ""

        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, title={'y':.98})




        return [dcc.Graph(figure=fig, style={'width':"80%"})], [dcc.Graph(figure=second_fig, style={'width':"80%"})], indicator_explain, second_explain
    return html.Div(""), html.Div(""), "", ""


if __name__ == '__main__':
    app.run_server(debug=True)
