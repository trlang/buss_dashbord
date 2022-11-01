#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 00:23:21 2022

@author: trym
"""
import datetime
import requests
import dash
from dash import html, dcc, dash_table
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from hente_bussdata import hente_bussdata
from vaer_data import vaer_data
from figur import figur

# Henter buss- og værdata
buss_data = hente_bussdata()
tidsserie = vaer_data()

 

# Starter appen, og laster inn noen visuelle oppdateringer
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Klokke til å ha øverst. Mulig den skal endres til bare å vise når dataene ble oppdatert sist 
app.layout = html.Div(className='row', children=[
    html.H1('Klokken er: ' + str(datetime.datetime.now().strftime('%H:%M:%S')), id ='tittel'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
        ),
# Bussdata-tabellen, størrelsen kan endres i . Oppdateres hvert minutt
    dash_table.DataTable(
        buss_data.to_dict('records'),
        [{"name": i, "id": i} for i in buss_data.columns],
        id='tbl'),
    dcc.Interval(
        id='interval-buss',
        interval=60*1000, # in milliseconds
        n_intervals=0),
''' 
Her er det også mulig å lage dataframet slik:
dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[{'id': c, 'name': c} for c in df.columns],
    id='tbl'
'''
# Her er grafene, størrelsen på disse kan man endre i figur.py    
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


@app.callback([Output('tbl', 'data'), Output('tbl', 'columns')],
              [Input('interval-buss', 'n_intervals')])
def oppdatere_bussdata(n):
    if n in [0, None]:
        raise PreventUpdate
    else:
        buss_data = hente_bussdata()
        columns = [{"name": i, "id": i} for i in buss_data.columns]
        verdier = buss_data.to_dict('records')

        return verdier, columns


@app.callback(Output('graph1', 'figure'),
              Output('graph2', 'figure'),
              Input('interval-vaer', 'n_intervals'))
def oppdatere_graf(n):
    df = vaer_data()
    return figur(df), figur(df)

if __name__ == '__main__':
    app.run_server(port = 8061, debug=True)



    



