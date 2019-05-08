import os
import json
from random import randint
import numpy as np
import dash
import flask
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import geopandas as gpd

server = flask.Flask(__name__)
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
communities = pd.read_csv('Data.csv')
names = communities['Community']
path_prefix='./'
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

def calc_rolling_mean(array, ndays, location):
    annual_rolling_pcpt = []
    annual_rolling_mean = []
    rolling_pcpt = []
    for i, (index,row) in enumerate(df.iterrows()):
        rolling_pcpt.append(row[location])
        if len(rolling_pcpt) > (ndays):
            rolling_pcpt.pop(0)
        annual_rolling_mean = np.mean(rolling_pcpt)
        annual_rolling_pcpt = np.sum(rolling_pcpt)
    return {'pcpt': annual_rolling_pcpt, 'mean': annual_rolling_mean}

community = html.Div(
    className='field',
    children=[
        html.Label('Select Location'),
        html.Div(
            className='control',
            children=[
                dcc.Dropdown(
                    id='community',
                    options=[{'label':name, 'value':name} for name in names],
                    value='Shishmaref',
                    multi=True
                )
            ]
        )
    ]
)



map_communities_trace = go.Scattermapbox(
    lat=communities['Latitude'],
    lon=communities['Longitude'],
    mode='markers',
    marker={
        'size': 15,
        'color': 'rgb(80,80,80)'
    },
    line={
        'color': 'rgb(0, 0, 0)',
        'width': 2
    },
    text=communities['Community'],
    hoverinfo='text'
)

map_layout = go.Layout(
    height=400,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3,
        center=dict(lat=65, lon=-146.5),
    ),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

map_figure = go.Figure({
    'data': [map_communities_trace],
    'layout': map_layout
})


config = {
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'CommunityRisk',
        'height': 500,
        'width': 1200,
        'scale': 1
    }
}
header_section = html.Div(
    className='header',
    children=[
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='section',
                    children=[
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='header--logo',
                                    children=[
                                        html.A(
                                            className='header--snap-link',
                                            href='https://snap.uaf.edu',
                                            rel='external',
                                            target='_blank',
                                            children=[
                                                html.Img(src=path_prefix + 'assets/SNAP_acronym_color_square.svg')
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className='header--titles',
                                    children=[
                                        html.H1(
                                            'Community Permafrost Data',
                                            className='title is-2'
                                        ),
                                        html.H2(
                                            'Explore community risk to permafrost.',
                                            className='subtitle is-4'
                                        )
                                    ]
                                ),
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

footer = html.Footer(
    className='footer has-text-centered',
    children=[
        html.Div(
            children=[
                html.A(
                    href='https://snap.uaf.edu',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/SNAP.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/UAF.svg'
                        )
                    ]
                ),
            ]
        ),
        dcc.Markdown(
            """
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className='content is-size-6'
        )
    ]
)

app.layout = html.Div(
    children=[
        header_section,
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='column',
                                    children=[
                                        dcc.Graph(
                                            id='weather-plot',
                                            config=config
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='column',
                                    children=[
                                        community
                                    ]
                                ),
                            ]
                        ),
                        html.Div(
                            className='column is-one-third',
                            children=[
                                dcc.Graph(
                                    id='map',
                                    figure=map_figure,
                                    config={
                                        'displayModeBar': False,
                                        'scrollZoom': False
                                    }
                                )
                            ]
                        )
                    ]
                )
            ]
        ),
        footer
    ]
)

@app.callback(
    Output('community', 'value'),
    [
        Input('map', 'clickData')
    ]
)

def update_mine_site_dropdown(selected_on_map):
    """ If user clicks on the map, update the drop down. """
    if selected_on_map is not None:
        # Return community name
        return selected_on_map['points'][0]['text']
    # Return a default
    return 'Shishmaref'

@app.callback(
    Output('weather-plot', 'figure'),
    inputs=[
        Input('community', 'value')
    ]
)
def make_plot(community):
    figure = {}
    figure['data'] = []

    hazard_lu = ['Massive Ice', 'Thaw Susceptibility', 'Existing Problems', 'Permafrost Occurrence','Permafrost Temperature' ]
    mult = 200.0
    marker_colors = ['#053F5A','#2AACB5','#DDE495','#EEB26B','#E1695B']




    for i in community:
        if type(community) == str: 
            df = communities[communities['Community'] == community].iloc[0]
        else:
            df = communities[communities['Community'] == i].iloc[0]
            
        marker_texts = [df[11], df[10], df[12], df[8], df[9]]
        marker_sizes = [x * 0.8 + 0.25 for x in marker_texts]




        figure['data'].append({
            'x': hazard_lu,
            'y': [df['Community'], df['Community'], df['Community'], df['Community'], df['Community']],
            'name': df['Community'],
            'showlegend': False,
            'hovertext': marker_texts,
            'hovertemplate': "Risk Level: %{text}",
            'text': marker_texts,
            #'mode': 'markers+text',
            'mode': 'markers',
            'marker': {
                'color': marker_colors,
                'size': marker_sizes,
                'sizeref': 0.05,
                'sizemode': 'scaled',
                'opacity': 1.0
            },
        })

    ref_sizes = [0.25, 1.05, 1.85, 2.65, 0]
    ref_text = [0, 1, 2, 3, '']
    ref_colors = 'rgb(150,150,150)'
    figure['data'].append({
        'x': hazard_lu,
        'y': ['<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>', '<b>Reference</b>'],
        'name': 'Reference',
        'showlegend': False,
        'hovertext': ref_text,
        'hovertemplate': "Risk Level: %{text}",
        'text': ref_text,
        'textposition': 'top center',
        'mode': 'markers+text',
        'marker': {
            'color': ref_colors,
            'size': ref_sizes,
            'sizeref': 0.05,
            'sizemode': 'scaled'
        },
    })
    layout = {
        'barmode': 'grouped',
        'hovermode': 'closest',
        'title': {
            'text': 'Community Permafrost Data',
        },
	'height': 500,
	'yaxis': {
            'showline': 'false',
            'hoverformat': '1f'
	},
        'margin': {
            'b': 100
        },
        'xaxis': { 
            'range': hazard_lu,
            'type': 'category',
            'showline': 'false'
        }
    }
    figure['layout'] = layout
    return figure

if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
    #app.run_server(debug=True)
