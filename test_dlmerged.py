from __future__ import print_function
import os,sys,argparse

parser = argparse.ArgumentParser("test_3d lardly viewer w/ DL Merged File")
parser.add_argument("-i","--input-file",required=True,type=str,help="dlmerged file")
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

ientry = args.entry

HAS_TRACKS = True
HAS_PIXELS = False

# ======================================
# IO
# --
# LARLITE
io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( args.input_file )

# BONUS: larflow hits
if True:
    io_ll.add_in_filename( "../ubdl/testdata/mcc9_run3_bnb1e19/output_larmatch.root" )
    
io_ll.open()
io_ll.go_to(ientry)


# LARCV
io_cv = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickBackward)
io_cv.add_in_file( args.input_file )
io_cv.reverse_all_products()
io_cv.initialize()
io_cv.read_entry(ientry)

# ======================================
# TRACE CONTAINERS
traces3d = []
traces2d = {0:[],1:[],2:[]}

ev_adc = io_cv.get_data( larcv.kProductImage2D, "wire" )
img_v  = ev_adc.Image2DArray()

# VERTEX
if True:
    # vertices: 2d
    ev_pgraph = io_cv.get_data( larcv.kProductPGraph,  "test" )
    ev_pclust = io_cv.get_data( larcv.kProductPixel2D, "test_ctor" )
    print("Number of vertices: ",ev_pgraph.PGraphArray().size())

    pgraph_traces2d = lardly.data.visualize2d_larcv_pgraph( ev_pgraph, event_contour_pixels=ev_pclust )
    for p in range(3):
        traces2d[p] += pgraph_traces2d[p]

    # 3D vertices                                                                                                                                                                                       
    pgraph_traces3d = lardly.data.visualize3d_larcv_pgraph( ev_pgraph )

    traces3d += pgraph_traces3d

# PATICLE TRACK
if True:
    evtrack = io_ll.get_data(larlite.data.kTrack,"trackReco")
    print("number of tracks: ",evtrack.size())
    traces3d += [ lardly.data.visualize_larlite_track( evtrack[i], color=(125,255,255) ) for i in range(evtrack.size())  ]

    for itrack in range(evtrack.size()):
        track_traces = lardly.data.visualize2d_larlite_track( evtrack[itrack], img_v, color=(125,255,255) )
        for p in range(3):
            traces2d[p].append( track_traces[p] )

# SHOWER
if True:
    # 3D Showers
    ev_shower = io_ll.get_data( larlite.data.kShower, "showerreco" )
    print("number of showers (showerreco): ",ev_shower.size())
    shower_traces = [ lardly.data.visualize3d_larlite_shower( ev_shower.at(x) ) for x in range(ev_shower.size()) ]
    traces3d += shower_traces

    shower2d_traces = [ lardly.data.visualize2d_larlite_shower( ev_shower.at(x) ) for x in range(ev_shower.size()) ]
    for shower2d_trace in shower2d_traces:
        #print("shower trace: ",shower2d_trace)
        for p in range(3):
            traces2d[p].append( shower2d_trace[p] )

# COSMIC TRACKS
if True:
    ev_cosmics = io_ll.get_data(larlite.data.kTrack,"mergedthrumu3d")
    traces3d += [ lardly.data.visualize_larlite_track( ev_cosmics[i], color=(255,0,0) ) for i in range(ev_cosmics.size())  ]

# MCTRACK
if False:
    print("VISUALIZE MCTRACKS")
    mctrack_v = lardly.data.visualize_larlite_event_mctrack( io_ll.get_data(larlite.data.kMCTrack, "mcreco"))

# LARFLOW HITS
if True:
    print("Visualize LArFlow Hits")
    ev_lfhits_y2u = io_ll.get_data(larlite.data.kLArFlow3DHit,"larmatchy2u")
    ev_lfhits_y2v = io_ll.get_data(larlite.data.kLArFlow3DHit,"larmatchy2v")
    print("  num hits: y2u=",ev_lfhits_y2u.size()," y2v=",ev_lfhits_y2v.size())
    lfhits_v =  [ lardly.data.visualize_larlite_larflowhits( ev_lfhits_y2u, "larmatchy2u" ) ]
    lfhits_v += [ lardly.data.visualize_larlite_larflowhits( ev_lfhits_y2v, "larmatchy2v" ) ]
    traces3d += lfhits_v


# IMAGE2D
ev_img = io_cv.get_data( larcv.kProductImage2D, "wire" )
img2d_v = ev_img.Image2DArray()

if False:
    ev_pix = io_cv.get_data( larcv.kProductPixel2D, "allreco" )
    pix_meta_v = [ ev_pix.ClusterMetaArray(p) for p in range(3) ]
    pix_arr_v = [ ev_pix.Pixel2DClusterArray()[p] for p in range(3) ]
    pixtraces = [ lardly.data.visualize_larcv_pixel2dcluster( pix_arr_v[0][i], pix_meta_v[0][0] ) for i in range(pix_arr_v[0].size()) ]

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
        "aspectratio": {"x": 1, "y": 1, "z": 4},
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
