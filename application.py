#!/usr/bin/env python3

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
        zoom=2.5,
        center=dict(lat=65, lon=-152),
        style="light",
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

help_text = html.Div(
    className='container',
    children=[
        dcc.Markdown(
            """
### Notes:
* Confidence level: * – low (no reports with ground-ice data, no HMPs; estimation is based on general information on surficial geology and PF occurrence and analysis of available imagery); ** – medium (some information on permafrost conditions is available, including several geotechnical reports, HMPs, etc.); *** – high (comprehensive data are available, including numerous reports with geotechnical information, HMPs, and other sources, or we have sufficient information that there is no PF in the area).
* Massive ice occurrence: 0 – no permafrost; 1 – no massive ice; 2 – sparse small to medium ice wedges (inactive or slightly active) and/or rare occurrence of buried ice; 3 – abundant large ice wedges close to the surface (yedoma and/or active modern wedges) and/or large bodies of buried glacier ice close to the surface. Occurrence of large ice bodies near the surface makes communities extremely vulnerable to PF thawing even in the areas with very low PF temperatures.
* Thaw susceptibility: 0 – no permafrost; 1 – almost no excess ice, thaw settlement is less than ~0.1 m; 2 – thaw settlement is ~0.2-0.7 m; 3 – thaw settlement is more than 1 m.
* Existing PF-related problems: 0 – no permafrost; 1 – no PF-related problems (or minor problems); 2 – Moderate problems; 3 – Severe problems. Estimation is based mainly on available documents (e.g., HMPs) and/or pers.com.
* Permafrost Occurrence: 0 – no permafrost; 1 – mostly unfrozen soils with isolated patches of PF; 2 – discontinuous permafrost (intermittent distribution of PF and unfrozen soils, numerous open and/or closed taliks); 3 – continuous permafrost (rare taliks exist only under large and deep waterbodies).
* Permaftost Temperature: 0 – no permafrost; 1 – Mean annual ground temperature (MAGT) < -5°C (< -8°C for saline soils); 2 – MAGT = -5 – -2°C (-8– -5°C for saline soils); 3 – MAGT = -2 –
*0°C (-5– -3°C for saline soils).
* Risk level based on the rating score: 0 – no permafrost; 5-8 – low risk level; 9-11 – medium risk level; 12-15 - high risk level. Rating score (cumulative risk level) is a sum of ranks for five different categories: PF temperature; thaw susceptibility (potential thaw settlement); occurrence of massive ice; existing PF-related problems. 
            """,
            className='content is-size-5'
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
                                        html.H1(
                                            'Community Risk Data & Selection'
                                        ),
                                        html.Div(
                                            'Community Permafrost data is available to explore local risks and hazards based on Massive Ice, Thaw Susceptibility, Existing Problems, Permafrost Occurrence, and Permafrost Temperature. (This is only Sample Text).<br>Select one or more communities to get more information about these risks.'
                                        ),
                                        community
                                    ]
                                ),
                                html.Div(
                                    className='column',
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
                                ),

                            ]
                        ),
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
                help_text
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
            
        marker_texts = [df[10], df[9], df[11], df[7], df[8]]
        marker_size_vals = [df[5], df[4], df[6], df[2], df[3]]
        marker_sizes = [x * 0.8 + 0.25 for x in marker_size_vals]




        figure['data'].append({
            'x': hazard_lu,
            'y': [df['Community'], df['Community'], df['Community'], df['Community'], df['Community']],
            'name': df['Community'],
            'showlegend': False,
            'hovertext': marker_texts,
            'hovertemplate': "%{text}",
            'text': marker_texts,
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
