"""
IntimeFlash plotter implementation

This module implements a plotter for in-time optical flashes.
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
    from lardly.data.larlite_opflash import visualize_larlite_opflash_3d, visualize_empty_opflash
    from larlite import larlite, larutil
    _IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logger.error(f"Error importing dependencies for IntimeFlashPlotter: {e}")
    _IMPORTS_SUCCESSFUL = False

class IntimeFlashPlotter(BasePlotter):
    """
    Plotter for in-time optical flashes
    
    This plotter visualizes optical flashes from the detector,
    with options to select specific flashes by index and time.
    """
    
    def __init__(self):
        """Initialize the IntimeFlash plotter"""
        super().__init__("IntimeFlash", "In-time Optical Flashes")
        self._imports_successful = _IMPORTS_SUCCESSFUL
        logger.info(f"IntimeFlashPlotter initialized. Imports successful: {self._imports_successful}")
        self._flash_data = None  # Cache for flash data
    
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
            logger.warning("IntimeFlashPlotter not applicable: imports failed")
            return False
            
        # Get opflash treename from configuration or use default
        self.opflash_treename = "simpleFlashBeam"
        required_tree = f"opflash_{self.opflash_treename}_tree"
        
        if required_tree not in tree_keys:
            logger.info(f"IntimeFlashPlotter not applicable: missing tree {required_tree}")
            return False
        
        logger.info("IntimeFlashPlotter is applicable for the current data")
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("selected_flash", "intime")  # Default to intime
        self.set_option_value("pmt_radius", 15.24)  # Default PMT radius in cm
        self.set_option_value("pe_threshold", 0.0)  # PE display threshold
        self.set_option_value("show_null", False)  # Show empty flash option
    
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
                html.Label('Optical Flash Options:'),
                html.Div([
                    html.Label('Select Flash:'),
                    dcc.Dropdown(
                        id='intimeflash-selector',
                        options=[
                            {'label': 'Loading flashes...', 'value': 'loading'}
                        ],
                        value=self.get_option_value("selected_flash", "intime"),
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('PMT Radius (cm):'),
                    dcc.Slider(
                        id='intimeflash-pmt-radius',
                        min=5,
                        max=30,
                        step=1,
                        marks={i: f'{i}' for i in range(5, 31, 5)},
                        value=self.get_option_value("pmt_radius", 15.24),
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('PE Threshold:'),
                    dcc.Slider(
                        id='intimeflash-pe-threshold',
                        min=0,
                        max=50,
                        step=1,
                        marks={i: f'{i}' for i in range(0, 51, 10)},
                        value=self.get_option_value("pe_threshold", 0),
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('Display Options:'),
                    dcc.Checklist(
                        id='intimeflash-display-options',
                        options=[
                            {'label': 'Show Empty Flash Option', 'value': 'show_null'},
                        ],
                        value=[
                            'show_null' if self.get_option_value("show_null", False) else None,
                        ],
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ]),
            ])
        ]
    
    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return [
            'intimeflash-selector',
            'intimeflash-pmt-radius',
            'intimeflash-pe-threshold',
            'intimeflash-display-options'
        ]
    
    def get_flash_data(self, iolarlite) -> List[Tuple[int, float]]:
        """
        Get flash data from the current event
        
        Args:
            iolarlite: LArLite I/O manager
            
        Returns:
            List of (index, time) tuples for each flash
        """
        if self._flash_data is not None:
            return self._flash_data
            
        flash_data = []
        
        try:
            ev_flash = iolarlite.get_data("opflash", self.opflash_treename)
            nflashes = ev_flash.size()
            
            # Find intime flash (in window [2.94, 4.98])
            intime_index = None
            
            for i in range(nflashes):
                flash = ev_flash.at(i)
                time = flash.Time()
                flash_data.append((i, time))
                
                # Check if this is the first flash in the intime window
                if intime_index is None and 2.94 <= time <= 4.98:
                    intime_index = i
            
            # Store intime_index in the flash data
            self._flash_data = {
                'flashes': flash_data,
                'intime_index': intime_index
            }
            
            return self._flash_data
            
        except Exception as e:
            logger.error(f"Error getting flash data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'flashes': [], 'intime_index': None}

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
            
            # Reset flash data cache when making new traces
            self._flash_data = None
            
            # Get options, using provided options or falling back to stored options
            if options is None:
                options = {}
            
            selected_flash = options.get('selected_flash', self.get_option_value('selected_flash', 'intime'))
            pmt_radius = options.get('pmt_radius', self.get_option_value('pmt_radius', 15.24))
            pe_threshold = options.get('pe_threshold', self.get_option_value('pe_threshold', 0.0))
            
            # Get flash data
            flash_data = self.get_flash_data(iolarlite)
            
            # Get the opflash event
            ev_flash = iolarlite.get_data("opflash", self.opflash_treename)
            self.log_info(f"Number of optical flashes: {ev_flash.size()}")
            
            traces = []
            
            # Handle the selected flash
            if selected_flash == 'null':
                # Show empty flash
                self.log_info("Creating empty flash visualization")
                traces = visualize_empty_opflash(pmt_radius=pmt_radius)
                
            elif selected_flash == 'intime' and flash_data['intime_index'] is not None:
                # Show the first flash in the intime window
                intime_index = flash_data['intime_index']
                flash = ev_flash.at(intime_index)
                self.log_info(f"Visualizing intime flash at index {intime_index}, time {flash.Time()}")
                traces = visualize_larlite_opflash_3d(flash, pmt_radius_cm=pmt_radius, pe_draw_threshold=pe_threshold, use_v4_geom=True)
                
            elif selected_flash.isdigit():
                # Show specific flash by index
                index = int(selected_flash)
                if 0 <= index < ev_flash.size():
                    flash = ev_flash.at(index)
                    self.log_info(f"Visualizing flash at index {index}, time {flash.Time()}")
                    traces = visualize_larlite_opflash_3d(flash, pmt_radius_cm=pmt_radius, pe_draw_threshold=pe_threshold, use_v4_geom=True)
                else:
                    self.log_error(f"Flash index {index} out of range")
                    traces = visualize_empty_opflash(pmt_radius=pmt_radius)
            
            else:
                # Default to empty if no valid selection
                self.log_info("No valid flash selection, showing empty")
                traces = visualize_empty_opflash(pmt_radius=pmt_radius)
            
            self.log_info(f"Created {len(traces)} flash traces")
            return traces
            
        except Exception as e:
            self.log_error(f"Error in make_traces: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
            # Update flash selector options when a new entry is loaded
            @app.callback(
                Output('intimeflash-selector', 'options'),
                [Input('io-nav-button-load-entry', 'n_clicks'),
                 Input('intimeflash-display-options', 'value')],
                [State('det3d-viewer-checklist-plotchoices', 'value')],
                prevent_initial_call=True
            )
            def update_flash_selector(n_clicks, display_options, selected_plotters):
                # Only update if this plotter is selected
                if 'IntimeFlash' not in selected_plotters:
                    # Return a single placeholder option if not selected
                    return [{'label': 'Select a flash...', 'value': 'intime'}]
                
                show_null = 'show_null' in display_options if display_options else False
                
                # Get the IO manager and check if it's loaded
                from lardly.ubdl.io.io_manager import get_tree_dict
                tree_dict = get_tree_dict()
                iolarlite = tree_dict.get('iolarlite')
                
                if iolarlite is None:
                    return [{'label': 'No data loaded', 'value': 'loading'}]
                
                # Get flash data
                flash_data = self.get_flash_data(iolarlite)
                options = []
                
                # Add null option if requested
                if show_null:
                    options.append({'label': 'Empty Flash (Null)', 'value': 'null'})
                
                # Add intime option
                if flash_data['intime_index'] is not None:
                    intime_flash = flash_data['flashes'][flash_data['intime_index']]
                    options.append({
                        'label': f'Intime Flash: #{intime_flash[0]} (t={intime_flash[1]:.2f} μs)',
                        'value': 'intime'
                    })
                else:
                    options.append({'label': 'No Intime Flash Found', 'value': 'intime'})
                
                # Add individual flash options
                for idx, time in flash_data['flashes']:
                    in_window = 2.94 <= time <= 4.98
                    window_marker = " [INTIME]" if in_window else ""
                    options.append({
                        'label': f'Flash #{idx}: t={time:.2f} μs{window_marker}',
                        'value': str(idx)
                    })
                
                return options
            
            # Update selected flash in state when dropdown changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('intimeflash-selector', 'value')],
                prevent_initial_call=True
            )
            def store_selected_flash(value):
                if value:
                    self.set_option_value('selected_flash', value)
                return None
            
            # Store PMT radius in state when slider changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('intimeflash-pmt-radius', 'value')],
                prevent_initial_call=True
            )
            def store_pmt_radius(value):
                if value:
                    self.set_option_value('pmt_radius', value)
                return None
            
            # Store PE threshold in state when slider changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('intimeflash-pe-threshold', 'value')],
                prevent_initial_call=True
            )
            def store_pe_threshold(value):
                if value is not None:
                    self.set_option_value('pe_threshold', value)
                return None
            
            # Store display options in state when they change
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('intimeflash-display-options', 'value')],
                prevent_initial_call=True
            )
            def store_display_options(value):
                show_null = 'show_null' in value if value else False
                self.set_option_value('show_null', show_null)
                return None
            
            logger.info("IntimeFlashPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering IntimeFlashPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())