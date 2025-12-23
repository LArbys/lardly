import os,sys

import json
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np

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

# TPC dimensions (cm)
TPC_X_MIN = 0.0      # Anode plane
TPC_X_MAX = 256.35   # Cathode plane
TPC_Y_MIN = -116.5   # Bottom
TPC_Y_MAX = 116.5    # Top
TPC_Z_MIN = 0.0      # Front
TPC_Z_MAX = 1036.8   # Back

def make_coordinate_axes(origin=(0, 0, 0), scale=80):
    """Create 3D coordinate axes with arrows at the origin."""
    ox, oy, oz = origin
    traces = []

    # X-axis (red) - drift direction
    traces.append({
        "type": "scatter3d",
        "x": [ox, ox + scale],
        "y": [oy, oy],
        "z": [oz, oz],
        "mode": "lines",
        "name": "X-axis",
        "line": {"color": "rgb(200,0,0)", "width": 8},
        "showlegend": False,
    })
    # X-axis arrowhead
    traces.append({
        "type": "cone",
        "x": [ox + scale],
        "y": [oy],
        "z": [oz],
        "u": [1],
        "v": [0],
        "w": [0],
        "sizemode": "absolute",
        "sizeref": 15,
        "anchor": "tip",
        "colorscale": [[0, "rgb(200,0,0)"], [1, "rgb(200,0,0)"]],
        "showscale": False,
        "showlegend": False,
    })

    # Y-axis (green) - vertical
    traces.append({
        "type": "scatter3d",
        "x": [ox, ox],
        "y": [oy, oy + scale],
        "z": [oz, oz],
        "mode": "lines",
        "name": "Y-axis",
        "line": {"color": "rgb(0,150,0)", "width": 8},
        "showlegend": False,
    })
    # Y-axis arrowhead
    traces.append({
        "type": "cone",
        "x": [ox],
        "y": [oy + scale],
        "z": [oz],
        "u": [0],
        "v": [1],
        "w": [0],
        "sizemode": "absolute",
        "sizeref": 15,
        "anchor": "tip",
        "colorscale": [[0, "rgb(0,150,0)"], [1, "rgb(0,150,0)"]],
        "showscale": False,
        "showlegend": False,
    })

    # Z-axis (blue) - beam direction
    traces.append({
        "type": "scatter3d",
        "x": [ox, ox],
        "y": [oy, oy],
        "z": [oz, oz + scale],
        "mode": "lines",
        "name": "Z-axis",
        "line": {"color": "rgb(0,0,200)", "width": 8},
        "showlegend": False,
    })
    # Z-axis arrowhead
    traces.append({
        "type": "cone",
        "x": [ox],
        "y": [oy],
        "z": [oz + scale],
        "u": [0],
        "v": [0],
        "w": [1],
        "sizemode": "absolute",
        "sizeref": 15,
        "anchor": "tip",
        "colorscale": [[0, "rgb(0,0,200)"], [1, "rgb(0,0,200)"]],
        "showscale": False,
        "showlegend": False,
    })

    return traces

def make_direction_arrow(start, direction, length=150, color="rgb(50,50,50)", name=""):
    """Create a direction arrow with label."""
    sx, sy, sz = start
    dx, dy, dz = direction
    # Normalize direction
    mag = np.sqrt(dx**2 + dy**2 + dz**2)
    dx, dy, dz = dx/mag, dy/mag, dz/mag

    end = (sx + dx*length, sy + dy*length, sz + dz*length)

    traces = []
    # Arrow line
    traces.append({
        "type": "scatter3d",
        "x": [sx, end[0]],
        "y": [sy, end[1]],
        "z": [sz, end[2]],
        "mode": "lines",
        "name": name,
        "line": {"color": color, "width": 6},
        "showlegend": False,
    })
    # Arrowhead
    traces.append({
        "type": "cone",
        "x": [end[0]],
        "y": [end[1]],
        "z": [end[2]],
        "u": [dx],
        "v": [dy],
        "w": [dz],
        "sizemode": "absolute",
        "sizeref": 12,
        "anchor": "tip",
        "colorscale": [[0, color], [1, color]],
        "showscale": False,
        "showlegend": False,
    })

    return traces

def make_anode_plane_mesh():
    """Create a semi-transparent mesh for the anode plane at x=0."""
    # Anode plane at x=0
    traces = []
    traces.append({
        "type": "mesh3d",
        "x": [TPC_X_MIN, TPC_X_MIN, TPC_X_MIN, TPC_X_MIN],
        "y": [TPC_Y_MIN, TPC_Y_MAX, TPC_Y_MAX, TPC_Y_MIN],
        "z": [TPC_Z_MIN, TPC_Z_MIN, TPC_Z_MAX, TPC_Z_MAX],
        "i": [0, 0],
        "j": [1, 2],
        "k": [2, 3],
        "color": "rgba(50, 50, 150, 0.3)",
        "name": "Anode Plane",
        "showlegend": False,
    })
    return traces

def make_cathode_plane_mesh():
    """Create a semi-transparent mesh for the cathode plane at x=256."""
    traces = []
    traces.append({
        "type": "mesh3d",
        "x": [TPC_X_MAX, TPC_X_MAX, TPC_X_MAX, TPC_X_MAX],
        "y": [TPC_Y_MIN, TPC_Y_MAX, TPC_Y_MAX, TPC_Y_MIN],
        "z": [TPC_Z_MIN, TPC_Z_MIN, TPC_Z_MAX, TPC_Z_MAX],
        "i": [0, 0],
        "j": [1, 2],
        "k": [2, 3],
        "color": "rgba(100, 100, 200, 0.2)",
        "name": "Cathode Plane",
        "showlegend": False,
    })
    return traces

def get_coordinate_annotations():
    """Create 3D annotations for coordinate system labels."""
    annotations = [
        # Axis labels
        dict(
            x=90, y=-20, z=-30,
            text="X",
            showarrow=False,
            font=dict(size=24, color="rgb(200,0,0)"),
        ),
        dict(
            x=-20, y=90, z=-30,
            text="Y",
            showarrow=False,
            font=dict(size=24, color="rgb(0,150,0)"),
        ),
        dict(
            x=-20, y=-20, z=90,
            text="Z",
            showarrow=False,
            font=dict(size=24, color="rgb(0,0,200)"),
        ),
        # Cathode plane label
        dict(
            x=TPC_X_MAX + 0, y=TPC_Y_MAX + 0, z=TPC_Z_MIN+20,
            text=f"x = +{TPC_X_MAX:.1f} cm<br>[cathode plane]",
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-70,
            font=dict(size=20, color="black"),
        ),
        # Anode plane label
        dict(
            x=TPC_X_MIN - 0, y=TPC_Y_MAX + 0, z=TPC_Z_MIN + 100,
            text=f"x = {TPC_X_MIN:.1f} cm [anode plane]<br>z = {TPC_Z_MIN:.1f} cm [front]",
            showarrow=True,
            arrowhead=2,
            ax=40,
            ay=-50,
            font=dict(size=20, color="black"),
        ),
        # Top label
        dict(
            x=TPC_X_MIN - 40, y=TPC_Y_MAX+20, z=TPC_Z_MAX/2,
            text=f"y = +{TPC_Y_MAX:.1f} cm [top]",
            showarrow=False,
            font=dict(size=20, color="black"),
        ),
        # Bottom label
        dict(
            x=TPC_X_MIN - 40, y=TPC_Y_MIN-20, z=TPC_Z_MAX/2,
            text=f"y = {TPC_Y_MIN:.1f} cm [bottom]",
            showarrow=False,
            font=dict(size=20, color="black"),
        ),
        # Back label
        dict(
            x=TPC_X_MAX/2, y=TPC_Y_MAX + 30, z=TPC_Z_MAX,
            text=f"z = +{TPC_Z_MAX:.1f} cm [back]",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-30,
            font=dict(size=20, color="black"),
        ),
        # Beam direction label
        dict(
            x=-60, y=-150, z=200,
            text="Beam direction",
            showarrow=False,
            font=dict(size=20, color="rgb(50,50,50)"),
        ),
        # Drift direction label
        dict(
            x=200, y=-150, z=-30,
            text="Drift direction",
            showarrow=False,
            font=dict(size=20, color="rgb(50,50,50)"),
        ),
        # Anode plane and PMTs label
        dict(
            x=TPC_X_MIN, y=TPC_Y_MIN - 30, z=TPC_Z_MAX + 50,
            text="Anode plane and PMTs",
            showarrow=True,
            arrowhead=2,
            ax=60,
            ay=40,
            font=dict(size=20, color="black"),
        ),
    ]
    return annotations

# Create all traces for the coordinate system figure
coord_axes = make_coordinate_axes(origin=(0, 0, 0), scale=70)
beam_arrow = make_direction_arrow(start=(-30, -130, 30), direction=(0, 0, 1), length=150,
                                   color="rgb(50,50,50)", name="Beam")
drift_arrow = make_direction_arrow(start=(240, -130, -30), direction=(-1, 0, 0), length=150,
                                    color="rgb(50,50,50)", name="Drift")
anode_mesh = make_anode_plane_mesh()
cathode_mesh = make_cathode_plane_mesh()


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

axis_template = {
    "showbackground": True,
    "backgroundcolor": "rgb(250,250,250)",
    "gridcolor": "rgb(200, 200, 200)",
    "zerolinecolor": "rgb(175, 175, 175)",
    "showgrid": True,
    "showline": True,
    "linecolor": "rgb(255, 255, 255)",
    "linewidth": 2,
}

plot_layout = {
    "title": dict(
        text="Figure 1: A cartoon depiction of the TPC coordinate system",
        x=0.5,
        y=0.02,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=16, color="black"),
    ),
    "height": 1200,
    "width": 2400,
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 20, "color": "black"},
    "showlegend": False,
    "plot_bgcolor": "rgb(255,255,255)",
    "paper_bgcolor": "rgb(255,255,255)",
    "scene": {
        "xaxis": dict(
            **axis_template,
            title="X (cm)",
            range=[-100, 350],
        ),
        "yaxis": dict(
            **axis_template,
            title="Y (cm)",
            range=[-200, 200],
        ),
        "zaxis": dict(
            **axis_template,
            title="Z (cm)",
            range=[-100, 1150],
        ),
        "aspectmode": "manual",
        "aspectratio": {"x": 0.45, "y": 0.4, "z": 1.25},
        "camera": {
            "eye": {"x": -1.5, "y": -1.2, "z": 0.8},
            "up": dict(x=0, y=1, z=0),
            "center": dict(x=0.1, y=0, z=0.1),
        },
        "annotations": get_coordinate_annotations(),
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

# Combine all traces for the coordinate system visualization
all_traces = (
    detlines +           # TPC outline
    pmtlines +           # PMT outlines
    coord_axes +         # X, Y, Z coordinate axes with arrows
    beam_arrow +         # Beam direction arrow
    drift_arrow +        # Drift direction arrow
    #anode_mesh +         # Semi-transparent anode plane
    cathode_mesh         # Semi-transparent cathode plane
)

app.layout = html.Div( [
    html.Div( [
        dcc.Graph(
            id="det3d",
            figure={
                "data": all_traces,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": True},
        )],
        className="graph__container"),
     ] )

if __name__ == "__main__":
    port = 8050
    app.run(port=port,debug=True)
