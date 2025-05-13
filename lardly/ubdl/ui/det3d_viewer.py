"""
Detector 3D Viewer component

This module provides the Detector 3D Viewer component and related functions.
"""
import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

from lardly.ubdl.plotters.registry import registry, get_applicable_plotters
from lardly.ubdl.core.state import state_manager
from lardly.ubdl.config.settings import config
import lardly.ubdl.utils.detectoroutline as detector_utils

def get_default_det3d_layout():
    """
    Get the default layout for the 3D detector view
    
    Returns:
        Default layout dictionary for Plotly
    """
    axis_template = {
        "showbackground": True,
        "backgroundcolor": "rgb(255,255,255)",
        "gridcolor": "rgb(175, 175, 175)",
        "zerolinecolor": "rgb(175, 175, 175)"
    }

    layout = {
        "title": "Detector View",
        "height": config.get("plot", "default_layout", "height", default=800),
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
        "font": {"size": 12, "color": "black"},
        "showlegend": False,
        "paper_bgcolor": "rgb(255,255,255)",
        "scene": {
            "xaxis": axis_template,
            "yaxis": axis_template,
            "zaxis": axis_template,
            "aspectratio": config.get("plot", "default_layout", "aspect_ratio", 
                                    default={"x": 1, "y": 1, "z": 4}),
            "camera": {"eye": {"x": -4.0, "y": 0.25, "z": 0.0},
                      "center": {"x": 0.0, "y": 0.0, "z": 0.0},
                      "up": {"x": 0, "y": 1, "z": 0}},
            "annotations": [],
        },
    }
    return layout

def make_default_plot():
    """
    Create a default plot with detector outline
    
    Returns:
        Plotly Figure object with detector outline
    """
    detdata = detector_utils.DetectorOutline()
    xtraces = detdata.get_lines(color=(0, 0, 0))
    return go.Figure(data=xtraces, layout=get_default_det3d_layout())

def make_det3d_viewer():
    """Create the detector 3D viewer component"""
    return html.Div([
        html.Div(id='det3d-hidden-output', style={'display': 'none'}),  # Hidden div for callbacks
        
        html.H3('Detector Viewer'),
        html.Label('Plot Menu'),
        dcc.Checklist(
            id='det3d-viewer-checklist-plotchoices',
            options=[],
            value=[],
        ),
        html.Button("Make 3D Plot", id='button-load-det3d-fig'),
        html.Div(
            id='det3d-plot-options',
            children=[html.Hr(), html.Label('Plot options'), html.Hr()],
        ),
        dcc.Graph(
            id="det3d",
            figure=make_default_plot(),
            config={"editable": True, "scrollZoom": True},
        )
    ], className="graph__container")

def register_det3d_callbacks(app):
    """Register callbacks for the detector 3D viewer"""
    
    # Update plot options when selected plotters change
    @app.callback(
        Output('det3d-plot-options', 'children'),
        [Input('det3d-viewer-checklist-plotchoices', 'value')]
    )
    def update_plot_options(selected_plots):
        """Update plot options based on selected plotters"""
        if not selected_plots:
            return [html.Hr(), html.Label('Plot options'), html.Hr()]
        
        all_option_widgets = [html.Hr(), html.Label('Plot options'), html.Hr()]
        
        from lardly.ubdl.plotters.registry import registry
        
        for plot_name in selected_plots:
            plotter = registry.get_plotter(plot_name)
            if plotter:
                # Get option widgets from the plotter
                plotter_widgets = plotter.make_option_widgets()
                if plotter_widgets:
                    all_option_widgets.extend([
                        html.Div(
                            plotter_widgets,
                            id={'type': 'plotter-options-container', 'name': plot_name},
                            style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
                        ),
                        html.Hr()
                    ])
        
        return all_option_widgets
    
    # Run active plotters and update the 3D figure
    @app.callback(
        [Output('det3d', 'figure')],
        [Input('button-load-det3d-fig', 'n_clicks')],
        [State('det3d-viewer-checklist-plotchoices', 'value')]
    )
    def run_active_det3d_plotters(n_clicks, selected_plots):
        """Run active plotters and update the 3D figure"""
        if n_clicks is None or not selected_plots:
            return [make_default_plot()]
        
        # Get options for all selected plotters from the state store
        from lardly.ubdl.core.state import state_manager
        all_options = state_manager.get_state('plotters', 'options', default={})
        
        # Get the tree dictionary
        from lardly.ubdl.io.io_manager import get_tree_dict
        tree_dict = get_tree_dict()
        
        # Create options dictionary for the selected plotters
        options = {name: all_options.get(name, {}) for name in selected_plots}
        
        # Get traces from plotters
        from lardly.ubdl.plotters.registry import registry
        traces = registry.make_traces(selected_plots, tree_dict, options)
        
        # Create figure
        fig = make_default_plot()
        
        # Adjust aspect ratio for certain plotters
        if "RecoCRT" in selected_plots:
            fig.layout['scene']['aspectratio']['z'] = 2
            
        # Add traces to figure
        for trace in traces:
            fig.add_trace(trace)
            
        return [fig]
