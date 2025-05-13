"""
CRT plotter implementation

This module implements a plotter for Cosmic Ray Tagger (CRT) hits and tracks.
"""
from typing import Dict, Any, List, Optional
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
    from lardly.data.larlite_crttrack import visualize_larlite_event_crttrack
    from lardly.data.larlite_crthit import visualize_larlite_event_crthit
    from lardly.data.larlite_opflash import visualize_larlite_opflash_3d
    from lardly.crtoutline import CRTOutline
    from larlite import larlite, larutil
    _IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing dependencies for CRTPlotter: {e}")
    _IMPORTS_SUCCESSFUL = False

try:
    from ublarcvapp import ublarcvapp
    _UBLARCVAPP_AVAILABLE = True
except ImportError:
    logger.warning("ublarcvapp module not available for CRTPlotter")
    _UBLARCVAPP_AVAILABLE = False

class CRTPlotter(BasePlotter):
    """
    Plotter for Cosmic Ray Tagger data
    
    This plotter visualizes CRT hits and tracks, optionally filtered by
    proximity to optical flashes.
    """
    
    def __init__(self):
        """Initialize the CRT plotter"""
        super().__init__("CRT", "Cosmic Ray Tagger Hits and Tracks")
        self._imports_successful = _IMPORTS_SUCCESSFUL
        logger.info(f"CRTPlotter initialized. Imports successful: {self._imports_successful}")
    
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
            logger.warning("CRTPlotter not applicable: imports failed")
            return False

        # one day allow this to be configured by yaml
        self.crttrack_treename = "crttrack"
        self.crthit_treename = "crthitcorr"
        self.opflash_treename = "simpleFlashCosmic"
            
        # Check for required tree: crttrack_crttrack_tree
        required_trees = [(self.crttrack_treename,f"crttrack_{self.crttrack_treename}_tree"),
            (self.crthit_treename,f"crthit_{self.crthit_treename}_tree"),
            (self.opflash_treename,f"opflash_{self.opflash_treename}_tree")]

        self.found_trees = []
        for (name,full_name) in required_trees:
            if full_name in tree_keys:
                self.found_trees.append(name)
        if len(self.found_trees)==0:
            logger.info(f"CRTPlotter not applicable: need at list one from {required_trees}")
            return False
        else:
            logger.info(f"CRTPlotter found {len(self.found_trees)} trees: ",self.found_trees)
        
        logger.info("CRTPlotter is applicable for the current data")
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("show_tracks", True)
        self.set_option_value("show_hits", True)
        self.set_option_value("show_outline", True)
        self.set_option_value("filter_by_opflash", True)
        self.set_option_value("max_dt_usec", 1.0)
        self.set_option_value("hit_size", 3)
        self.set_option_value("track_width", 2)
    
    def make_option_widgets(self) -> List[Any]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        # If imports failed, show error message
        if not self._imports_successful:
            return [html.Div("Error: Required modules not available", style={"color": "red"})]
            
        return [
            html.Div([
                html.Label('CRT Options:'),
                html.Div([
                    html.Label('Display Options:'),
                    dcc.Checklist(
                        id='crt-display-options',
                        options=[
                            {'label': 'Show Tracks', 'value': 'tracks'},
                            {'label': 'Show Hits', 'value': 'hits'},
                            {'label': 'Show CRT Outline', 'value': 'outline'},
                            {'label': 'Filter by OpFlash', 'value': 'filter_opflash'},
                        ],
                        value=[
                            'tracks' if self.get_option_value("show_tracks", True) else None,
                            'hits' if self.get_option_value("show_hits", True) else None,
                            'outline' if self.get_option_value("show_outline", True) else None,
                            'filter_opflash' if self.get_option_value("filter_by_opflash", True) else None,
                        ],
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('Max Time Difference (μs):'),
                    dcc.Slider(
                        id='crt-max-dt-slider',
                        min=0.1,
                        max=3.0,
                        step=0.1,
                        marks={i/10: f'{i/10}' for i in range(1, 31, 5)},
                        value=self.get_option_value("max_dt_usec", 1.0),
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('Visual Settings:'),
                    html.Div([
                        html.Label('Hit Size:'),
                        dcc.Slider(
                            id='crt-hit-size-slider',
                            min=1,
                            max=8,
                            step=1,
                            marks={i: f'{i}' for i in range(1, 9, 1)},
                            value=self.get_option_value("hit_size", 3),
                        )
                    ], style={'margin-bottom': '5px'}),
                    html.Div([
                        html.Label('Track Width:'),
                        dcc.Slider(
                            id='crt-track-width-slider',
                            min=1,
                            max=6,
                            step=1,
                            marks={i: f'{i}' for i in range(1, 7, 1)},
                            value=self.get_option_value("track_width", 2),
                        )
                    ])
                ])
            ])
        ]
    
    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return [
            'crt-display-options', 
            'crt-max-dt-slider',
            'crt-hit-size-slider',
            'crt-track-width-slider'
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
            display_options = options.get('display_options', [])
            
            show_tracks = 'tracks' in display_options if 'display_options' in options else self.get_option_value('show_tracks', True)
            show_hits = 'hits' in display_options if 'display_options' in options else self.get_option_value('show_hits', True)
            show_outline = 'outline' in display_options if 'display_options' in options else self.get_option_value('show_outline', True)
            filter_by_opflash = 'filter_opflash' in display_options if 'display_options' in options else self.get_option_value('filter_by_opflash', True)
            if self.crttrack_treename not in self.found_trees:
                show_tracks = False
            if self.crthit_treename not in self.found_trees:
                show_hits = False
            if self.opflash_treename not in self.found_trees:
                filter_by_opflash = False
            
            max_dt_usec = options.get('max_dt_usec', self.get_option_value('max_dt_usec', 1.0))
            hit_size = options.get('hit_size', self.get_option_value('hit_size', 3))
            track_width = options.get('track_width', self.get_option_value('track_width', 2))
            
            # Get CRT tracks and hits
            if show_tracks:
                ev_crttrk = iolarlite.get_data("crttrack", self.crttrack_treename)
                self.log_info(f"Number of CRT track objects: {ev_crttrk.size()}")
            if show_hits:
                ev_crthit = iolarlite.get_data("crthit", self.crthit_treename)
                self.log_info(f"Number of CRT hit objects: {ev_crthit.size()}")
            
            # Get optical flashes for filtering
            flash_times = None
            if filter_by_opflash:
                ev_flash = iolarlite.get_data("opflash", self.opflash_treename)
                if ev_flash.size() > 0:
                    flash_times = np.zeros(ev_flash.size())
                    for iflash in range(ev_flash.size()):
                        flash = ev_flash.at(iflash)
                        flash_times[iflash] = flash.Time()
            
            crt_traces = []
            
            # Process CRT tracks
            if show_tracks and ev_crttrk.size() > 0:
                try:
                    # Get all track traces
                    track_traces = visualize_larlite_event_crttrack(ev_crttrk)
                    
                    # Filter and configure tracks
                    for itrack, trace in enumerate(track_traces):
                        # Adjust marker size
                        trace['marker']['size'] = hit_size * 1.33  # Slightly larger than hits
                        trace['line']['width'] = track_width
                        trace['name'] = f"crttrack[{itrack}]"
                        
                        # Apply flash filter if enabled
                        if filter_by_opflash and flash_times is not None:
                            tusec = trace['customdata'][0, 0]  # (t,tick,plane)
                            dt = np.abs(flash_times - tusec)
                            dtmin = np.min(dt)
                            
                            if dtmin < max_dt_usec:
                                crt_traces.append(trace)
                        else:
                            crt_traces.append(trace)
                except Exception as e:
                    self.log_error(f"Error processing CRT tracks: {e}")
            
            # Process CRT hits
            if show_hits and ev_crthit.size() > 0:
                try:
                    # Process hit data
                    dv = larutil.LArProperties.GetME().DriftVelocity()
                    
                    crthit_hovertemplate = """
                    <b>x</b>: %{x}<br>
                    <b>y</b>: %{y}<br>
                    <b>z</b>: %{z}<br>
                    <b>t</b>: %{customdata[0]} usec<br>
                    <b>tick</b>: %{customdata[1]}<br>
                    <b>CRT plane</b>: %{customdata[2]}<br>
                    """
                    
                    hitinfo_v = []
                    
                    # Apply flash filtering if enabled
                    for ihit in range(ev_crthit.size()):
                        crthit = ev_crthit.at(ihit)
                        hitinfo = np.zeros(6)
                        t_usec = crthit.ts2_ns * 0.001
                        dx = t_usec * dv
                        
                        hitinfo[0] = crthit.x_pos + dx
                        hitinfo[1] = crthit.y_pos
                        hitinfo[2] = crthit.z_pos
                        hitinfo[3] = t_usec
                        hitinfo[4] = 3200 + t_usec / 0.5
                        hitinfo[5] = crthit.plane
                        
                        # Apply flash filter if enabled
                        if filter_by_opflash and flash_times is not None:
                            dt = np.abs(flash_times - t_usec)
                            dtmin = np.min(dt)
                            
                            if dtmin < max_dt_usec:
                                hitinfo_v.append(hitinfo)
                        else:
                            hitinfo_v.append(hitinfo)
                    
                    # Create hit trace if we have hits
                    if len(hitinfo_v) > 0:
                        if len(hitinfo_v) > 1:
                            hitinfo_all = np.stack(hitinfo_v, axis=0)
                        else:
                            hitinfo_all = np.array([hitinfo_v[0]])
                        
                        crthit_trace = {
                            "type": "scatter3d",
                            "x": hitinfo_all[:, 0],
                            "y": hitinfo_all[:, 1],
                            "z": hitinfo_all[:, 2],
                            "mode": "markers",
                            "name": "crthits",
                            "hovertemplate": crthit_hovertemplate,
                            "customdata": hitinfo_all[:, 3:],
                            "marker": {"color": "rgb(255,0,255)", "size": hit_size, "opacity": 0.5},
                        }
                        crt_traces.append(crthit_trace)
                except Exception as e:
                    self.log_error(f"Error processing CRT hits: {e}")
            
            # Add CRT outline if requested
            if show_outline and len(crt_traces) > 0:
                try:
                    crt_outline_traces = CRTOutline().get_lines()
                    crt_traces.extend(crt_outline_traces)
                except Exception as e:
                    self.log_error(f"Error creating CRT outline: {e}")
            
            self.log_info(f"Created {len(crt_traces)} CRT traces")
            return crt_traces
            
        except Exception as e:
            self.log_error(f"Error in make_traces: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
            # Store display options in state when they change
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('crt-display-options', 'value')],
                prevent_initial_call=True
            )
            def store_display_options(value):
                if value is not None:
                    display_options = {
                        'show_tracks': 'tracks' in value,
                        'show_hits': 'hits' in value,
                        'show_outline': 'outline' in value,
                        'filter_by_opflash': 'filter_opflash' in value
                    }
                    for k, v in display_options.items():
                        self.set_option_value(k, v)
                return None
            
            # Store max dt value
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('crt-max-dt-slider', 'value')],
                prevent_initial_call=True
            )
            def store_max_dt(value):
                if value is not None:
                    self.set_option_value('max_dt_usec', value)
                return None
            
            # Store visual settings
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('crt-hit-size-slider', 'value')],
                prevent_initial_call=True
            )
            def store_hit_size(value):
                if value is not None:
                    self.set_option_value('hit_size', value)
                return None
            
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('crt-track-width-slider', 'value')],
                prevent_initial_call=True
            )
            def store_track_width(value):
                if value is not None:
                    self.set_option_value('track_width', value)
                return None
            
            logger.info("CRTPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering CRTPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())