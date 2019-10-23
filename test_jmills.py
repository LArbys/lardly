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
input_larlite = "/home/jmills/workdir/michel_files/tracker_reco_0.root"
input_larcv   = "/home/jmills/workdir/michel_files/output_dltagger_larcv_masked.root"
entry = 2
# LARLITE
io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( input_larlite )
io_ll.open()
io_ll.go_to(entry)



# TRACK
evtrack = io_ll.get_data(larlite.data.kTrack,"trackReco")

print("number of tracks: ",evtrack.size())
track_v = [ lardly.data.visualize_larlite_track( evtrack[i] ) for i in range(evtrack.size())  ]
vtx_v =  [ lardly.data.visualize_larlite_track_vtx( evtrack[i] ) for i in range(evtrack.size())  ]
end_v =  [ lardly.data.visualize_larlite_track_end( evtrack[i] ) for i in range(evtrack.size())  ]

# LARCV
io_cv = larcv.IOManager(larcv.IOManager.kREAD)
io_cv.add_in_file( input_larcv )
io_cv.initialize()
io_cv.read_entry(entry)

# IMAGE2D
ev_img = io_cv.get_data( larcv.kProductImage2D, "wire_masked" )
img2d_v = ev_img.Image2DArray()

# Vertex
evpgraph = io_cv.get_data( larcv.kProductPGraph, "bragg_vertex")
print("number of vertices: ",evpgraph.PGraphArray().size())
bragg_v = [ lardly.data.visualize3d_larcv_pgraph( evpgraph )  ]


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
                "data": track_v + bragg_v + vtx_v + end_v,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )],
              className="graph__container"),
    html.Div( [
        dcc.Graph(
            id="image2d_plane0",
            figure={"data":[ lardly.data.visualize_larcv_image2d( img2d_v[0] )], #+pixtraces
                    "layout":{"height":800} }),
        dcc.Graph(
            id="image2d_plane1",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[1] )],
                    "layout":{"height":800}}),
        dcc.Graph(
            id="image2d_plane2",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[2] )],
                    "layout":{"height":800}}),
        ] ),
    ] )

if __name__ == "__main__":
    app.run_server(debug=True)
