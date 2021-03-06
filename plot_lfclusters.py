from __future__ import print_function
import os,sys,argparse

import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import numpy as np
import ROOT as rt
from larlite import larlite

color_by_options = ["ssnet","charge","prob","dead","cluster"]
colorscale = "Viridis"

treename = "pcacluster"
inputfile = "larflow_reco.root"

io = larlite.storage_manager( larlite.storage_manager.kREAD )
io.add_in_filename( inputfile )
io.open()

nentries = io.get_entries()
print("NENTRIES: ",nentries)

def make_figures(entry,plotby="ssnet"):
    print("making figures for entry={} plot-by={}".format(entry,plotby))
    global io
    io.go_to(entry)

    evclusters = io.get_data( larlite.data.kLArFlowCluster, treename )
    evpcaxis   = io.get_data( larlite.data.kPCAxis, treename )
    nclusters = evclusters.size()

    cluster_traces_v = []

    for icluster in xrange(nclusters):

        cluster = evclusters.at(icluster)
        nhits = cluster.size()
    
        pts = np.zeros( (nhits,4) )
        for idx in xrange(nhits):
            hit = cluster.at(idx)
            for i in range(3):
                pts[idx,i] = hit[i]
            if plotby=="ssnet":
                pts[idx,3] = hit.shower_score
            elif plotby in ["charge","dead"]:
                totq = 0.
                npix = 0
                for p in xrange(3):
                    if hit[3+p]>5:
                        totq += hit[3+p]
                        npix += 1
                if npix>0:
                    totq /= float(npix)
                if totq>150.0:
                    totq = 150.0
                elif totq<0:
                    totq = 0.0
                    
                if plotby=="charge":
                    pts[idx,3] = totq
                else:
                    if npix<3:
                        pts[idx,3] = 5.0
                    else:
                        pts[idx,3] = 10.0
            elif plotby=="prob":
                prob = hit[6]
                if prob<0.5:
                    prob *= 2.0
                pts[idx,3] = prob

        if plotby in ["ssnet","charge","prob","dead"]:
            colors = pts[:,3]
        elif plotby in ["cluster"]:
            r3 = np.random.randint(255,size=3)
            colors = "rgb(%d,%d,%d)"%( r3[0], r3[1], r3[2] )
        clusterplot = {
            "type":"scatter3d",
            "x":pts[:,0],
            "y":pts[:,1],
            "z":pts[:,2],
            "mode":"markers",
            "name":"[%d]"%(icluster),
            "marker":{"color":colors,"size":1,"colorscale":colorscale}
        }
        cluster_traces_v.append( clusterplot )

        # PCA-axis
        llpca = evpcaxis.at(icluster)

        pca_pts = np.zeros( (3,3) )
        for i in range(3):
            pca_pts[0,i] = llpca.getEigenVectors()[3][i]
            pca_pts[1,i] = llpca.getAvePosition()[i]
            pca_pts[2,i] = llpca.getEigenVectors()[4][i]
            
        pca_plot = {
            "type":"scatter3d",
            "x":pca_pts[:,0],
            "y":pca_pts[:,1],
            "z":pca_pts[:,2],
            "mode":"lines",
            "name":"pca[%d]"%(icluster),
            "line":{"color":"rgb(255,255,255)","size":2}
        }
        cluster_traces_v.append( pca_plot )

    return cluster_traces_v

def test():
    pass
    
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

axis_template = {
    "showbackground": True,
    #"backgroundcolor": "#141414", # black
    #"gridcolor": "rgba(255, 255, 255)",
    #"zerolinecolor": "rgba(255, 255, 255)",    
    "backgroundcolor": "rgba(100, 100, 100,0.5)",    
    "gridcolor": "rgb(50, 50, 50)",
    "zerolinecolor": "rgb(0, 0, 0)",
}

plot_layout = {
    "title": "",
    "height":800,
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 12, "color": "black"},
    "showlegend": False,
    #"plot_bgcolor": "#141414",
    #"paper_bgcolor": "#141414",
    "plot_bgcolor": "#ffffff",
    "paper_bgcolor": "#ffffff",
    "scene": {
        "xaxis": axis_template,
        "yaxis": axis_template,
        "zaxis": axis_template,
        "aspectratio": {"x": 1, "y": 1, "z": 3},
        "camera": {"eye": {"x": 1, "y": 1, "z": 1},
                   "up":dict(x=0, y=1, z=0)},
        "annotations": [],
    },
}

eventinput = dcc.Input(
    id="input_event",
    type="number",
    placeholder="Input Event")

plotopt = dcc.Dropdown(
    options=[
        {'label':'ssnet','value':'ssnet'},
        {'label':'charge','value':'charge'},
        {'label':'prob','value':'prob'},
        {'label':'cluster','value':'cluster'},
        {'label':'on dead channel','value':'dead'}],
    value='ssnet',
    id='plotbyopt',
    )
        

app.layout = html.Div( [
    html.Div( [ eventinput,
                plotopt,
                html.Button("Plot",id="plot")
    ] ),
    html.Hr(),
    html.Div( [
        dcc.Graph(
            id="det3d",
            figure={
                "data": [],
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )],
              className="graph__container"),
    html.Div(id="out")
] )

                       
@app.callback(
    [Output("det3d","figure"),
     Output("out","children")],
    [Input("plot","n_clicks")],
    [State("input_event","value"),
     State("plotbyopt","value"),
     State("det3d","figure")],
    )
def cb_render(*vals):
    if vals[1] is None:
        print("Input event is none")
        raise PreventUpdate
    if vals[1]>=nentries or vals[1]<0:
        print("Input event is out of range")
        raise PreventUpdate
    if vals[2] is None:
        print("Plot-by option is None")
        raise PreventUpdate

    cluster_traces_v = make_figures(int(vals[1]),plotby=vals[2])
    #print(cluster_traces_v)
    vals[-1]["data"] = cluster_traces_v
    return vals[-1],"event requested: {} {}".format(vals[1],vals[2])

if __name__ == "__main__":
    app.run_server(debug=True)
