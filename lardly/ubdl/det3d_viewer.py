import os,traceback
import dash
from dash import html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import lardly
import lardly.ubdl.det3d_plot_factory as det3d_plot_factory

def get_default_det3d_layout():

    axis_template = {
        "showbackground": True,
        "backgroundcolor": "rgb(255,255,255)",
        "gridcolor": "rgb(175, 175, 175)",
        "zerolinecolor": "rgb(175, 175, 175)"
    }

    plot3d_layout = {
        "title": "Detector View",
        "height":800,
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
        "font": {"size": 12, "color": "black"},
        "showlegend": False,
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

def make_default_plot():
    detdata = lardly.DetectorOutline()
    xtraces = detdata.getlines(color=(0,0,0))
    plot3d_layout = get_default_det3d_layout()
    return go.Figure(data=xtraces,layout=plot3d_layout)

def make_det3d_viewer():

    det3d_widget = html.Div( [
        html.H3('Detector Viewer'),
        html.Label('Plot Menu'),
        dcc.Checklist(options=[], value=[], id='det3d-viewer-checklist-plotchoices'),
        html.Button("Make 3D Plot", id='button-load-det3d-fig'),
        html.Div([html.Hr(),html.Label('Plot options'),html.Hr()],id='det3d-plot-options'),
        dcc.Graph(
            id="det3d",
            figure=make_default_plot(),
            config={"editable": True, "scrollZoom": True},
        )], className="graph__container")

    return det3d_widget

def register_det3d_callbacks(app):
    
    # callback for entry loading
    @app.callback(
        [Output('det3d','figure')],
        Input('button-load-det3d-fig','n_clicks'),
        [State('det3d-viewer-checklist-plotchoices','value')]
    )
    def run_active_det3d_plotters(n_clicks, selected_plots):
        print("Run active Det3D plotters")
        if len(selected_plots)==0:
            return [make_default_plot()]

        traces = det3d_plot_factory.make_det3d_traces( selected_plots )
        print("number of returned traces: ",len(traces))
        fig = make_default_plot()
        for plot in traces:
            #print(plot)
            fig.add_trace(plot)
        return [fig]
    
