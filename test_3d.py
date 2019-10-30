from __future__ import print_function
import os,sys,argparse

parser = argparse.ArgumentParser("test_3d lardly viewer")
parser.add_argument("-ll","--larlite",required=True,type=str,help="larlite file with dltagger_allreco tracks")
parser.add_argument("-lcv","--larcv",required=True,type=str,help="larcv with 'wire' images")
parser.add_argument("-mct","--mctrack",type=str,default="",help="larlite mcinfo file")
parser.add_argument("-e","--entry",required=True,type=int,help="Entry to load")

args = parser.parse_args(sys.argv[1:])

import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from larlite import larlite
from larcv import larcv
import lardly


input_larlite = args.larlite
input_larcv   = args.larcv
ientry        = args.entry

HAS_TRACKS = True
HAS_PIXELS = False

# LARLITE
io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( input_larlite )
io_ll.open()
io_ll.go_to(ientry)


traces3d = []
traces2d = {0:[],1:[],2:[]}

# TRACK
if HAS_TRACKS:
    #evtrack = io_ll.get_data(larlite.data.kTrack,"dltagger_allreco")
    evtrack = io_ll.get_data(larlite.data.kTrack,"trackReco")
    print("number of tracks: ",evtrack.size())
    track_v = [ lardly.data.visualize_larlite_track( evtrack[i], track_id=i ) for i in range(evtrack.size())  ]
    traces3d += track_v

# MCTRACK
if args.mctrack!="":
    print("VISUALIZE MCTRACKS")
    mctrack_v = lardly.data.visualize_larlite_event_mctrack( io_ll.get_data(larlite.data.kMCTrack, "mcreco"))
    traces3d += mctrack_v

# LARCV
io_cv = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickBackward)
io_cv.add_in_file( input_larcv )
io_cv.reverse_all_products()
io_cv.initialize()
io_cv.read_entry(ientry)

# IMAGE2D
ev_img = io_cv.get_data( larcv.kProductImage2D, "wire" )
img2d_v = ev_img.Image2DArray()

if HAS_PIXELS:
    ev_pix = io_cv.get_data( larcv.kProductPixel2D, "allreco" )
    pix_meta_v = [ ev_pix.ClusterMetaArray(p) for p in range(3) ]
    pix_arr_v = [ ev_pix.Pixel2DClusterArray()[p] for p in range(3) ]
    pixtraces = [ lardly.data.visualize_larcv_pixel2dcluster( pix_arr_v[0][i], pix_meta_v[0][0] ) for i in range(pix_arr_v[0].size()) ]

if HAS_TRACKS:
    for itrack in range(evtrack.size()):
        print("track[%d] len=%d"%(itrack,evtrack[itrack].NumberTrajectoryPoints()))
        track_traces = lardly.data.visualize2d_larlite_track( evtrack[itrack], img2d_v, color=(125,255,255), track_id=itrack )
        for p in range(3):
            traces2d[p].append( track_traces[p] )
            

detdata = lardly.DetectorOutline()

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

axis_template = {
    "showbackground": True,
    "backgroundcolor": "#141414",
    "gridcolor": "rgb(255, 255, 255)",
    "zerolinecolor": "rgb(255, 255, 255)",
}

plot_layout = {
    "title": "",
    "height":800,
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 12, "color": "white"},
    "showlegend": False,
    "plot_bgcolor": "#141414",
    "paper_bgcolor": "#141414",
    "scene": {
        "xaxis": axis_template,
        "yaxis": axis_template,
        "zaxis": axis_template,
        "aspectratio": {"x": 2, "y": 1, "z": 4},
        "camera": {"eye": {"x": 2, "y": 2, "z": 2},
                   "up":dict(x=0, y=1, z=0)},
        "annotations": [],
    },
}

testline = {
    "type":"scattergl",
    "x":[200,400,400,800],
    "y":[3200,3400,3800,4400],
    "mode":"markers",
    #"line":{"color":"rgb(255,255,255)","width":4},
    "marker":dict(size=10, symbol="triangle-up",color="rgb(255,255,255)"),
    }

app.layout = html.Div( [
    html.Div( [
        dcc.Graph(
            id="det3d",
            figure={
                "data": detdata.getlines()+traces3d,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )],
              className="graph__container"),
    html.Div( [
        dcc.Graph(
            id="image2d_plane0",
            figure={"data":[ lardly.data.visualize_larcv_image2d( img2d_v[0] )]+traces2d[0],
                    "layout":{"height":800} }),
        dcc.Graph(
            id="image2d_plane1",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[1] )]+traces2d[1],
                    "layout":{"height":800}}),
        dcc.Graph(
            id="image2d_plane2",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[2] )]+traces2d[2],
                    "layout":{"height":800}}),
        ] ),
    ] )

if __name__ == "__main__":
    app.run_server(debug=True)
