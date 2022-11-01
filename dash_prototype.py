#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 00:23:21 2022

@author: trym
"""

import datetime
import requests
import json
import dash
from dash import html, dcc, dash_table
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go

def hente_bussdata():
    headers = {"ET-Client-Name": "****"}
    def run_query(query):
        request = requests.post('https://api.entur.io/journey-planner/v3/graphql', json={'query': query}, headers=headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Feilkode {}. {}".format(request.status_code, query))
    query = """
    {
      stopPlaces(ids: ["NSR:StopPlace:4527" "NSR:StopPlace:4531"]){
        id
        name
        estimatedCalls(timeRange: 72100, numberOfDepartures: 2) {
          realtime
          aimedDepartureTime
          expectedDepartureTime
          destinationDisplay {
            frontText
          }
          quay {
            id
          }
          serviceJourney {
            journeyPattern {
              line {
                id
    	    publicCode
                name
              }
            }
          }
        }
      }
    }
    """
            # stopPlaces(ids: ["NSR:StopPlace:4527" "NSR:StopPlace:4531"])
    result = run_query(query)
    def getProps (estimatedCall):
        return {
            'linje': estimatedCall['serviceJourney']['journeyPattern']['line']['publicCode'],
            'destinasjon': estimatedCall['destinationDisplay']['frontText'],
            'sanntid': estimatedCall['expectedDepartureTime'],
            'avgang': estimatedCall['aimedDepartureTime']
                }
    filteredDataList = []
    for i in range(0,2):
        for estimatedCall in result['data']['stopPlaces'][i]['estimatedCalls']:
            filteredDataList.append(getProps(estimatedCall))
    df = pd.DataFrame.from_dict(filteredDataList)
    df['sanntid'] = df['sanntid'].str.slice(11, 19)
    df['avgang'] = df['avgang'].str.slice(11, 19)
    df.sort_values('sanntid', ascending=True, inplace=True)

    return df

df = hente_bussdata()


def vaer_data():
    url = 'https://api.met.no/weatherapi/locationforecast/2.0/complete?altitude=35&lat=59.92453&lon=10.709682'
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': '**** github.com/trlang',
        }
    )
    
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    
    
    tidsserie_temp = pd.DataFrame()
    for i in range(len(response_dict['properties']['timeseries'])):
        instans = response_dict['properties']['timeseries'][i]['data']['instant']['details']
        df = pd.DataFrame(instans, index=[response_dict['properties']['timeseries'][i]['time']])
        tidsserie_temp = pd.concat([tidsserie_temp, df])
        
    tidsserie_regn = pd.DataFrame()
    for i in range(len(response_dict['properties']['timeseries'])):
        try:
            instans = response_dict['properties']['timeseries'][i]['data']['next_1_hours']['details']
            df = pd.DataFrame(instans, index=[response_dict['properties']['timeseries'][i]['time']])
            tidsserie_regn = pd.concat([tidsserie_regn, df])
        except KeyError:
            pass
    return tidsserie_regn

tidsserie = vaer_data()

 
def figur(data):
    x = list(data.index)
    x_rev = x[::-1]
    
    # Line 1
    y1 = list(data.precipitation_amount)
    y1_upper = list(data.precipitation_amount_max)
    y1_lower = list(data.precipitation_amount_min)
    y1_lower = y1_lower[::-1]
    
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x+x_rev,
        y=y1_upper+y1_lower,
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line_color='rgba(255,255,255,0)',
        showlegend=False,
        
    ))
    
    fig.add_trace(go.Scatter(
        x=x, y=y1,
        line_color='rgb(0,100,80)',
        showlegend=False,
    ))
    fig.update_layout(width=915)
    fig.update_layout(title_text = "Nedbør")
    
    
    return fig

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



app.layout = html.Div(className='row', children=[
    html.H1('Klokken er: ' + str(datetime.datetime.now().strftime('%H:%M:%S')), id ='tittel'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
        ),
    dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], id='tbl'),
    dcc.Interval(
        id='interval-buss',
        interval=60*1000, # in milliseconds
        n_intervals=0),
    html.Div(children=[
        dcc.Graph(figure = figur(tidsserie), id="graph1", style={'display': 'inline-block'}),
        dcc.Graph(figure = figur(tidsserie), id="graph2", style={'display': 'inline-block'})
    ]),
    dcc.Interval(
        id='interval-vaer',
        interval=60*1000, # in milliseconds
        n_intervals=0),
])


@app.callback(Output('tittel', 'children'),
              Input('interval-component', 'n_intervals'))
def serve_layout(self):
    return html.H1('Klokken er: ' + str(datetime.datetime.now().strftime('%H:%M:%S')))

@app.callback(Output('tbl', 'children'),
              Input('interval-buss', 'n_intervals'))
def oppdatere_bussdata(self):
    df = hente_bussdata()
    return dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], id='tbl')

@app.callback(Output('graph1', 'figure'),
              Output('graph2', 'figure'),
              Input('interval-vaer', 'n_intervals'))
def oppdatere_graf(n):
    df = vaer_data()
    return figur(df), figur(df)

if __name__ == '__main__':
    app.run_server(port = 8060, debug=True)



    
