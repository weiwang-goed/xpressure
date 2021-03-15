import dash
import os
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import pickle
import json
from datetime import datetime
import daemon
import plotly.figure_factory as ff

audioPath = './audio/'
testingTick = 0
selected = ''
today = './data/' + datetime.today().strftime('%m_%d') + '.txt'

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'notation': '#7FFFFF'
}

############ Data  #######################

############ Callbacks ###################

def registerCallback(app):
    @app.callback(
        [Output('graph-line', 'figure'), Output('graph-2D', 'figure')], 
        [Input('timer-update', 'n_intervals'), State('date-selector', 'value')]
    )
    def update_sensor_lines(n_intervals, path):
        df=pd.read_csv(path, sep=',',header=None)
        print( df.values.shape )
        dataNum = df.values.shape[0]

        avg = np.average(df.values[:, 1:], axis = 1)    
        figL = go.Figure()
        if path == today:
            y = avg[max(-1*dataNum, -2000):]
        else:
            y = avg

        figL.add_trace(go.Scatter(x= np.arange(len(y)), y=y, mode='lines', name='average'))


        figL.update_layout(
            template="seaborn",
            showlegend=True,
            )

        if path == today:
            z = df.values[-1, 1:].reshape(10,7)
        else:
            z = df.values[ min(n_intervals, dataNum-1),1:].reshape(10,7)

        figH = ff.create_annotated_heatmap(z, zmin=0, zmax=1024)    
        # figH = go.Figure(data=go.Heatmap(
        #            z=z,
        #            x=[ 'row'+str(i) for i in range(10)],
        #            y=[ 'col'+str(i) for i in range(10)], 
        #            zmin = 0, zmax = 1024, text = z, 
        #            hoverongaps = False))
        figH.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            font_size = 12, 
            legend_font_size = 23,
            legend_title_font_size = 25)

        return figL, figH


    @app.callback(
        Output('timer-update', 'interval'),
        [Input('timer-selector', 'value')]
    )
    def update_timer(value):
        print('timer: ', int(value[:-2]))
        return int(value[:-2])

    @app.callback(
        Output('DEBUG', 'children'),
        [Input('date-selector', 'value')]
    )
    def update_debug_token(clickData):
        v = str(clickData)
        return v