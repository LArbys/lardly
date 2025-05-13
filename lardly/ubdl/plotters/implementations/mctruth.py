"""
MCTruth plotter implementation

This module implements a plotter for Monte Carlo truth information,
including tracks and showers.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from lardly.ubdl.plotters.base import BasePlotter
from lardly.ubdl.core.state import state_manager
import lardly.data.larlite_mctrack as vis_mctrack
import lardly.data.larlite_mcshower as vis_mcshower
from ublarcvapp import ublarcvapp
from larlite import larlite, larutil

class MCTruthPlotter(BasePlotter):
    """
    Plotter for Monte Carlo truth information
    
    This plotter visualizes MC tracks and showers from simulation.
    """
    
    def __init__(self):
        """Initialize the MCTruth plotter"""
        super().__init__("MCTruth", "Monte Carlo Truth (Tracks/Showers)")
    
    def is_applicable(self, tree_keys: List[str]) -> bool:
        """
        Check if this plotter is applicable
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            True if the required trees are available
        """
        # Check for required trees: mctrack_mcreco_tree and mcshower_mcreco_tree
        required_trees = ["mctrack_mcreco_tree", "mcshower_mcreco_tree"]
        for treename in required_trees:
            if treename not in tree_keys:
                return False
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("do_sce_correction", True)
        self.set_option_value("no_offset", False)
        self.set_option_value("show_tracks", True)
        self.set_option_value("show_showers", True)
        self.set_option_value("origin_filter", None)  # None, 1 (neutrino), 2 (cosmic)
    
    def make_option_widgets(self) -> List[Any]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        return [
            html.Div([
                html.Label('MCTruth Options:'),
                html.Div([
                    html.Label('Origin Filter:'),
                    dcc.RadioItems(
                        id='mctruth-origin-filter',
                        options=[
                            {'label': 'All Particles', 'value': 'all'},
                            {'label': 'Neutrino Only', 'value': '1'},
                            {'label': 'Cosmic Only', 'value': '2'},
                        ],
                        value='all' if self.get_option_value("origin_filter", None) is None else str(self.get_option_value("origin_filter")),
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('Display Options:'),
                    dcc.Checklist(
                        id='mctruth-display-options',
                        options=[
                            {'label': 'Show Tracks', 'value': 'tracks'},
                            {'label': 'Show Showers', 'value': 'showers'},
                            {'label': 'Apply SCE Correction', 'value': 'sce'},
                            {'label': 'No Tick Offset', 'value': 'no_offset'},
                        ],
                        value=[
                            'tracks' if self.get_option_value("show_tracks", True) else None,
                            'showers' if self.get_option_value("show_showers", True) else None,
                            'sce' if self.get_option_value("do_sce_correction", True) else None,
                            'no_offset' if self.get_option_value("no_offset", False) else None,
                        ],
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ]),
            ])
        ]
    
    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return ['mctruth-origin-filter', 'mctruth-display-options']

    def make_traces(self, tree_dict: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create traces for this plotter
        
        Args:
            tree_dict: Dictionary of trees (data sources)
            options: Optional dictionary of options for this plotter
            
        Returns:
            List of plotly trace dictionaries
        """
        iolarlite = tree_dict.get('iolarlite')
        if iolarlite is None:
            self.log_error("iolarlite not found in tree_dict")
            return []
        
        # Get options, using provided options or falling back to stored options
        if options is None:
            options = {}
        
        # Process options
        display_options = options.get('display_options', [])
        origin_filter = options.get('origin_filter', self.get_option_value('origin_filter', None))
        
        # Convert origin_filter to integer if needed
        if origin_filter == 'all':
            origin_filter = None
        elif origin_filter is not None:
            try:
                origin_filter = int(origin_filter)
            except:
                origin_filter = None
        
        show_tracks = 'tracks' in display_options if 'display_options' in options else self.get_option_value('show_tracks', True)
        show_showers = 'showers' in display_options if 'display_options' in options else self.get_option_value('show_showers', True)
        do_sce_correction = 'sce' in display_options if 'display_options' in options else self.get_option_value('do_sce_correction', True)
        no_offset = 'no_offset' in display_options if 'display_options' in options else self.get_option_value('no_offset', False)
        
        traces = []
        
        # Process MC tracks
        if show_tracks:
            ev_mctrack = iolarlite.get_data("mctrack", "mcreco")
            self.log_info(f"Size of mctrack container: {ev_mctrack.size()}")
            
            track_traces = vis_mctrack.visualize_larlite_event_mctrack(
                ev_mctrack, 
                origin=origin_filter, 
                do_sce_correction=do_sce_correction, 
                no_offset=no_offset
            )
            
            self.log_info(f"Number of track traces: {len(track_traces)}")
            traces.extend(track_traces)
        
        # Process MC showers
        if show_showers:
            ev_mcshower = iolarlite.get_data("mcshower", "mcreco")
            self.log_info(f"Size of mcshower container: {ev_mcshower.size()}")
            
            shower_traces = vis_mcshower.visualize_larlite_event_mcshower(
                ev_mcshower,
                origin=origin_filter,
                apply_sce=do_sce_correction,
                no_offset=no_offset
            )
            
            self.log_info(f"Number of shower traces: {len(shower_traces)}")
            traces.extend(shower_traces)
        
        return traces

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        # Store origin filter in state when it changes
        @app.callback(
            Output('det3d-hidden-output', 'children',allow_duplicate=True),
            [Input('mctruth-origin-filter', 'value')],
            prevent_initial_call=True
        )
        def store_origin_filter(value):
            if value is not None:
                if value == 'all':
                    self.set_option_value('origin_filter', None)
                else:
                    try:
                        self.set_option_value('origin_filter', int(value))
                    except:
                        self.set_option_value('origin_filter', None)
            return None
        
        # Store display options in state when they change
        @app.callback(
            Output('det3d-hidden-output', 'children', allow_duplicate=True),
            [Input('mctruth-display-options', 'value')],
            prevent_initial_call=True
        )
        def store_display_options(value):
            if value is not None:
                display_options = {
                    'show_tracks': 'tracks' in value,
                    'show_showers': 'showers' in value,
                    'do_sce_correction': 'sce' in value,
                    'no_offset': 'no_offset' in value
                }
                for k, v in display_options.items():
                    self.set_option_value(k, v)
            return None