"""
LArFlowHits plotter implementation

This module implements a plotter for neutrino input clusters
with multiple coloring options.
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import logging
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from lardly.ubdl.plotters.base import BasePlotter
from lardly.ubdl.core.state import state_manager

# Create a logger for this module
logger = logging.getLogger(__name__)

# Import optional dependencies with error handling
try:
    from larlite import larlite, larutil
    _IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing dependencies for LArFlowHitsPlotter: {e}")
    _IMPORTS_SUCCESSFUL = False

class KeypointHitsPlotter(BasePlotter):
    """
    Plotter for neutrino input clusters
    
    This plotter visualizes clusters used as input for neutrino reconstruction,
    with multiple coloring options.
    """
    
    def __init__(self):
        """Initialize the KeypointHits (as larflowhits) plotter"""
        super().__init__("KeypointHits", "keypoints stored as larflow hits")
        self._imports_successful = _IMPORTS_SUCCESSFUL
        self._input_trees_present = []
        logger.info(f"KeypointHits initialized. Imports successful: {self._imports_successful}")
    
    def is_applicable(self, tree_keys: List[str]) -> bool:
        """
        Check if this plotter is applicable
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            True if the required trees are available
        """
        # Check if imports were successful
        if not self._imports_successful:
            logger.warning("KeypointHitsPlotter not applicable: imports failed")
            return False
            
        # Check for input cluster trees
        # we just for any larflow3dhit tree 
        self._input_trees_present = []
        lfhit_len = len('larflow3dhit_')
        for treename in tree_keys:
            if 'larflow3dhit' not in treename:
                continue
            logger.info(f"parseme: {treename} to {treename[lfhit_len:-5]}")
            if ( (lfhit_len < len(treename))
                 and treename[:lfhit_len]=='larflow3dhit_'
                 and treename[-5:]=="_tree"):
                self._input_trees_present.append( treename[lfhit_len:-5] )

        if not self._input_trees_present:
            logger.info("LArFlowHitsPlotter not applicable: no input trees found")
            return False
        
        logger.info(f"KeypointHitsPlotter is applicable, found trees: {self._input_trees_present}")
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("marker_size", 1.0)
        self.set_option_value("marker_opacity", 0.4)
    
    def make_option_widgets(self) -> List[Any]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        # If imports failed, show error message
        if not self._imports_successful:
            return [html.Div("Error: Required modules not available", style={"color": "red"})]
        
        # If no input trees found, show message
        if not self._input_trees_present:
            return [html.Div("No input cluster trees found in this file", style={"color": "orange"})]
            
        return [
            html.Div([
                html.Label('KeypointHits Options:'),
                
                html.Div([
                    html.Label('KeypointHits larflow3dhit Source:'),
                    dcc.Dropdown(
                        id='keypointhits-source',
                        options=[
                            {'label': tree, 'value': tree} for tree in self._input_trees_present
                        ],
                        value=self._input_trees_present[0] if self._input_trees_present else None,
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
                
                html.Div([
                    html.Label('Visual Settings:'),
                    html.Div([
                        html.Label('Marker Size:'),
                        dcc.Slider(
                            id='keypointhits-marker-size',
                            min=1.0,
                            max=5.0,
                            step=0.5,
                            marks={i/10: f'{i/10}' for i in range(10, 51, 5)},
                            value=self.get_option_value("marker_size", 3.0),
                        )
                    ], style={'margin-bottom': '5px'}),
                    html.Div([
                        html.Label('Marker Opacity:'),
                        dcc.Slider(
                            id='keypointhits-marker-opacity',
                            min=0.1,
                            max=1.0,
                            step=0.1,
                            marks={i/10: f'{i/10}' for i in range(1, 11, 2)},
                            value=self.get_option_value("marker_opacity", 0.4),
                        )
                    ])
                ])
            ])
        ]
    
    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return [
            'keypointhits-source',
            'keypointhits-marker-size',
            'keypointhits-marker-opacity'
        ]

    def make_traces(self, tree_dict: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create traces for this plotter
        
        Args:
            tree_dict: Dictionary of trees (data sources)
            options: Optional dictionary of options for this plotter
            
        Returns:
            List of plotly trace dictionaries
        """
        # Check if imports were successful
        if not self._imports_successful:
            self.log_error("Required modules not available")
            return []
            
        try:
            iolarlite = tree_dict.get('iolarlite')
            if iolarlite is None:
                self.log_error("iolarlite not found in tree_dict")
                return []
            
            # Get options, using provided options or falling back to stored options
            if options is None:
                options = {}
            
            # Process options
            cluster_source = options.get('cluster_source', self._input_trees_present[0] if self._input_trees_present else None)
            marker_size    = options.get('marker_size', self.get_option_value('marker_size', 1.0))
            marker_opacity = options.get('marker_opacity', self.get_option_value('marker_opacity', 0.4))
            
            if cluster_source not in self._input_trees_present:
                self.log_error(f"Selected cluster source {cluster_source} not available")
                return []
            
            
            # Define common hover template
            hover_template = """
            <b>x</b>: %{x}<br>
            <b>y</b>: %{y}<br>
            <b>z</b>: %{z}<br>
            <b>tick</b>: %{customdata[3]}<br>
            <b>U</b>: %{customdata[0]}<br>
            <b>V</b>: %{customdata[1]}<br>
            <b>Y</b>: %{customdata[2]}<br>
            <b>kptype</b>: %{customdata[4]:.2f}<br>
            <b>kpscore</b>: %{customdata[5]:.2f}<br>
            """
            
            # Get cluster data
            traces = []
            self.log_info("getting clusters from source: {cluster_source}")
            ev_cluster = iolarlite.get_data("larflow3dhit", cluster_source)
            self.log_info(f"Number of clusters from {cluster_source}: {ev_cluster.size()}")

            # Process the hits
            for icluster,cluster in enumerate([ev_cluster]):

                npts = cluster.size()
                
                if npts == 0:
                    continue
                
                # Initialize arrays for position and custom data
                pos = np.zeros((npts, 3))
                custom_data = np.zeros((npts, 30))  # Expanded to include more data (bigger than needs to be)
                
                # Extract data for each point
                for isp in range(npts):
                    hit = cluster.at(isp)
                    
                    # Position data
                    for i in range(3):
                        pos[isp, i] = hit[i]
                    
                    # Custom data for hover info
                    custom_data[isp, 0] = hit.targetwire[0]  # U wire
                    custom_data[isp, 1] = hit.targetwire[1]  # V wire
                    custom_data[isp, 2] = hit.targetwire[2]  # Y wire
                    custom_data[isp, 3] = hit.tick   # tick
                    custom_data[isp, 4] = hit.at(3)  # keypoint type
                    custom_data[isp, 5] = hit.at(4)  # keypoint score
                    custom_data[isp, 6] = hit.at(3)/5.0
                
                # Color by type
                marker_config = {
                    "color": custom_data[:,6],
                    "size": marker_size,
                    "opacity": marker_opacity,
                    "colorscale": "Jet",
                    "cmin": 0.0,
                    "cmax": 1.0,
                    "colorbar": {
                        "title": "LArMatch Score",
                        "thickness": 15,
                        "len": 0.5,
                        "x": 1.0,
                        "xanchor": "left"
                    }
                }

                # Create the trace for this cluster
                cluster_trace = {
                    "type": "scatter3d",
                    "x": pos[:, 0],
                    "y": pos[:, 1],
                    "z": pos[:, 2],
                    "mode": "markers",
                    "name": f"{cluster_source}[{icluster}]",
                    "hovertemplate": hover_template,
                    "customdata": custom_data,
                    "marker": marker_config
                }

                traces.append(cluster_trace)
            
            self.log_info(f"Created {len(traces)} cluster traces")
            return traces
            
        except Exception as e:
            self.log_error(f"Error in KeypointHits make_traces: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
        
            # Store cluster source when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('keypointhits-source', 'value')],
                prevent_initial_call=True
            )
            def store_cluster_source(value):
                if value:
                    self.set_option_value('cluster_source', value)
                return None
            
            # Store marker size when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('keypointhits-marker-size', 'value')],
                prevent_initial_call=True
            )
            def store_marker_size(value):
                if value:
                    self.set_option_value('marker_size', value)
                return None
            
            # Store marker opacity when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('keypointhits-marker-opacity', 'value')],
                prevent_initial_call=True
            )
            def store_marker_opacity(value):
                if value is not None:
                    self.set_option_value('marker_opacity', value)
                return None
            
            logger.info("KeypointHitsPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering KeypointHitsPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())
