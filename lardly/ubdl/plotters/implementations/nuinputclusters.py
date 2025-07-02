"""
NuInputClusters plotter implementation

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
    logger.error(f"Error importing dependencies for NuInputClustersPlotter: {e}")
    _IMPORTS_SUCCESSFUL = False

class NuInputClustersPlotter(BasePlotter):
    """
    Plotter for neutrino input clusters
    
    This plotter visualizes clusters used as input for neutrino reconstruction,
    with multiple coloring options.
    """
    
    def __init__(self):
        """Initialize the NuInputClusters plotter"""
        super().__init__("NuInputClusters", "Neutrino Input Clusters")
        self._imports_successful = _IMPORTS_SUCCESSFUL
        self._input_trees_present = []
        logger.info(f"NuInputClustersPlotter initialized. Imports successful: {self._imports_successful}")
    
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
            logger.warning("NuInputClustersPlotter not applicable: imports failed")
            return False
            
        # Check for input cluster trees
        possible_input_tree_list = [
            "showergoodhit", 
            "trackprojsplit_wcfilter",
            "trackprojsplit_offtrigger",
            "cosmicproton",
            "hip",
            "showerkp"
        ]
        
        self._input_trees_present = []
        for treename in possible_input_tree_list:
            lltree = f'larflowcluster_{treename}_tree'
            if lltree in tree_keys:
                self._input_trees_present.append(treename)
                logger.info(f"Found input tree: {lltree}")

        # look for unexpected larflowcluster_X_tree tree names
        for present in tree_keys:
            splitlist = present.strip().split("_")
            if len(splitlist)>=3:
                if splitlist[0]=="larflowcluster" and splitlist[-1]=="tree":
                    producername = present[len("larflowcluster_"):-len("_tree")]
                    logger.info(f"Found larflowcluster tree: {producername}")
                    if producername not in self._input_trees_present:
                        self._input_trees_present.append(producername)
        
        if not self._input_trees_present:
            logger.info("NuInputClustersPlotter not applicable: no input trees found")
            return False
        
        logger.info(f"NuInputClustersPlotter is applicable, found trees: {self._input_trees_present}")
        return True
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("coloring_mode", "cluster")  # Default to ssnet (particle ID) coloring
        self.set_option_value("particle_type", "shower")  # Default to shower score
        self.set_option_value("keypoint_type", "nu")  # Default to nu keypoint
        self.set_option_value("plane_charge", "U")  # Default to U plane
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
                html.Label('Neutrino Input Clusters Options:'),
                
                html.Div([
                    html.Label('Cluster Source:'),
                    dcc.Dropdown(
                        id='nuinputclusters-source',
                        options=[
                            {'label': tree, 'value': tree} for tree in self._input_trees_present
                        ],
                        value=self._input_trees_present[0] if self._input_trees_present else None,
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
                
                html.Div([
                    html.Label('Coloring Mode:'),
                    dcc.RadioItems(
                        id='nuinputclusters-coloring-mode',
                        options=[
                            {'label': 'By Cluster (Random Colors)', 'value': 'cluster'},
                            {'label': 'LArMatch Score', 'value': 'larmatch'},
                            {'label': 'Particle ID Scores', 'value': 'ssnet'},
                            {'label': 'Keypoint Scores', 'value': 'keypoint'},
                            {'label': 'Plane Charge', 'value': 'charge'},
                            {'label': 'Position (XYZ as RGB)', 'value': 'position'}
                        ],
                        value=self.get_option_value("coloring_mode", "ssnet"),
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ], style={'margin-bottom': '10px'}),
                
                # Conditional options depending on coloring mode
                html.Div(id='nuinputclusters-conditional-options', children=[
                    # This will be populated by callback
                ]),
                
                html.Div([
                    html.Label('Visual Settings:'),
                    html.Div([
                        html.Label('Marker Size:'),
                        dcc.Slider(
                            id='nuinputclusters-marker-size',
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
                            id='nuinputclusters-marker-opacity',
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
            'nuinputclusters-source',
            'nuinputclusters-coloring-mode',
            'nuinputclusters-conditional-options',
            'nuinputclusters-particle-type',
            'nuinputclusters-keypoint-type',
            'nuinputclusters-plane-charge',
            'nuinputclusters-marker-size',
            'nuinputclusters-marker-opacity'
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
            coloring_mode = options.get('coloring_mode', self.get_option_value('coloring_mode', 'cluster'))
            particle_type = options.get('particle_type', self.get_option_value('particle_type', 'shower'))
            keypoint_type = options.get('keypoint_type', self.get_option_value('keypoint_type', 'nu'))
            plane_charge = options.get('plane_charge', self.get_option_value('plane_charge', 'U'))
            marker_size = options.get('marker_size', self.get_option_value('marker_size', 1.0))
            marker_opacity = options.get('marker_opacity', self.get_option_value('marker_opacity', 0.4))
            
            if cluster_source not in self._input_trees_present:
                self.log_error(f"Selected cluster source {cluster_source} not available")
                return []
            
            # Define mappings for indices
            particle_type_indices = {
                'electron': 10,
                'gamma': 11,
                'muon': 12,
                'proton': 13,
                'pion': 14
            }
            
            keypoint_type_indices = {
                'nu': 17,
                'track_start': 18,
                'track_end': 19,
                'shower': 20,
                'delta': 21,
                'michel': 22
            }
            
            plane_charge_indices = {
                'U': 23,
                'V': 24,
                'Y': 25
            }
            
            # Define common hover template
            hover_template = """
            <b>x</b>: %{x}<br>
            <b>y</b>: %{y}<br>
            <b>z</b>: %{z}<br>
            <b>tick</b>: %{customdata[3]}<br>
            <b>U</b>: %{customdata[0]}<br>
            <b>V</b>: %{customdata[1]}<br>
            <b>Y</b>: %{customdata[2]}<br>
            <b>larmatch</b>: %{customdata[4]:.2f}<br>
            <b>e</b>: %{customdata[5]:.2f}<br>
            <b>g</b>: %{customdata[6]:.2f}<br>
            <b>mu</b>: %{customdata[7]:.2f}<br>
            <b>p</b>: %{customdata[8]:.2f}<br>
            <b>pi</b>: %{customdata[9]:.2f}<br>
            """
            
            # Get cluster data
            traces = []
            self.log_info("getting clusters from source: {cluster_source}")
            ev_cluster = iolarlite.get_data("larflowcluster", cluster_source)
            self.log_info(f"Number of clusters from {cluster_source}: {ev_cluster.size()}")
            
            # Process each cluster
            for icluster in range(ev_cluster.size()):
                cluster = ev_cluster.at(icluster)
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
                    custom_data[isp, 3] = hit.tick  # tick
                    custom_data[isp, 4] = hit.track_score  # larmatch score
                    
                    # Particle ID scores
                    for c in range(5):
                        if hit.size() > 10 + c:
                            custom_data[isp, 5 + c] = hit[10 + c]
                    
                    # Keypoint scores
                    for k in range(6):
                        if hit.size() > 17 + k:
                            custom_data[isp, 10 + k] = hit[17 + k]
                
                # Determine coloring based on selected mode
                if coloring_mode == 'cluster':
                    # Random color for entire cluster
                    random_color = np.random.randint(0, 255, 3)
                    color_rgb = f'rgba({random_color[0]},{random_color[1]},{random_color[2]},1.0)'
                    
                    marker_config = {
                        "color": color_rgb,
                        "size": marker_size,
                        "opacity": marker_opacity
                    }
                
                elif coloring_mode == 'larmatch':
                    # Color by larmatch score
                    marker_config = {
                        "color": custom_data[:, 4],  # larmatch score
                        "size": marker_size,
                        "opacity": marker_opacity,
                        "colorscale": "Viridis",
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
                
                elif coloring_mode == 'ssnet':
                    # Color by particle ID score
                    particle_idx = particle_type_indices.get(particle_type, 10)
                    score_idx = particle_idx - 10 + 5  # Adjust to our custom_data index
                    
                    marker_config = {
                        "color": custom_data[:, score_idx],
                        "size": marker_size,
                        "opacity": marker_opacity,
                        "colorscale": "Plasma",
                        "cmin": 0.0,
                        "cmax": 1.0,
                        "colorbar": {
                            "title": f"{particle_type.capitalize()} Score",
                            "thickness": 15,
                            "len": 0.5,
                            "x": 1.0,
                            "xanchor": "left"
                        }
                    }
                
                elif coloring_mode == 'keypoint':
                    # Color by keypoint score
                    keypoint_idx = keypoint_type_indices.get(keypoint_type, 17)
                    score_idx = keypoint_idx - 17 + 10  # Adjust to our custom_data index
                    
                    marker_config = {
                        "color": custom_data[:, score_idx],
                        "size": marker_size,
                        "opacity": marker_opacity,
                        "colorscale": "Cividis",
                        "cmin": 0.0,
                        "cmax": 1.0,
                        "colorbar": {
                            "title": f"{keypoint_type.replace('_', ' ').capitalize()} Score",
                            "thickness": 15,
                            "len": 0.5,
                            "x": 1.0,
                            "xanchor": "left"
                        }
                    }
                
                elif coloring_mode == 'charge':
                    # Color by plane charge
                    plane_idx = plane_charge_indices.get(plane_charge, 23)
                    
                    # Extract charge values if available
                    charges = np.zeros(npts)
                    for isp in range(npts):
                        hit = cluster.at(isp)
                        if hit.size() > plane_idx:
                            charges[isp] = hit[plane_idx]
                    
                    marker_config = {
                        "color": charges,
                        "size": marker_size,
                        "opacity": marker_opacity,
                        "colorscale": "Viridis",
                        "colorbar": {
                            "title": f"{plane_charge} Plane Charge",
                            "thickness": 15,
                            "len": 0.5,
                            "x": 1.0,
                            "xanchor": "left"
                        }
                    }
                
                elif coloring_mode == 'position':
                    # Map XYZ coordinates to RGB values
                    x_norm = (pos[:, 0] - np.min(pos[:, 0])) / (np.max(pos[:, 0]) - np.min(pos[:, 0]) + 1e-8)
                    y_norm = (pos[:, 1] - np.min(pos[:, 1])) / (np.max(pos[:, 1]) - np.min(pos[:, 1]) + 1e-8)
                    z_norm = (pos[:, 2] - np.min(pos[:, 2])) / (np.max(pos[:, 2]) - np.min(pos[:, 2]) + 1e-8)
                    
                    # Create RGB color array
                    rgb_colors = []
                    for i in range(npts):
                        rgb_colors.append(f'rgb({int(x_norm[i]*255)},{int(y_norm[i]*255)},{int(z_norm[i]*255)})')
                    
                    marker_config = {
                        "color": rgb_colors,
                        "size": marker_size,
                        "opacity": marker_opacity
                    }
                
                else:
                    # Default coloring by shower score
                    marker_config = {
                        "color": custom_data[:, 4],  # shower score = renormed_shower_score
                        "size": marker_size,
                        "opacity": marker_opacity,
                        "colorscale": "Viridis",
                        "cmin": 0.0,
                        "cmax": 1.0
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
            self.log_error(f"Error in make_traces: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        try:
            # Update conditional options based on coloring mode
            @app.callback(
                Output('nuinputclusters-conditional-options', 'children'),
                [Input('nuinputclusters-coloring-mode', 'value')],
                prevent_initial_call=True
            )
            def update_conditional_options(coloring_mode):
                if coloring_mode == 'ssnet':
                    return html.Div([
                        html.Label('Particle Type:'),
                        dcc.RadioItems(
                            id='nuinputclusters-particle-type',
                            options=[
                                {'label': 'Electron', 'value': 'electron'},
                                {'label': 'Gamma', 'value': 'gamma'},
                                {'label': 'Muon', 'value': 'muon'},
                                {'label': 'Proton', 'value': 'proton'},
                                {'label': 'Pion', 'value': 'pion'}
                            ],
                            value=self.get_option_value('particle_type', 'electron'),
                            style={'display': 'flex', 'flex-direction': 'column'}
                        )
                    ], style={'margin-bottom': '10px'})
                
                elif coloring_mode == 'keypoint':
                    return html.Div([
                        html.Label('Keypoint Type:'),
                        dcc.RadioItems(
                            id='nuinputclusters-keypoint-type',
                            options=[
                                {'label': 'Neutrino', 'value': 'nu'},
                                {'label': 'Track Start', 'value': 'track_start'},
                                {'label': 'Track End', 'value': 'track_end'},
                                {'label': 'Shower', 'value': 'shower'},
                                {'label': 'Delta', 'value': 'delta'},
                                {'label': 'Michel', 'value': 'michel'}
                            ],
                            value=self.get_option_value('keypoint_type', 'nu'),
                            style={'display': 'flex', 'flex-direction': 'column'}
                        )
                    ], style={'margin-bottom': '10px'})
                
                elif coloring_mode == 'charge':
                    return html.Div([
                        html.Label('Plane:'),
                        dcc.RadioItems(
                            id='nuinputclusters-plane-charge',
                            options=[
                                {'label': 'U Plane', 'value': 'U'},
                                {'label': 'V Plane', 'value': 'V'},
                                {'label': 'Y Plane', 'value': 'Y'}
                            ],
                            value=self.get_option_value('plane_charge', 'U'),
                            style={'display': 'flex', 'flex-direction': 'column'}
                        )
                    ], style={'margin-bottom': '10px'})
                
                else:
                    return html.Div([])  # Empty div for other modes
            
            # Store cluster source when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-source', 'value')],
                prevent_initial_call=True
            )
            def store_cluster_source(value):
                if value:
                    self.set_option_value('cluster_source', value)
                return None
            
            # Store coloring mode when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-coloring-mode', 'value')],
                prevent_initial_call=True
            )
            def store_coloring_mode(value):
                if value:
                    self.set_option_value('coloring_mode', value)
                return None
            
            # Store particle type when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-particle-type', 'value')],
                prevent_initial_call=True
            )
            def store_particle_type(value):
                if value:
                    self.set_option_value('particle_type', value)
                return None
            
            # Store keypoint type when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-keypoint-type', 'value')],
                prevent_initial_call=True
            )
            def store_keypoint_type(value):
                if value:
                    self.set_option_value('keypoint_type', value)
                return None
            
            # Store plane charge when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-plane-charge', 'value')],
                prevent_initial_call=True
            )
            def store_plane_charge(value):
                if value:
                    self.set_option_value('plane_charge', value)
                return None
            
            # Store marker size when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-marker-size', 'value')],
                prevent_initial_call=True
            )
            def store_marker_size(value):
                if value:
                    self.set_option_value('marker_size', value)
                return None
            
            # Store marker opacity when it changes
            @app.callback(
                Output('det3d-hidden-output', 'children', allow_duplicate=True),
                [Input('nuinputclusters-marker-opacity', 'value')],
                prevent_initial_call=True
            )
            def store_marker_opacity(value):
                if value is not None:
                    self.set_option_value('marker_opacity', value)
                return None
            
            logger.info("NuInputClustersPlotter callbacks registered successfully")
        except Exception as e:
            logger.error(f"Error registering NuInputClustersPlotter callbacks: {e}")
            import traceback
            logger.error(traceback.format_exc())