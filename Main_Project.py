# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 00:54:47 2022

@author: omark
"""

#============================================================
# IMPORTS
#============================================================

import pandas as pd

from dash import Dash, dash_table, html, dcc
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output

#============================================================

DEBUG = True 
nbaData = pd.read_excel("./nba_player_data.xlsx")
    #'nba_player_data.xlsx')

teamDescription = nbaData.drop(columns=['TEAM_ID','PLAYER_ID'])
teamDescription = teamDescription.groupby(['TEAM']).mean()

# players.drop(columns = ['RANK', 'EFF',' season_start_year'], inplace = True)
# players['start_year'] = players['Year'].str[:4].astype(int)
# players['TEAM'].replace(to_replace=['NOP', 'NOH'], value = 'NO', inplace = True)
# players['Season_Type'].replace('Regular%20Season', 'Regular', inplace = True)

#============================================================
# Data Visualization
#============================================================


def createRadarChart(player : str, year : int ):
    
    global nbaData
    global DEBUG 

    year_string_lookup = { 2012:'2012-13', 2013:'2013-14', 2014:'2014-15', 2015:'2015-16'}
    year = year_string_lookup[year]

    if DEBUG:
        print(f'UPDATING RADAR CHART: {year}, {player}')


    fig = go.Figure()
    variables = ['Field Goal %', '3-Pointer %', 'Free Throw %']

    playerData = nbaData[ nbaData['PLAYER'] == player]
    try:
        playerDataForYear = playerData[ playerData['Year'] == year ].mean()
        fieldGoalPercent = playerDataForYear['FG_PCT']
        threePtrPercent = playerDataForYear['FG3_PCT']
        freeThrowPercent = playerDataForYear['FT_PCT']
        print([fieldGoalPercent, threePtrPercent, freeThrowPercent])
    except Exception as exception:
        print(f'Exception: {exception}')
        fieldGoalPercent = 15
        threePtrPercent = 15
        freeThrowPercent = 15

    fig.add_trace(go.Scatterpolar(
        r=[fieldGoalPercent*100, threePtrPercent*100, freeThrowPercent*100],
        theta=variables,
        fill='toself',
        name='Product A'
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0, 100]
        )),
    showlegend=False
    )

    return fig

def createBarGraph(team, attribute):

    global nbaData

    attribute_lookup = { 'Field Goal %' : 'FG_PCT', '3-Pointer %' : 'FG3_PCT', 'Free Throw %':'FT_PCT'}
    attribute = attribute_lookup[attribute]

    data = nbaData[ nbaData['TEAM'] == team ].groupby(['PLAYER']).mean()[[f'{attribute}']].reset_index().sort_values(by=[f'{attribute}'], ascending=False)

    # try:
    fig = px.bar(data, x='PLAYER', y=f'{attribute}')
    
    return fig 

    # except Exception:
    #     return None     


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Create dash app
app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Build dash app layout 
app.layout = html.Div([

    html.H1('NBA Statistics'),
    
    dcc.Tabs([

        dcc.Tab(label='Player Statistics', children = [
            
            html.Br(),

            html.Div([
                html.P('Team:'),
                dcc.Dropdown( nbaData['TEAM'].unique(), searchable=True, id='team-name' )
            ]),

            html.Div([
                html.P('Player:'),
                dcc.Dropdown( nbaData['PLAYER'].unique(), searchable=True, id='player-name' )
            ]),

            html.Br(),

            dcc.Slider(2012, 2017,
                step=None,
                marks={
                    2012: '2012-13',
                    2013: '2013-14',
                    2014: '2014-15',
                    2015: '2015-16',
                },
                value=2015,
                id='year-slider'
            ),

            html.Div([

                html.Div([
                dcc.Graph(figure=createRadarChart('Kevin Durant', 2012), id='radar-chart')
                ])

            ])
        ]),


        dcc.Tab(label='Team Statistics', children = [
            
            html.Br(),

            html.Div([
                html.P('Team:'),
                dcc.Dropdown( nbaData['TEAM'].unique(), searchable=True, id='team-name-2' )
            ]),

            dcc.RadioItems(['Field Goal %', '3-Pointer %', 'Free Throw %'], id='attribute'),

            html.Div([dcc.Graph(figure=px.bar(nbaData[ nbaData['TEAM'] == 'OKC' ].groupby(['PLAYER']).mean()[[f'FT_PCT']].reset_index().sort_values(by=['FT_PCT'], ascending=False), x='PLAYER', y=f'FT_PCT'),
                                id='bar-graph')])
        ])
    ])

], style={'marginBottom': 50, 'marginTop': 25})

#============================================================
# App callbacks
#============================================================

@app.callback(Output(component_id='player-name', component_property='options'),
                [Input(component_id='team-name', component_property='value')])
def updatePlayerList(team):
    return nbaData[nbaData['TEAM'] == team ]['PLAYER'].unique()

@app.callback(Output(component_id='radar-chart', component_property='figure'),
                [Input(component_id='year-slider', component_property='value'),Input(component_id='player-name', component_property='value')])
def updateRadarChart(year, player='Kevin Durant'):
    return createRadarChart(player,year)

@app.callback(Output(component_id='bar-graph', component_property='figure'),
                [Input(component_id='team-name-2', component_property='value'), 
                Input(component_id='attribute', component_property='value') ])
def updateBarGraph(team, attribute):
    return createBarGraph(team,attribute)



#============================================================
# Run App 
#============================================================

# Run app and display result inline in the notebook
app.run_server()


