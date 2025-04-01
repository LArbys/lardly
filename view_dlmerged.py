#!/bin/env python3
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
import lardly.ubdl.det3d_viewer as det3d_viewer
import lardly.ubdl.det3d_truth_plot # register plotter
import lardly.ubdl.det3d_recoshower_plot # register plotter

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div( [
    io_nav_widget.make_ionavigation_widget(app),
    html.Hr(),
    wireplane_widget.make_imageplane_view_widget(app),
    html.Hr(),
    det3d_viewer.make_det3d_viewer(),    
    ])

wireplane_widget.register_dropdown_callback(app)
io_nav_widget.register_ionavigation_callbacks(app)
det3d_viewer.register_det3d_callbacks(app)



if __name__ == "__main__":
    app.run_server(port=8891,debug=True)
