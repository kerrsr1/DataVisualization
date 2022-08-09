# AnimalShelterVisualization.py
#
# Created by Sarah Kerr for CS340 - Client/Server Development
# Created on Jupyter Notebook
#
# This is the framework for the data visualization program. It will
# display a chart populated with the data. Below that, a pie chart
# is displayed next to a geolocation map that displays the location
# of any given data point that the user selects on the chart. Radio
# buttons are located above the chart and allow the user to perform
# pre-defined queries on the database.


from jupyter_plotly_dash import JupyterDash

import dash
import dash_leaflet as dl
from dash import dcc
from dash import html
import plotly.express as px
from dash import dash_table as dt
from dash.dependencies import Input, Output, State

import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from bson.json_util import dumps

import base64

from animal_shelter_crud import AnimalShelter

###########################
# Data Manipulation / Model
###########################
username = "aacuser"
password = "1a2b3c"
shelter = AnimalShelter(username, password)

# reads the data into Pandas dataframe
df = pd.DataFrame.from_records(shelter.read_all({}))

#########################
# Dashboard Layout / View
#########################
app = JupyterDash('Dash DataTable Only')

image_filename = 'Grazioso Salvare Logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read()) #base64 used to allow proper data transfer

app.layout = html.Div([
    html.Center(html.B(html.H1('Animal Shelter Dashboard - Sarah Kerr'))),
    html.Hr(),
    # customer image with link to homepage that opens in new browser tab
    html.A([
        html.Img(
            id='customer-image',
            src='data:image/png;base64,{}'.format(encoded_image.decode()),
            alt='customer image',
            style={
                'height': '10%', 
                'width': '10%',
                'display': 'block',
                'margin-left': 'auto',
                'margin-right': 'auto'
            }),
        ], href='http://www.snhu.edu', target='_blank'),
    html.Div([
        html.Label(['Disaster Rescue Dog Type'], style={'font-weight': 'bold'}),
        #These are the radio buttons the user can click on. Default is 'Reset'
        dcc.RadioItems(
            id='Rescue_Type',
            options=[
                {'label': 'Water Rescue', 'value': 'Water'},
                {'label': 'Mountain or Wilderness Rescue', 'value': 'MountainWilderness'},
                {'label': 'Disaster or Individual Tracking', 'value': 'DisasterOrTracking'},
                {'label': 'Reset', 'value': 'Reset'}
            ],
            value = 'Reset'),
        ]),
    html.Br(),
    # This is the table that displays all fields for each document matching query
    dt.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns
        ],
        data=df.to_dict('records'), # Data is read as Python dictionary
        editable=False,
        sort_action="native",
        sort_mode="multi",
        column_selectable=False,
        row_selectable=False,
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.Br(),
    html.Br(),
    #Sets up the dashboard so that the piechart and geolocation chart are side-by-side
     html.Div(className='row',
         style={'display' : 'flex'},
             children=[
        html.Div(
            dcc.Graph(
                id='pie_chart',
                className='col s12 m6',
                )
            ),
        html.Div(
            id='map-id',
            className='col s12 m6',
            )
        ])    
])

@app.callback(Output('pie_chart', 'figure'),
              [Input('datatable-interactivity', 'data')]
              )
def generate_pie_chart(data):
    """
    Generates a pie chart showing percentage of fields matching query data.
    
    Parameters:
        data (dict): Documents are contained in Python dictionary.
        
    Returns:
        fig (Plotly graph object): The Plotly pie chart.
    """
    dff = pd.DataFrame.from_dict(data) #Takes data from updated table using Pandas
    
    fig = px.pie(dff, title='Breeds Matching Criteria', names='breed')
    return fig
    
@app.callback(Output('datatable-interactivity',"data"), 
              [Input('Rescue_Type', 'value')]
              )
def radio_button_section(button):
    """
    User interactive buttons for database visualization.
    
    Selecting a button will update the data table, pie chart, and geolocation chart with the
    matching documents.
    
    Parameters:
        button (Plotly RadioItem): Represents the radio button the user selected.
    
    Returns:
        dff (dict) : Resulting documents contained in Pyton dictionary.
    """              
    dff = df #make copy of dataframe (so as not to work with global object)
    
    if button == 'Water':
        
        dff = pd.DataFrame.from_records(shelter.read_all({
            'animal_type': 'Dog',
            'sex_upon_outcome': 'Intact Female',
            'age_upon_outcome_in_weeks':{'$gt': 25, '$lt': 157},
            'breed': {'$regex': 'Labrador Retriever|Chesapeake Bay Retriever|Newfoundland'}
        }))
    
    elif button == 'MountainWilderness':
        dff = pd.DataFrame.from_records(shelter.read_all({
            'animal_type': 'Dog',
            'sex_upon_outcome': 'Intact Male',
            'age_upon_outcome_in_weeks':{'$gt': 25, '$lt': 157},
            'breed': {'$regex': 'German Shepherd|Alaskan Malamute|Old English Sheepdog|Siberian Husky|Rottweiler'}
        }))
        
    elif button == 'DisasterOrTracking':
        dff = pd.DataFrame.from_records(shelter.read_all({
            'animal_type': 'Dog',
            'sex_upon_outcome': 'Intact Male',
            'age_upon_outcome_in_weeks':{'$gt': 29, '$lt': 301},
            'breed': {'$regex': 'Doberman Pinscher|German Shepherd|Golden Retriever|Bloodhound|Rottweiler'} 
         }))
              
    elif button == 'Reset':
        dff = pd.DataFrame.from_records(shelter.read_all({}))
         
    return dff.to_dict('records')

@app.callback(
    Output('map-id', "children"),
    [Input('datatable-interactivity', "derived_viewport_data")])
def update_map(viewData):
    """
    Geolocation map that updates based on what document user has clicked on from the data table.
    
    Parameters:
        viewData: The document user has selected by clicking on a row on the data table. Default is 
        document in the first row.
        
    Returns: 
        dl.Map: The map is updated with a marker on the selected data point.
    """
    dff = pd.DataFrame.from_dict(viewData)
    # Austin TX is at [30.75,-97.48]
    return [
        dl.Map(style={'width': '1000px', 'height': '500px'}, center=[30.75,-97.48], zoom=12, children=[
            dl.TileLayer(id="base-layer-id"),
            # Marker with tool tip and popup
            dl.Marker(position=[(dff.iloc[1,13]),(dff.iloc[1,14])], children=[
                dl.Tooltip(dff.iloc[0,4]),
                dl.Popup([
                    html.H3("Animal Name"),
                    html.P(dff.iloc[0,9]),
                    html.H3("Animal Type"),
                    html.P(dff.iloc[0,3]),
                    html.H3("Animal Breed"),
                    html.P(dff.iloc[0,4]),
                    html.H3("Coordinates"),
                    html.P(dff.iloc[0,13]),
                    html.P(dff.iloc[0,14])
                ])
            ])
        ])
    ]

app