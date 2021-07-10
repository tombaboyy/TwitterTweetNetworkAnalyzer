# -*- coding: utf-8 -*-
"""
@author: Tomi Räsänen
"""

import tweepy
import json
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import get_tweetss as gw
from graph_functions import form_edges
from graph_functions import make_grap
from graph_functions import data_man
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from textwrap import dedent as d

#pio.renderers.default='browser'

# Authentication

consumer_key = ''
consumer_secret = ''
access_token= ''
access_token_secret= ''

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)

""" This function was found on the internet. I can't remember the site"""
def make_plot(G,nodes):
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = nodes[edge[0]]
        x1, y1 = nodes[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = nodes[node]
        node_x.append(x)
        node_y.append(y)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Electric',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Käyttäjän yhteydet',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))        
        node_text.append('Nimi: '+ str(adjacencies[0].split(",")[0]) + " -- " + 
                        'Yhteyksiä: ' + str(len(adjacencies[1])))
    
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text
    figure = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="@Tomi Räsänen",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    )

    
        
    return figure

def form_table(G):
    list_ed = sorted(G.degree, key=lambda x: x[1], reverse=True)
    new_list = []
    for n,i in enumerate(list_ed):
        name = i[0].split(",")[0]
        new_list.append((name,i[1]))
    table = pd.DataFrame(new_list, columns=['Nimi', 'Yhteydet'])
    five_table = table.head(13)
    return five_table

INFO = ""

def more_info(data,user_nam):
    i = 0
    for nam in data["user"]:
        if nam["screen_name"] == user_nam:
            break
        else:
            i = i + 1
    user_name = data.loc[i,"user"]["name"]
    desc = data.loc[i,"user"]["description"]
    followers = data.loc[i,"user"]["followers_count"]
    following = data.loc[i,"user"]["friends_count"]
    Info = '----------------\n Oikea nimi: \t {} \n ----------------\nProfiiliteksti: \t {} \n ----------------\nSeuraajat: \t {} \n ----------------\n\
    Seuraa: \t {} \n'.format(user_name,desc,followers,following)
    return Info

SRC = ""
pf = pd.read_json("tweets.json")
data_for_edges = form_edges(pf)
good_data = data_man(data_for_edges)

G = nx.Graph()
G = make_grap(data_for_edges, G)

table_df = form_table(G)
nodes = nx.spring_layout(G)
fig = make_plot(G, nodes)


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#figure = {}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Sosiaalinen verkosto '{}' - Twitter".format(gw.HAKUSANA)


app.layout = html.Div([
    
    html.Div([html.H1("Sosiaalinen verkosto '{}' - Twitter".format(gw.HAKUSANA))],
             className="row",
             style={'textAlign': "center"}),
    
    html.Div(
        className="row",
        children=[
            html.Div(
                className="eight columns",
                children=[dcc.Graph(id="network_graph",
                                    figure=fig)],
            ),
            html.Div(
                className="four columns",
                children=[
                        html.Div(
                        className='four rows',
                        children=[
                            dcc.Markdown(d("""
                            **Suosituimmat käyttäjät**
                            """)),
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i} for i in table_df.columns],
                                data=table_df.to_dict('records'),
                            )
                        ]
                    ),
                    html.Div(
                        className='columns',
                        children=[
                            html.Pre(id='click-data')
                        ]
                    )
                ]
            )                               
        ]
    ),
   html.Div(id='textarea-output', style={'whiteSpace': 'pre-line'})
    
])                                  
#style=styles['pre']
@app.callback(
    dash.dependencies.Output('click-data', 'children'),
    [dash.dependencies.Input('network_graph', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        dash.no_update
    else:
        ctx = dash.callback_context
        jeeson = json.dumps(ctx.triggered[0]["value"])
        nimi = jeeson.split(",")[5].split("--")[0].split("i:")[1].strip()
        
        try:
            show_data = json.dumps({nimi: good_data[nimi]}, indent=2)    
            return show_data
        except KeyError:
            return "Ei twiittejä"

@app.callback(
    dash.dependencies.Output('textarea-output', 'children'),
    [dash.dependencies.Input('network_graph', 'clickData')])            
def update_output(clickData):
    if clickData is None:
        dash.no_update
    else:
        ctx = dash.callback_context
        jeeson = json.dumps(ctx.triggered[0]["value"])
        nimi = jeeson.split(",")[5].split("--")[0].split("i:")[1].strip()
        return more_info(pf,nimi)


# This run the dash app
if __name__ == '__main__':
    app.run_server(debug=False)
    




