import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go 

###LOAD IN DATA

#Q1: species, borough, health
soql_url_1 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,boroname,health,count(spc_common)' +\
        '&$group=spc_common,boroname,health')

all_trees_1 = pd.read_json(soql_url_1 + '&$limit=1818') #1818 utilized after discovering it to be incoming observation #
t1 = all_trees_1.dropna() #drop NA values
t1 = t1.rename(columns={"spc_common": "species", "boroname": "borough", "count_spc_common": "count"}) #rename cols

#Q2: species, borough, health, steward
soql_url_2 = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,boroname,health,steward,count(spc_common)' +\
        '&$group=spc_common,boroname,health,steward')

all_trees_2 = pd.read_json(soql_url_2 + '&$limit=4554') #4554 utilized after discovering it to be incoming observation #
t2 = all_trees_2.dropna() #drop NA values
t2 = t2.rename(columns={"spc_common": "species", "boroname": "borough", "count_spc_common": "count"}) #rename cols

# #Update the value of steward for later comparison so that we sort for whether a tree did or did not have a caretaker
t2.loc[t2['steward'] == 'None', ['steward']] = 'no'

#sum count for observations with stewards
#update steward value to 'yes'
t2.loc[t2['steward'] == '1or2', ['steward']] = 'yes'
t2.loc[t2['steward'] == '3or4', ['steward']] = 'yes'
t2.loc[t2['steward'] == '4orMore', ['steward']] = 'yes'

#print(t2.head()) #verified
#print(t2.steward.unique()) #'None', '1or2','3or4','4orMore'

###......................................................................................###


###FILTER & PLOT [ISOLATED TEST]

#Q1: test filtering with borough and species to plot count vs. health
#borough = 'Bronx'
#species = 'London planetree'
#dff = t1[(t1['borough'] == borough) & (t1['species'] == species)] #filter works :)

#Verify and plot output
#print(dff.head()) #verify
#fig = px.bar(dff, x='health', y='count', 
# category_orders={"health": ["Poor", "Fair", "Good"]}, # replaces default order by column name
# title='Health Ratings of London planetrees in Queens')
#fig.show()

#Q2: test filtering with borough and species to plot count vs. health colored by stewardship
# borough = 'Bronx'
# species = 'London planetree'
# dff_y = t2[(t2['steward'] == 'yes')] 
# dff_n = t2[(t2['steward'] == 'no')]
# dff_y = dff_y[(dff_y['borough'] == borough) & (dff_y['species'] == species)]
# dff_n = dff_n[(dff_n['borough'] == borough) & (dff_n['species'] == species)]

#print(dff_y.head())
#print(dff_n.head())

#Verify and plot output as stacked bar chart
#fig2 = px.bar(dff2, x='health', y='count', color='steward', title='Health Ratings of London planetrees in Queens') #not informative or clear enough
#fig2.show()

#Verify and plot output as subplot donut charts
# fig2 = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
# fig2.add_trace(go.Pie(labels=dff_y['health'], values=dff_y['count'], name='With a Steward'), 1, 1)
# fig2.add_trace(go.Pie(labels=dff_n['health'], values=dff_n['count'], name='No Steward'), 1, 2)

# fig2.update_traces(hole=.4, hoverinfo="label+value+name")

# fig2.update_layout(
#      title_text="Measuring the Effect of Stewardship on Health Ratings of London planetrees in Queens",
#      # Add annotations in the center of the donut pies.
#      annotations=[dict(text='Steward', x=0.19, y=0.5, font_size=20, showarrow=False),
#                   dict(text='No Steward', x=0.83, y=0.5, font_size=20, showarrow=False)])
# fig2.show()

###......................................................................................###


###DASH APP

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

available_boroughs = t1['borough'].unique()
available_species = t1['species'].unique()

app.layout = html.Div(children=[
    html.H1(children = 'NYC Tree Health and Effects of Stewardship'),
    html.P(children = 'Based on 2015 Street Tree Census Tree Data downloaded from the city of New York, tree health and stewardship effect plots are produced after selecting the New York City borough and tree species of interest. The default borough is the Bronx and the default species is American beech (as shown below).'),
    html.P(children = 'Select a borough:'),
    dcc.Dropdown(
        id='borough',
        options=[{'label': b, 'value': b} for b in available_boroughs],
        value=available_boroughs[0] #default
    ),
    html.Div(id='dd-borough'),
    
    html.P(children = 'Select a tree species:'),
    dcc.Dropdown(
        id='species',
        options=[{'label': s, 'value': s} for s in available_species],
        value=available_species[0] #default
    ),
    #Q1
    html.Div(id='health-app'),
    html.H2(children = 'Proportion of Trees in Poor vs. Fair vs. Good Health'),
    dcc.Graph(id='health-bar'),
    #Q2
    html.Div(id='steward-app'),
    html.H2(children = 'Impact of Stewardship on Health of Trees'),
    dcc.Graph(id='steward-pie'),
    html.P(children = 'We can utilize displayed percentages as a stewardship effectiveness diagnostic (ie. does `Steward` have a higher proportion of trees in Good health and/or a lower proportion of trees in Poor health than `No Steward`?).'),

])

#Q1 Dash App Portion

@app.callback(
    dash.dependencies.Output('health-bar', 'figure'), 
    [dash.dependencies.Input('borough', 'value')], 
    [dash.dependencies.Input('species', 'value')]
)

def health_app(borough, species):
    #filter for proper data
    dff = t1[(t1['borough'] == borough) & (t1['species'] == species)] #filter works :)
    
    #display corresponding count vs. health
    fig = px.histogram(dff, x='health', y='count', category_orders={"health": ["Poor", "Fair", "Good"]}, opacity=0.8)
    fig.update_xaxes(type='category', title_text='Tree Health')
    fig.update_yaxes(title_text='Number of Trees')
    return fig

#Q2 Dash App Portion

@app.callback(
    dash.dependencies.Output('steward-pie', 'figure'), 
    [dash.dependencies.Input('borough', 'value')], 
    [dash.dependencies.Input('species', 'value')]
)

def species_app(borough, species):
    #filter for proper data
    dff_y = t2[(t2['borough'] == borough) & (t2['species'] == species) & (t2['steward'] == 'yes')] #filter works :)
    dff_n = t2[(t2['borough'] == borough) & (t2['species'] == species) & (t2['steward'] == 'no')] #filter works :)
    
    #Verify and plot output as subplot donut charts
    ##attempts to vary color scheme did not work (consistently)

    fig2 = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
    fig2.add_trace(go.Pie(labels=dff_y['health'], values=dff_y['count'], name='With a Steward',  opacity=0.8), 1, 1)
    fig2.add_trace(go.Pie(labels=dff_n['health'], values=dff_n['count'], name='No Steward', opacity=0.8), 1, 2)
    
    fig2.update_traces(hole=.4, hoverinfo="label+value+name", marker=dict(line=dict(color='#000000', width=1)))

    fig2.update_layout(
        annotations=[dict(text='Steward', x=0.19, y=0.5, font_size=15, showarrow=False),
        dict(text='No Steward', x=0.82, y=0.5, font_size=15, showarrow=False)])
        
    return fig2

if __name__ == '__main__':
       app.run_server(debug=False)

#References
#1. Subplot donut charts: https://plotly.com/python/pie-charts/
#2. Multi page apps: https://dash.plotly.com/urls 