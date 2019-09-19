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
input_larlite = "output_dltagger_larlite.root"

io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( input_larlite )
io_ll.open()

io_ll.go_to(0)

evtrack = io_ll.get_data(larlite.data.kTrack,"dltagger_allreco")
print("number of tracks: ",evtrack.size())
track_v = [ lardly.data.visualize_larlite_track( evtrack[i] ) for i in xrange(evtrack.size())  ]

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


app.layout = html.Div(
    [
        dcc.Graph(
            id="brain-graph",
            figure={
                "data": detdata.getlines()+track_v,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )
    ],
    className="graph__container")

if __name__ == "__main__":
    app.run_server(debug=True)
