from __future__ import print_function
import os,sys

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

#input_larlite = sys.argv[1]
# input_larlite = "/home/jmills/workdir/michel_files/tracker_reco_Run000001-SubRun000586.root"
input_larlite = "/home/jmills/workdir/michel_files/tracker_reco_Run000001-SubRun000001.root"

input_mc =      "/home/jmills/workdir/michel_files/mcinfo-Run000001-SubRun000001.root"
# input_larcv   = "/home/jmills/workdir/michel_files/supera-Run000001-SubRun000586.root"
input_larcv   = "/home/jmills/workdir/michel_files/supera-Run000001-SubRun000001.root"

input_pgraph = "/home/jmills/workdir/michel_files/pgraph_file-Run000001-SubRun000001.root"
detdata = lardly.DetectorOutline()

entry = 12 
# LARLITE
io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( input_larlite )
io_ll.open()
io_ll.go_to(entry)

io_ll_mc = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll_mc.add_in_filename( input_mc )
io_ll_mc.open()
io_ll_mc.go_to(entry)



# TRACK
evtrack = io_ll.get_data(larlite.data.kTrack,"trackReco")
evmctrack = io_ll_mc.get_data(larlite.data.kMCTrack,"mcreco")
evmcshower = io_ll_mc.get_data(larlite.data.kMCShower,"mcreco")


print("number of tracks: ",evtrack.size())
track_v = [lardly.data.visualize_larlite_track( evtrack[i], color=(255,0,0) ) for i in range(evtrack.size())]

mctrack_v =  lardly.data.visualize_larlite_event_mctrack( evmctrack )
mcshower_v = [ lardly.data.visualize3d_larlite_mcshower( evmcshower.at(x) ) for x in range(evmcshower.size()) ]
# mctrack_v = lardly.data.visualize_larlite_event_mctrack( io_ll_mc.get_data(larlite.data.kMCTrack, "mcreco"))
# mcshower_v = lardly.data.visualize_larlite_event_mcshower( evmcshower )

# vtx_v =  [ lardly.data.visualize_larlite_track_vtx( evtrack[i] ) for i in range(evtrack.size())  ]
# end_v =  [ lardly.data.visualize_larlite_track_end( evtrack[i] ) for i in range(evtrack.size())  ]

# LARCV
io_cv = larcv.IOManager(larcv.IOManager.kREAD,"supera",larcv.IOManager.kTickBackward)
io_cv.add_in_file( input_larcv )
#io_cv.reverse_all_products()
io_cv.initialize()
io_cv.read_entry(entry)

io_pgraph_cv = larcv.IOManager(larcv.IOManager.kREAD)
io_pgraph_cv.add_in_file( input_pgraph )
io_pgraph_cv.initialize()
io_pgraph_cv.read_entry(entry)

# IMAGE2D
ev_img = io_cv.get_data( larcv.kProductImage2D, "wire" )
img2d_v = ev_img.Image2DArray()

# Vertex
ev_michel = io_pgraph_cv.get_data( larcv.kProductPGraph, "mc_decays")
print("number of decays: ",ev_michel.PGraphArray().size())
color_michel = [0,255,0] #green
michel_v =  lardly.data.visualize3d_larcv_pgraph( ev_michel, color_michel )
pgraph2d_michel = lardly.data.visualize2d_larcv_pgraph( ev_michel,None,  color=color_michel )


ev_good = io_pgraph_cv.get_data( larcv.kProductPGraph, "good_candidates_reco")
print("number of good candidates (multi counting): ",ev_good.PGraphArray().size())
color_good = [0,255,255] #teal
good_v =  lardly.data.visualize3d_larcv_pgraph( ev_good, color_good )
pgraph2d_good = lardly.data.visualize2d_larcv_pgraph( ev_good,None, color=color_good )

ev_bad = io_pgraph_cv.get_data( larcv.kProductPGraph, "bad_candidates_reco")
print("number of bad candidates (multi counting): ",ev_bad.PGraphArray().size())
color_bad_2d = [0,0,0] # black
color_bad_3d = [255,255,0] # black

bad_v =  lardly.data.visualize3d_larcv_pgraph( ev_bad, color_bad_3d )
pgraph2d_bad = lardly.data.visualize2d_larcv_pgraph( ev_bad,None, color=color_bad_2d )


# ev_pix = io_cv.get_data( larcv.kProductPixel2D, "allreco" )
# pix_meta_v = [ ev_pix.ClusterMetaArray(p) for p in range(3) ]
# pix_arr_v = [ ev_pix.Pixel2DClusterArray()[p] for p in range(3) ]
# pixtraces = [ lardly.data.visualize_larcv_pixel2dcluster( pix_arr_v[0][i], pix_meta_v[0][0] ) for i in range(pix_arr_v[0].size()) ]

# detdata = lardly.DetectorOutline()

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
                "data": detdata.getlines()+track_v+ mctrack_v + michel_v + mcshower_v + good_v + bad_v,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )],
              className="graph__container"),
    html.Div( [
        dcc.Graph(
            id="image2d_plane0",
            figure={"data":[ lardly.data.visualize_larcv_image2d( img2d_v[0] )]+ pgraph2d_michel[0]+ pgraph2d_good[0]+ pgraph2d_bad[0], #+pixtraces
                    "layout":{"height":800} }),
        dcc.Graph(
            id="image2d_plane1",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[1] )]+ pgraph2d_michel[1]+ pgraph2d_good[1]+ pgraph2d_bad[1],
                    "layout":{"height":800}}),
        dcc.Graph(
            id="image2d_plane2",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[2] )]+ pgraph2d_michel[0]+ pgraph2d_good[2]+ pgraph2d_bad[2],
                    "layout":{"height":800}}),
        ] ),
    ] )

if __name__ == "__main__":
    app.run_server(debug=True)
