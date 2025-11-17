"""
larlite SimCh plotter implementation

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
    from lardly.data.larlite_simch import visualize_larlite_simch
    _IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing dependencies for SimChPlotter: {e}")
    _IMPORTS_SUCCESSFUL = False

class SimChPlotter(BasePlotter):
    """
    Plotter for neutrino input clusters
    
    This plotter visualizes clusters used as input for neutrino reconstruction,
    with multiple coloring options.
    """
    
    def __init__(self):
        """Initialize the SimCh plotter"""
        super().__init__("SimCh", "SimChannel Information")
        self._imports_successful = _IMPORTS_SUCCESSFUL
        self._input_trees_present = []
        logger.info(f"SimChPlotter initialized. Imports successful: {self._imports_successful}")
    
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
            logger.warning("SimChPlotter not applicable: imports failed")
            return False
            
        # Check for input cluster trees
        # we just for any larflow3dhit tree 
        self._input_trees_present = []
        lfhit_len = len('simch_')
        for treename in tree_keys:
            if 'simch' not in treename:
                continue
            logger.info(f"parseme: {treename} to {treename[lfhit_len:-5]}")
            if ( (lfhit_len < len(treename))
                 and treename[:lfhit_len]=='simch_'
                 and treename[-5:]=="_tree"):
                self._input_trees_present.append( treename[lfhit_len:-5] )

        if not self._input_trees_present:
            logger.info("SimChPlotter not applicable: no input trees found")
            return False
        
        logger.info(f"SimChPlotter is applicable, found trees: {self._input_trees_present}")
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("coloring_mode", "edep")  # Default to ssnet (particle ID) coloring
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
                html.Label('SimCh Options:'),
                
                # Which tree do we use
                html.Div([
                    html.Label('simch Source:'),
                    dcc.Dropdown(
                        id='simch-source',
                        options=[
                            {'label': tree, 'value': tree} for tree in self._input_trees_present
                        ],
                        value=self._input_trees_present[0] if self._input_trees_present else None,
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
                
                # how do we color the points
                html.Div([
                    html.Label('Coloring Mode:'),
                    dcc.RadioItems(
                        id='simch-coloring-mode',
                        options=[
                            {'label': 'Energy Deposited', 'value': 'edep'},
                            {'label': 'Particle Type', 'value': 'pid'},
                            {'label': 'Particle Instance', 'value': 'instance'},
                        ],
                        value=self.get_option_value("coloring_mode", "edep"),
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ], style={'margin-bottom': '10px'}),
                
                # Conditional options depending on coloring mode
                html.Div(id='simch-conditional-options', children=[
                    # This will be populated by callback
                ]),
                
                # Marker settings
                html.Div([
                    html.Label('Visual Settings:'),
                    html.Div([
                        html.Label('Marker Size:'),
                        dcc.Slider(
                            id='simch-marker-size',
                            min=0.5,
                            max=3.0,
                            step=0.1,
                            marks={i/10: f'{i/10}' for i in range(5, 31, 5)},
                            value=self.get_option_value("marker_size", 1.0),
                        )
                    ], style={'margin-bottom': '5px'}),
                    html.Div([
                        html.Label('Marker Opacity:'),
                        dcc.Slider(
                            id='simch-marker-opacity',
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
            'simch-source',
            'simch-coloring-mode',
            'simch-conditional-options',
            'simch-marker-size',
            'simch-marker-opacity'
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
            cluster_source = options.get('source',         self._input_trees_present[0] if self._input_trees_present else None)
            coloring_mode  = options.get('coloring_mode',  self.get_option_value('coloring_mode', 'edep'))
            marker_size    = options.get('marker_size',    self.get_option_value('marker_size', 1.0))
            marker_opacity = options.get('marker_opacity', self.get_option_value('marker_opacity', 0.4))
            
            if cluster_source not in self._input_trees_present:
                self.log_error(f"Selected cluster source {cluster_source} not available")
                return []
            
            # Get simch data
            self.log_info(f"getting clusters from source: {cluster_source}")
            ev_simch = iolarlite.get_data("simch", cluster_source)

            # make trace
            simch_plots = visualize_larlite_simch( ev_simch,
               color_by=coloring_mode,
               opacity=marker_opacity,
               marker_size=marker_size,
               ioll=iolarlite,
               max_num_pts=20000)
               
            self.log_info(f"Created {len(simch_plots)} cluster traces")
            return simch_plots
            
        except Exception as e:
            self.log_error(f"Error in make_traces: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
            # Update conditional options based on coloring mode
            @app.callback(
                Output('simch-conditional-options', 'children'),
                [Input('simch-coloring-mode', 'value')],
                prevent_initial_call=True
            )
            def update_conditional_options(coloring_mode):
                # if coloring_mode == 'edep':
                #     return html.Div([
                #         html.Label('Particle Type:'),
                #         dcc.RadioItems(
                #             id='larflowhits-particle-type',
                #             options=[
                #                 {'label': 'Electron', 'value': 'electron'},
                #                 {'label': 'Gamma', 'value': 'gamma'},
                #                 {'label': 'Muon', 'value': 'muon'},
                #                 {'label': 'Proton', 'value': 'proton'},
                #                 {'label': 'Pion', 'value': 'pion'}
                #             ],
                #             value=self.get_option_value('particle_type', 'electron'),
                #             style={'display': 'flex', 'flex-direction': 'column'}
                #         )
                #     ], style={'margin-bottom': '10px'})
                return html.Div([])  # Empty div for other modes
            
            # Store cluster source when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('simch-source', 'value')],
                prevent_initial_call=True
            )
            def store_source(value):
                if value:
                    self.set_option_value('source', value)
                return None
            
            # Store coloring mode when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('simch-coloring-mode', 'value')],
                prevent_initial_call=True
            )
            def store_coloring_mode(value):
                if value:
                    self.set_option_value('coloring_mode', value)
                return None
            
            # Store marker size when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('simch-marker-size', 'value')],
                prevent_initial_call=True
            )
            def store_marker_size(value):
                if value:
                    self.set_option_value('marker_size', value)
                return None
            
            # Store marker opacity when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('simch-marker-opacity', 'value')],
                prevent_initial_call=True
            )
            def store_marker_opacity(value):
                if value is not None:
                    self.set_option_value('marker_opacity', value)
                return None
            
            logger.info("SimChPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering SimChPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())
