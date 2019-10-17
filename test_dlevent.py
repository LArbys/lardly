from __future__ import print_function
import os,sys

import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import lardly
from lardly.ubdl import DLEvent

dlevt = DLEvent( "../ubdl/testdata/mcc9_v13_nueintrinsic_overlay_run1/complete/" )

traces2d,traces3d = dlevt.get_entry_data( 7 )

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
            figure={"data":traces2d[0],
                    "layout":{"height":800} }),
        dcc.Graph(
            id="image2d_plane1",
            figure={"data":traces2d[1],
                    "layout":{"height":800}}),
        dcc.Graph(
            id="image2d_plane2",
            figure={"data":traces2d[2],
                    "layout":{"height":800}}),
        ] ),
    ] )

if __name__ == "__main__":
    app.run_server(debug=True)

