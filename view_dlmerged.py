from __future__ import print_function
import os,sys,argparse

import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import lardly
import lardly.ubdl.dlmerged_parsing as dlmerged_parsing
import lardly.ubdl.wireplane_widget as wireplane_widget
import lardly.ubdl.io_navigation_widget as io_nav_widget

axis_template = {
    "showbackground": True,
    "backgroundcolor": "rgb(255,255,255)",
    "gridcolor": "rgb(175, 175, 175)",
    "zerolinecolor": "rgb(175, 175, 175)",
}

def get_default_det3d_layout():
    plot3d_layout = {
        "title": "Detector View",
        "height":800,
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
        "font": {"size": 12, "color": "black"},
        "showlegend": False,
        #"plot_bgcolor": "#141414",
        #"paper_bgcolor": "#141414",
        #"plot_bgcolor": "rgb(255,255,255)",
        "paper_bgcolor": "rgb(255,255,255)",
        "scene": {
            "xaxis": axis_template,
            "yaxis": axis_template,
            "zaxis": axis_template,
            "aspectratio": {"x": 1, "y": 1, "z": 4},
            "camera": {"eye": {"x": -4.0, "y": 0.25, "z": 0.0},
                "center":{"x":0.0, "y":0.0, "z":0.0},
                "up":dict(x=0, y=1, z=0)},
            "annotations": [],
        },
    }
    return plot3d_layout


def update_det3d_plot( traces=[] ):
    detdata = lardly.DetectorOutline()
    xtraces = detdata.getlines(color=(0,0,0))
    if len(traces)>0:
        xtraces += traces

    plot3d_layout = get_default_det3d_layout()
    return go.Figure(data=xtraces,layout=plot3d_layout)

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div( [
    io_nav_widget.make_ionavigation_widget(app),
    html.Hr(),
    html.Div( [
        dcc.Graph(
            id="det3d",
            figure=update_det3d_plot(),
            config={"editable": True, "scrollZoom": False},
        )], className="graph__container"),
    html.Hr(),
    wireplane_widget.make_imageplane_view_widget(app),
    ])

wireplane_widget.register_dropdown_callback(app)
io_nav_widget.register_ionavigation_callbacks(app)



if __name__ == "__main__":
    app.run_server(port=8888,debug=True)
