"""
Cosmic tracks plotter implementation

This module implements a plotter for cosmic ray tracks including
boundary, contained, and proton cosmic tracks.
"""
from typing import Dict, Any, List, Optional
from dash import html, dcc
from dash.dependencies import Input, Output, State
import logging

from lardly.ubdl.plotters.base import BasePlotter
from lardly.data.larlite_track import visualize_larlite_track

# Create a logger for this module
logger = logging.getLogger(__name__)

class CosmicTracksPlotter(BasePlotter):
    """
    Plotter for cosmic ray tracks
    
    This plotter visualizes cosmic ray tracks that have been reconstructed. 
    Depending on reconstruction options, they might also be classified as
    - Boundary cosmic tracks
    - Contained cosmic tracks  
    - Cosmic proton tracks
    """
    
    def __init__(self):
        """Initialize the Cosmic Tracks plotter"""
        super().__init__("CosmicTracks", "Cosmic Ray Tracks")
        self._input_trees_present = []
        self.possible_cosmic_track_trees = [
            "track_boundarycosmicreduced_tree",
            "track_containedcosmicreduced_tree", 
            "track_cosmicprotonreduced_tree",
            "track_simplecosmictrack_tree",
            "track_cosmictrack_tree" 
        ]

        self.colors = {
            "track_boundarycosmicreduced_tree":'rgb(102,102,53)',  # boundary - olive
            "track_containedcosmicreduced_tree":'rgb(153,51,0)',   # contained - burnt orange
            "track_cosmicprotonreduced_tree":'rgb(0,0,120)',       # proton - dark blue  
            "track_simplecosmictrack_tree":'rgb(10,10,10)',        # unclassified - black
            "track_cosmictrack_tree":'rgb(10,10,10)'               # unclassified - black
        }

    
    def is_applicable(self, tree_keys: List[str]) -> bool:
        """
        Check if this plotter is applicable
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            True if the required trees are available
        """

        
        self._imports_successful = False
        self._input_trees_present = ["all"]
        for treename in self.possible_cosmic_track_trees:
            if treename in tree_keys:
                self._imports_successful = True
                self._input_trees_present.append( treename )
                
        return self._imports_successful
    
    def make_option_widgets(self) -> List[Any]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        
        # If no input trees found, show message
        if len(self._input_trees_present)==1:
            return [html.Div("No input cluster trees found in this file", style={"color": "orange"})]
            
        return [
            html.Div([
                html.Label('CosmicTracks Options:'),
                
                html.Div([
                    html.Label('CosmicTrack Source:'),
                    dcc.Dropdown(
                        id='cosmictracks-source',
                        options=[
                            {'label': tree, 'value': tree} for tree in self._input_trees_present
                        ],
                        value=self._input_trees_present[0] if self._input_trees_present else None,
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
            ])
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
        iolarlite = tree_dict.get('iolarlite')
        if iolarlite is None:
            self.log_error("iolarlite not found in tree_dict")
            return []
        
        self.log_info("Creating cosmic tracks traces")
        
        traces = []

        cosmictracks_source = options.get('cosmictracks_source', self._input_trees_present[0] if self._input_trees_present else None)
        self.log_info(f"Get cosmic tracks from {cosmictracks_source}")

        if cosmictracks_source is None:
            return traces
        if cosmictracks_source == "all":
            cosmictracks_source = self._input_trees_present[1:]
        elif cosmictracks_source in self._input_trees_present[1:]:
            cosmictracks_source = [cosmictracks_source]
        
        # Process each type of cosmic track
        itrack = 0
        for ev_container_name in cosmictracks_source:
            producername = ev_container_name[len("track_"):-len("_tree")]
            self.log_info(f"  get cosmic tracks from {producername}")
            ev_container = iolarlite.get_data("track",producername)
            container_ntracks = ev_container.size()
            self.log_info(f"  num tracks in {producername}: {container_ntracks}")
            for itrack in range(ev_container.size()):
                track = ev_container.at(itrack)
                track_trace = visualize_larlite_track(track, track_id=itrack, color=self.colors[ev_container_name])
                track_trace['line']['width'] = 2.0
                traces.append(track_trace)
                itrack += 1
        
        return traces

    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return [
            'cosmictracks-source',
        ]

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
        
            # Store cluster source when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('cosmictracks-source', 'value')],
                prevent_initial_call=True
            )
            def store_cosmictracks_source(value):
                if value:
                    self.set_option_value('cosmictracks_source', value)
                return None
            
            logger.info("CosmicTracksPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering CosmicTracksPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())