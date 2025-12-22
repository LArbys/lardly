import os,sys

import json
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import lardly
#from lardly.detectormesh import DetectorDisplay
from lardly.detectoroutline import DetectorOutline
from lardly.ubdl.ubplot_opdet import make_opdet_plot, make_opdet_outline_plot

#detdisplay = DetectorDisplay()
detoutline = DetectorOutline()

#dettraces  = detdisplay.getmeshdata()
detlines   = detoutline.getlines(color=(0,0,0))

empty_pmt_values = [1.0]*32
pmtlines   = make_opdet_outline_plot( )


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

axis_template = {
    "showbackground": True,
    "backgroundcolor": "rgb(245,245,245)",
    "gridcolor": "rgb(20, 20, 20)",
    "zerolinecolor": "rgb(0, 0, 0)",
}

plot_layout = {
    "title": "",
    "height":800,
    "margin": {"t": 10, "b": 10, "l": 10, "r": 10},
    "font": {"size": 16, "color": "black"},
    "showlegend": False,
    "plot_bgcolor": "rgb(100,100,100)",
    "paper_bgcolor": "rgb(255,255,255)",
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
                "data":detlines+pmtlines,
                "layout":plot_layout,
            },
            config={"editable": True, "scrollZoom": True},
        )],
        className="graph__container"),
     ] )

if __name__ == "__main__":
    port = 8050
    app.run(port=port,debug=True)
