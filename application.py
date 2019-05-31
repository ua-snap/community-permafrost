#!/usr/bin/env python3
# pylint: disable=C0103,E0401

import os
import json
from random import randint
import math
import numpy as np
import dash
import dash_table
import flask
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html

import pandas as pd
import geopandas as gpd

server = flask.Flask(__name__)
mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
communities = pd.read_csv('Data.csv')
names = communities['Community']
path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server
app.title = 'SNAP - Community Permafrost Data'
app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# Community Dropdown
community = html.Div(
    className='field',
    children=[
        html.Label('Type the name of one or more communities in the box below to get started.'),
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

# Risk Type Dropdown
risk_type = html.Div(
    className='field',
    children=[
        html.Label('Select a category to visualize on the map'),
        html.Div(
            className='control',
            children=[
                dcc.Dropdown(
                    id='risk_type',
                    options=[
                        {'label':'Risk Level', 'value':'Risk Level'},
                        {'label':'Massive Ice', 'value':'Massive Ice'},
                        {'label':'Thaw Susceptibility', 'value':'Thaw Susceptibility'},
                        {'label':'Existing Problems', 'value':'Existing Problems'},
                        {'label':'Permafrost Occurrence', 'value':'Permafrost Occurrence'},
                        {'label':'Permafrost Temperature', 'value':'Permafrost Temperature'}
                    ],
                    value='Risk Level'
                )
            ]
        )
    ]
)

# Set defaults for map load.
risk_level = communities['Risk Level']
risk_color = []
for i in risk_level:
    if i == 'High':
        risk_color.append('#df684f')
    if i == 'Medium':
        risk_color.append('#f3cd4f')
    if i == 'Low':
        risk_color.append('#5d804c')
    if i == 'None':
        risk_color.append('#808080')

# Concat risk level with community for hover titles
communities['Hover Title'] = communities[['Community', 'Risk Level']].apply(lambda x: ': '.join(x), axis=1)

map_communities_trace = go.Scattermapbox(
    lat=communities['Latitude'],
    lon=communities['Longitude'],
    mode='markers',
    marker={
        'size': 15,
        'color': risk_color
    },
    text=communities['Hover Title'],
    hoverinfo='text'
)

map_layout = go.Layout(
    height=400,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3,
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

# Config options for bubble plot
config = {
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'CommunityRisk',
        'height': 500,
        'width': 1200,
        'scale': 1
    }
}

# Limit columns for data table to labels
table_columns = [{'name': 'Community', 'id': 'Community'}, {'name': 'Confidence', 'id': 'Confidence'}, {'name': 'Massive Ice', 'id': 'Massive Ice Table'}, {'name': 'Thaw Susceptibility', 'id': 'Thaw Susceptibility Table'}, {'name': 'Existing Problems', 'id': 'Existing Problems Table'}, {'name': 'Permafrost Occurrence', 'id': 'Permafrost Occurrence Table'}, {'name': 'Permafrost Temperature', 'id': 'Permafrost Temperature Table'}, {'name': 'Rating Score', 'id': 'Rating Score'}, {'name': 'Risk Level', 'id': 'Risk Level'}]

# Initial data table setup
initial=communities[communities['Community'] == 'Nome']
data_table = dash_table.DataTable(
    id='community-table',
    columns=table_columns,
    style_cell={
        'whiteSpace': 'normal',
        'textAlign': 'left'
    },
    data=initial.to_dict('records')
)

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
                    href='https://casc.alaska.edu/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/AKCASC_color.png'
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
                html.A(
                    href='https://www.erdc.usace.army.mil/Locations/CRREL/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/CRREL.png'
                        )
                    ]
                ),
                html.A(
                    href='https://www.denali.gov',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/DenaliCommission.png'
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
        html.A(id='descriptions'),
        dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
            """

<div class="content is-size-5">

<h3>Learn more about the variables used in this tool</h3>

<p>This data summarizes permafrost hazard risks specific for rural communitities in Alaska.
    It aggragates information from a number of different sources including DOT borehole logs and mean annual ground temperature (MAGT) from the GI Permafrost Lab
    to an average for the community.</p>

<h4>How to interpret permafrost hazards for your community</h4>

<p>You can examine community permafrost data for certain key permafrost values including massive ice and thaw susceptibility.  Communities with high massive ice and warm permafrost temperatures are of particular concern for infrastructure related issues.  Rating scores can be calculated by summing all categories using the associated values in the table. Risk levels translates this into a value.</p>

<h4>Detailed information on categories</h4>

<table class="legend">
    <thead>
        <tr>
            <th scope="col">Category</td>
            <th scope="col">Description of levels</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th scope="row">Confidence level</th>
            <td>
                <ul>
                    <li><strong>*</strong> – low (no reports with ground-ice data, no HMPs; estimation is based on general information on surficial geology and PF occurrence and analysis of available imagery)
                    </li>
                    <li><strong>**</strong> – medium (some information on permafrost conditions is available, including several geotechnical reports, HMPs, etc.)
                    </li>
                    <li><strong>***</strong> – high (comprehensive data are available, including numerous reports with geotechnical information, HMPs, and other sources, or we have sufficient information that there is no PF in the area)
                    </li>
                </ul>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend massive-ice">Massive ice occurrence</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>1 – no massive ice</li>
                    <li>2 – sparse small to medium ice wedges (inactive or slightly active) and/or rare occurrence of buried ice</li>
                    <li>3 – abundant large ice wedges close to the surface (yedoma and/or active modern wedges) and/or large bodies of buried glacier ice close to the surface  Occurrence of large ice bodies near the surface makes communities extremely vulnerable to PF thawing even in the areas with very low PF temperatures.</li>
                </ul>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend thaw-susceptibility">Thaw susceptibility</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>1 – almost no excess ice, thaw settlement is less than ~0.1 m
                    <li>2 – thaw settlement is ~0.2-0.7 m</li>
                    <li>3 – thaw settlement is more than 1 m</li>
                </ul>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend existing-problems">Existing permafrost-related problems</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>1 – no PF-related problems (or minor problems)
                    <li>2 – Moderate problems</li>
                    <li>3 – Severe problems</li>
                </ul>
                <p>Estimation is based mainly on available documents (e.g., HMPs) and/or pers.com.
                </p>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend permafrost-occurrence">Permafrost occurrence</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>1 – mostly unfrozen soils with isolated patches of PF</li>
                    <li>2 – discontinuous permafrost (intermittent distribution of PF and unfrozen soils, numerous open and/or closed taliks)</li>
                    <li>3 – continuous permafrost (rare taliks exist only under large and deep waterbodies)</li>
                </ul>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend permafrost-temperature">Permafrost temperature</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>1 – Mean annual ground temperature (MAGT) < -5°C (< -8°C for saline soils)</li>
                    <li>2 – MAGT = -5 – -2°C (-8– -5°C for saline soils)</li>
                    <li>3 – MAGT = -2 – *0°C (-5– -3°C for saline soils)</li>
                </ul>
            </td>
        </tr>
        <tr>
            <th scope="row" class="legend risk-level">Risk level based on the rating score</th>
            <td>
                <ul>
                    <li>0 – no permafrost</li>
                    <li>5-8 – low risk level</li>
                    <li>9-11 – medium risk level</li>
                    <li>12-15 - high risk level</li>
                </ul>
                <p>Rating score (cumulative risk level) is a sum of ranks for five different categories: permafrost occurrence and temperature; thaw susceptibility (potential thaw settlement); occurrence of massive ice and existing permafrost-related problems.
                </p>
            </td>
        </tr>
    </tbody>
</table>

<h5>More details</h5>

<p>Information produced as part of the report:<br/>
<a rel="noopener" target="_blank" href="https://scholarworks.alaska.edu/handle/11122/10155">
Risk Evaluation for Permafrost-Related Threats: Methods of Risk Estimation and Sources of Information</a>
</p>

</div>
            """
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
                                        html.Div(
                                            className='column',
                                            children=[
                                                dcc.Markdown(
                                                    """    
Explore permafrost risks and hazards for rural communities in Alaska based on massive ice, thaw susceptibility, existing infrastructure probelms, permafrost occurence and temperature. Detailed explanations for these variables can be found [below](#descriptions). These are tallied to create a cumulative rating score and risk level.
                                                    """,
                                                    className='content is-size-5'
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className='column',
                                            children=[
                                                risk_type
                                            ]
                                        ),
                                        html.Div(
                                            className='column',
                                            children=[
                                                community
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className='column',
                                    children=[
                                        dcc.Graph(
                                            id='map',
                                            figure=map_figure,
                                            config={
                                                'displayModeBar': 'hover',
                                                'scrollZoom': True,
                                                'modeBarButtonsToRemove': ["pan2d", "lasso2d", "toggleHover", "select2d"]
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
                        ),
                        html.Div(
                            className='column',
                            children=[
                                data_table,
                                html.Br(),
                                html.Br(),
                                html.Br()
                            ]
                        )
                    ]
                ),
                html.Div(
                    className='column',
                    children=[
                        help_text,

                    ]
                )
            ]
        ),
        footer
    ]
)

# Color Look Up table used for different risk_type dropdown selections
color_lu = {
    'Risk Level': {
        'None': '#808080',
        'Low': '#5d804c',
        'Medium': '#f3cd4f',
        'High': '#df684f'
    },
    'Massive Ice': {
        'None': '#808080',
        'Low': '#dcf5f9',
        'Medium': '#99e3ed',
        'High': '#1D94A5'
    },
    'Thaw Susceptibility': {
        'None': '#808080',
        'Low': '#cce6ee',
        'Medium': '#82c1d5',
        'High': '#2A697D'
    },
    'Existing Problems': {
        'None': '#808080',
        'Low': '#dfd2bd',
        'Medium': '#bfa67b',
        'High': '#AC8B53'
    },
    'Permafrost Occurrence': {
        'None': '#808080',
        'Low': '#cde7ef',
        'Medium': '#84c4d6',
        'High': '#2F798E'
    },
    'Permafrost Temperature': {
        'None': '#808080',
        'Low': '#dae3e5',
        'Medium': '#a1b8bc',
        'High': '#7F9EA3'
    }
}

# Callback for map object when risk_type dropdown is changed
@app.callback(
    Output('map', 'figure'),
    [
        Input('risk_type', 'value')
    ]
)

def update_map_colors(risktype):
    risk_level = communities[risktype]
    risk_color = []
    if (risktype  == 'Risk Level'):
        # Create new labels / color map based on selected risktype and community
        newcomm_labels = communities[['Community', 'Risk Level']].apply(lambda x: ': '.join(x), axis=1)
        for i in risk_level:
            if i == 'None':
                risk_color.append(color_lu[risktype]['None'])
            if i == 'Low':
                risk_color.append(color_lu[risktype]['Low'])
            if i == 'Medium':
                risk_color.append(color_lu[risktype]['Medium'])
            if i == 'High':
                risk_color.append(color_lu[risktype]['High'])
    else:
        # Create new labels / color map based on selected risktype and community
        newcomm_labels = communities[['Community', risktype + ' Label']].apply(lambda x: ': '.join(x), axis=1)
        for i in risk_level:
            if i == 0:
                risk_color.append(color_lu[risktype]['None'])
            if i == 1:
                risk_color.append(color_lu[risktype]['Low'])
            if i == 2:
                risk_color.append(color_lu[risktype]['Medium'])
            if i == 3:
                risk_color.append(color_lu[risktype]['High'])


    map_communities_trace = go.Scattermapbox(
        lat=communities['Latitude'],
        lon=communities['Longitude'],
        mode='markers',
        marker={
            'size': 15,
            'color': risk_color
        },
        text=newcomm_labels,
        hoverinfo='text'
    )
    figure = {
        'data': [map_communities_trace],
        'layout': map_layout
    }
    return figure

# Update selected community based on map marker click
@app.callback(
    Output('community', 'value'),
    [
        Input('map', 'clickData'),
    ],
    [
        State('community', 'value')
    ]
)

def update_mine_site_dropdown(selected_on_map, comm_state):
    """ If user clicks on the map, update the drop down. """
    if selected_on_map is not None:
        # Return community name
        comm_val =  selected_on_map['points'][0]['text'].split(':')[0]
        if comm_val not in comm_state:
            comm_state.append(comm_val)
        return comm_state
    # Return a default
    return ['Nome']

# Update data table when new community is selected
@app.callback(
    [Output('community-table', 'data')],
    inputs=[
        Input('community', 'value')
    ]
)

def update_graph(community):
    commarray = {}
    if (type(community) == str):
        commarray = communities[communities['Community'] == community]
    else:
        for i, obj in enumerate(community):
            if i == 0:
                commarray = communities[communities['Community'] == obj]
            else:
                commarray = pd.concat([commarray,communities[communities['Community'] == obj]])
    return [commarray.to_dict('records')]

# Update main plot based on community selections
@app.callback(
    Output('weather-plot', 'figure'),
    inputs=[
        Input('community', 'value'),
        Input('risk_type', 'value')
    ]
)
def make_plot(community, risktype):
    figure = {}
    figure['data'] = []

    # Select ordering of columns
    hazard_lu = ['Massive Ice', 'Thaw Susceptibility', 'Existing Problems', 'Permafrost Occurrence','Permafrost Temperature', 'Risk Level' ]
    mult = 200.0
    marker_colors = ['#1D94A5','#2A697D','#AC8B53','#2F798E','#7F9EA3', '#EA906D']
    if risktype != 'Risk Level':
        for i in range(0,len(hazard_lu)):
            if hazard_lu[i] != risktype:
                marker_colors[i] = '#808080'


    for i in community:
        if type(community) == str: 
            df = communities[communities['Community'] == community].iloc[0]
        else:
            df = communities[communities['Community'] == i].iloc[0]
   
        marker_texts = []
        marker_size_vals = []
        for i in hazard_lu: 
            # Risk Level / Rating Score have different column rules
            if (i == 'Risk Level'):
                marker_texts.append('<b>' + df['Risk Level'] + '</b>')
                marker_size_vals.append(df['Rating Score'])
            else: 
                marker_texts.append('<b>' + df[i + ' Label'] + '</b>')
                marker_size_vals.append(df[i])


        if marker_size_vals[5] == 0:
            # Leave marker size if 0
            marker_size_vals[5] = 0
        else:
            # Normalize Risk Score from 0 - 3 from None, 6-15
            # 6-8 = Low, 9-12 = Medium, 13+ = High
            marker_size_vals[5] = math.ceil((marker_size_vals[5] - 5) / 3)
        marker_sizes = [x * 1.2 + 0.25 for x in marker_size_vals]

        # Create trace for each community, to fit on one line
        figure['data'].append({
            'x': hazard_lu,
            'y': [df['Community'], df['Community'], df['Community'], df['Community'], df['Community'], df['Community']],
            'name': df['Community'],
            'showlegend': False,
            'hovertext': marker_texts,
            'hovertemplate': "%{text}",
            'text': marker_texts,
            'textposition': 'center',
            'mode': 'markers+text',
            'marker': {
                'color': marker_colors,
                'size': marker_sizes,
                'sizeref': 0.05,
                'sizemode': 'scaled',
                'opacity': 0.6
            },
        })

    '''
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
    '''
    plot_height = 500
    #if (type(community) == list):
        #plot_height = 100 * len(community)
    layout = {
        'barmode': 'grouped',
        'hovermode': 'closest',
        'title': {
            'text': 'Community Permafrost Risks',
        },
	'height': plot_height,
	'yaxis': {
            'showline': 'false',
            'hoverformat': '1f'
	},
        'margin': {
            'b': 100,
            'l': 150
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
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', False)
    app.server.run(debug=debug, port=port, threaded=True)
