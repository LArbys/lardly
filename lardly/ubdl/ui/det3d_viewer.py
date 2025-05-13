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
    """
    Create the detector 3D viewer component
    
    Returns:
        Dash component for the detector 3D viewer
    """
    return html.Div([
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
    """
    Register callbacks for the detector 3D viewer
    
    Args:
        app: Dash application
    """
    @app.callback(
        Output('det3d-plot-options', 'children'),
        [Input('det3d-viewer-checklist-plotchoices', 'value')]
    )
    def update_plot_options(selected_plots):
        """
        Update the plot options based on selected plotters
        
        Args:
            selected_plots: List of selected plotter names
            
        Returns:
            List of Dash components for plot options
        """
        if not selected_plots:
            return [html.Hr(), html.Label('Plot options'), html.Hr()]
        
        all_option_widgets = [html.Hr(), html.Label('Plot options'), html.Hr()]
        
        for plot_name in selected_plots:
            plotter = registry.get_plotter(plot_name)
            if plotter:
                all_option_widgets.extend([
                    html.Div(
                        plotter.make_option_widgets(),
                        id=f'{plot_name}-options',
                        style={'margin': '10px', 'padding': '10px', 'border': '1px solid #ddd'}
                    ),
                    html.Hr()
                ])
        
        return all_option_widgets
    
    @app.callback(
        [Output('det3d', 'figure')],
        [Input('button-load-det3d-fig', 'n_clicks')],
        [State('det3d-viewer-checklist-plotchoices', 'value')] +
        # Add any other state dependencies for plotter options
        [State('reconu-vertex-selector', 'value'),
         State('reconu-display-options', 'value')]
    )
    def run_active_det3d_plotters(n_clicks, selected_plots, reconu_vertex=None, reconu_display=None):
        """
        Run active plotters and update the 3D figure
        
        Args:
            n_clicks: Number of button clicks
            selected_plots: List of selected plotter names
            reconu_vertex: Selected vertex for RecoNu plotter
            reconu_display: Display options for RecoNu plotter
            
        Returns:
            Updated Plotly figure
        """
        if not selected_plots:
            return [make_default_plot()]
        
        # Collect plotter options
        options = {}
        if 'RecoNu' in selected_plots:
            options['RecoNu'] = {
                'selected_vertex': reconu_vertex,
                'display_options': reconu_display
            }
        
        # Get tree dictionary
        from lardly.io.io_manager import get_tree_dict
        tree_dict = get_tree_dict()
        
        # Get traces from plotters
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
    
    # Add callback to update vertex selector options when data is loaded
    @app.callback(
        Output('reconu-vertex-selector', 'options'),
        [Input('io-nav-button-load-entry', 'n_clicks')],
        [State('io-nav-entry-input', 'value')]
    )
    def update_vertex_dropdown(n_clicks, entry_value):
        """
        Update vertex dropdown options when data is loaded
        
        Args:
            n_clicks: Number of button clicks
            entry_value: Entry input value
            
        Returns:
            Updated dropdown options
        """
        if n_clicks is None:
            return [{'label': 'All Vertices', 'value': 'all'}]
        
        try:
            # Get the loaded RecoTree from state
            from lardly.io.io_manager import get_tree_dict
            tree_dict = get_tree_dict()
            recoTree = tree_dict.get('recoTree')
            
            if recoTree is None:
                return [{'label': 'All Vertices', 'value': 'all'}]
            
            # Get the number of vertices
            nvertices = recoTree.nuvetoed_v.size()
            options = [{'label': 'All Vertices', 'value': 'all'}]
            
            # Add an option for each vertex
            for i in range(nvertices):
                options.append({'label': f'Vertex {i}', 'value': str(i)})
            
            return options
        except Exception as e:
            print(f"Error updating vertex dropdown: {e}")
            return [{'label': 'All Vertices', 'value': 'all'}]
    
    # Add similar callbacks for other plotter options