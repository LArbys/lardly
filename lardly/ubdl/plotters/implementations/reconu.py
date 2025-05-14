"""
RecoNu plotter implementation

This module implements a plotter for reconstructed neutrino vertices.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from lardly.ubdl.plotters.base import BasePlotter
from lardly.ubdl.core.state import state_manager
from larlite import larutil

class RecoNuPlotter(BasePlotter):
    """
    Plotter for reconstructed neutrino vertices
    
    This plotter visualizes reconstructed neutrino vertices, including their
    associated tracks and showers.
    """
    
    def __init__(self):
        """Initialize the RecoNu plotter"""
        super().__init__("RecoNu", "Reconstructed Neutrino Vertices")
    
    def is_applicable(self, tree_keys: List[str]) -> bool:
        """
        Check if this plotter is applicable
        
        Args:
            tree_keys: List of tree keys available in the data
            
        Returns:
            True if the required trees are available
        """
        return "KPSRecoManagerTree" in tree_keys
    
    def initialize_options(self) -> None:
        """Initialize options for this plotter"""
        self.set_option_value("selected_vertex", "all")
        self.set_option_value("show_tracks", True)
        self.set_option_value("show_showers", True)
        self.set_option_value("show_vertices", True)
    
    def make_option_widgets(self) -> List[Any]:
        """
        Create option widgets for this plotter
        
        Returns:
            List of Dash components for options
        """
        return [
            html.Div([
                html.Label('RecoNu Options:'),
                html.Div([
                    html.Label('Select Vertex:'),
                    dcc.Dropdown(
                        id='reconu-vertex-selector',
                        options=[{'label': 'All Vertices', 'value': 'all'}],
                        value=self.get_option_value("selected_vertex", "all"),
                        clearable=False
                    )
                ], style={'margin-bottom': '10px'}),
                html.Div([
                    html.Label('Display Options:'),
                    dcc.Checklist(
                        id='reconu-display-options',
                        options=[
                            {'label': 'Show Tracks', 'value': 'tracks'},
                            {'label': 'Show Showers', 'value': 'showers'},
                            {'label': 'Show Vertices', 'value': 'vertices'},
                        ],
                        value=[
                            'tracks' if self.get_option_value("show_tracks", True) else None,
                            'showers' if self.get_option_value("show_showers", True) else None,
                            'vertices' if self.get_option_value("show_vertices", True) else None,
                        ],
                        style={'display': 'flex', 'flex-direction': 'column'}
                    )
                ]),
                html.Div(id='reconu-debug-output', style={'color': 'red'})
            ])
        ]
    
    def get_option_component_ids(self):
        """Get component IDs used by this plotter"""
        return ['reconu-vertex-selector', 'reconu-display-options']

    def make_traces(self, tree_dict: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create traces for this plotter
        
        Args:
            tree_dict: Dictionary of trees (data sources)
            options: Optional dictionary of options for this plotter
            
        Returns:
            List of plotly trace dictionaries
        """
        recoTree = tree_dict.get('recoTree')
        if recoTree is None:
            self.log_error("recoTree not found in tree_dict")
            return []
        
        # Get options, using provided options or falling back to stored options
        if options is None:
            options = {}
        
        selected_vertex = options.get('selected_vertex', self.get_option_value('selected_vertex', 'all'))
        show_tracks = 'tracks' in options.get('display_options', []) if 'display_options' in options else self.get_option_value('show_tracks', True)
        show_showers = 'showers' in options.get('display_options', []) if 'display_options' in options else self.get_option_value('show_showers', True)
        show_vertices = 'vertices' in options.get('display_options', []) if 'display_options' in options else self.get_option_value('show_vertices', True)
        
        nvertices = recoTree.nuvetoed_v.size()
        nselvars = recoTree.nu_sel_v.size()
        self.log_info(f"Number of vertices: {nvertices}, Number of selection var classes: {nselvars}")
        
        traces = []
        
        # arrays for nu-vertex plot
        # [0-3] x, y, z, tick,
        # [4-7] t, U, V, Y,
        # [8-11] n_primary tracks, n_primary showers, n second track, n second showers
        # [12-15] max-kp-score, nu-score, origin kptype, ivtx
        # [16-19] (optional) unreco fracion: U pix, V pix, Y pix, all spacepoints
        if nvertices > 0:
            vtxinfo = np.zeros((nvertices, 20))
        else:
            vtxinfo = None
            
        # Process vertices based on selection
        vertices_to_process = []
        if selected_vertex == 'all':
            vertices_to_process = range(nvertices)
        else:
            try:
                vtx_idx = int(selected_vertex)
                if 0 <= vtx_idx < nvertices:
                    vertices_to_process = [vtx_idx]
            except:
                # Fall back to all vertices if selection is invalid
                vertices_to_process = range(nvertices)
        
        cm_per_tick = larutil.LArProperties.GetME().DriftVelocity() * 0.5
        
        # Process each selected vertex
        for ivtx in vertices_to_process:
            nuvtx = recoTree.nuvetoed_v.at(ivtx)
            if nvertices == nselvars:
                nusel = recoTree.nu_sel_v.at(ivtx)
            else:
                nusel = None
                
            self.log_info(f"RecoNu Vertex[{ivtx}]")
            self.log_info(f"  ntracks={nuvtx.track_v.size()}")
            self.log_info(f"  nshowers={nuvtx.shower_v.size()}")
            
            # Process showers if enabled
            if show_showers:
                nshowers = nuvtx.shower_v.size()
                for ishower in range(nshowers):
                    shower = nuvtx.shower_v.at(ishower)  # a larlite::larflowcluster object
                    npts = shower.size()
                    ptpos = np.zeros((npts, 3))
                    for i in range(npts):
                        for v in range(3):
                            ptpos[i, v] = shower.at(i)[v]
                    ic = np.random.randint(0, 255, 3)
                    rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
                    primorsec = "1"
                    if ishower < nuvtx.shower_isSecondary_v.size() and nuvtx.shower_isSecondary_v.at(ishower)==1:
                        primorsec="2"
                    shower_trace = {
                        "type": "scatter3d",
                        "x": ptpos[:, 0],
                        "y": ptpos[:, 1],
                        "z": ptpos[:, 2],
                        "mode": "markers",
                        "name": f"Nu[{ivtx}]:S{primorsec}[{ishower}]",
                        "marker": {"color": rcolor, "size": 1.0, "opacity": 0.5},
                    }

                    trunk_pos = np.zeros( (2,3) )
                    for i in range(3):
                        trunk_pos[0,i] = nuvtx.shower_trunk_v.at(ishower).LocationAtPoint(0)[i]
                        trunk_pos[1,i] = nuvtx.shower_trunk_v.at(ishower).LocationAtPoint(1)[i]
                    trunk_trace = {
                        "type": "scatter3d",
                        "x": trunk_pos[:, 0],
                        "y": trunk_pos[:, 1],
                        "z": trunk_pos[:, 2],
                        "mode": "lines",
                        "name": f"Nu[{ivtx}]:S{primorsec}[{ishower}]",
                        "line": {"color": rcolor, "width":3.0},
                    }
                    traces.append(shower_trace)
                    traces.append(trunk_trace)
            
            # Process tracks if enabled
            if show_tracks:
                ntracks = nuvtx.track_v.size()
                for itrack in range(ntracks):
                    track = nuvtx.track_v.at(itrack)
                    trackhits = nuvtx.track_hitcluster_v.at(itrack)
                    npts = trackhits.size()
                    ptpos = np.zeros((npts, 3))
                    for i in range(npts):
                        for v in range(3):
                            ptpos[i, v] = trackhits.at(i)[v]
                    ic = np.random.randint(0, 255, 3)
                    rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
                    primorsec = "1"
                    if itrack < nuvtx.track_isSecondary_v.size() and nuvtx.track_isSecondary_v.at(itrack)==1:
                        primorsec="2"
                    trackhit_trace = {
                        "type": "scatter3d",
                        "x": ptpos[:, 0],
                        "y": ptpos[:, 1],
                        "z": ptpos[:, 2],
                        "mode": "markers",
                        "name": f"Nu[{ivtx}]:T{primorsec}[{itrack}]",
                        "marker": {"color": rcolor, "size": 1.0, "opacity": 0.5},
                    }

                    track_dir = nuvtx.track_dir_v.at(itrack)
                    track_start = track.LocationAtPoint(0)
                    trunk_pos = np.zeros( (2,3) )
                    for i in range(3):
                        trunk_pos[0,i] = track_start[i]
                        trunk_pos[1,i] = track_start[i] + 5.0*track_dir[i]
                    trunk_trace = {
                        "type": "scatter3d",
                        "x": trunk_pos[:, 0],
                        "y": trunk_pos[:, 1],
                        "z": trunk_pos[:, 2],
                        "mode": "lines",
                        "name": f"Nu[{ivtx}]:T{primorsec}[{itrack}]",
                        "line": {"color": rcolor, "width":3.0},
                    }

                    track_pts = np.zeros( (track.NumberTrajectoryPoints(),3))
                    for i in range( track_pts.shape[0] ):
                        for v in range(3):
                            track_pts[i,v] = track.LocationAtPoint(i)[v]
                    trackline_trace = {
                        "type": "scatter3d",
                        "x": track_pts[:, 0],
                        "y": track_pts[:, 1],
                        "z": track_pts[:, 2],
                        "mode": "lines",
                        "name": f"Nu[{ivtx}]:T{primorsec}[{itrack}]",
                        "line": {"color": rcolor, "width":1.0},
                    }

                    traces.append(trunk_trace)
                    traces.append(trackhit_trace)
                    traces.append(trackline_trace)

            # Gather data for nu vertex hover text
            vtxinfo[ivtx, 0] = nuvtx.pos[0]
            vtxinfo[ivtx, 1] = nuvtx.pos[1]
            vtxinfo[ivtx, 2] = nuvtx.pos[2]
            vtxinfo[ivtx, 3] = (nuvtx.tick - 3200) * 0.5  # t in usec relative to trigger
            vtxinfo[ivtx, 4] = nuvtx.tick
            vtxinfo[ivtx, 5] = nuvtx.col_v[0]  # u-plane wire
            vtxinfo[ivtx, 6] = nuvtx.col_v[1]  # v-plane wire
            vtxinfo[ivtx, 7] = nuvtx.col_v[2]  # y-plane wire
            
            # Count primary tracks and showers
            nprim_tracks = 0
            nprim_showers = 0
            nsec_tracks  = 0
            nsec_showers = 0
            for itrack in range(nuvtx.track_v.size()):
                if itrack < nuvtx.track_isSecondary_v.size():
                    if nuvtx.track_isSecondary_v.at(itrack) == 0:
                        nprim_tracks += 1
                    else:
                        nsec_tracks += 1
                elif nuvtx.track_isSecondary_v.size() == 0:
                    nprim_tracks += 1
                    
            for ishower in range(nuvtx.shower_v.size()):
                if ishower < nuvtx.shower_isSecondary_v.size():
                    if nuvtx.shower_isSecondary_v.at(ishower) == 0:
                        nprim_showers += 1
                    else:
                        nsec_showers += 1
                elif nuvtx.shower_isSecondary_v.size() == 0:
                    nprim_showers += 1
                    
            vtxinfo[ivtx, 8] = nprim_tracks
            vtxinfo[ivtx, 9] = nprim_showers
            vtxinfo[ivtx, 10] = nsec_tracks
            vtxinfo[ivtx, 11] = nsec_showers
            vtxinfo[ivtx, 12] = nuvtx.netScore
            vtxinfo[ivtx, 13] = nuvtx.netNuScore
            vtxinfo[ivtx, 14] = nuvtx.keypoint_type
            vtxinfo[ivtx, 15] = ivtx
            
            if nusel is not None:
                try:
                    for j in range(nusel.unreco_fraction_v.size()):
                        vtxinfo[ivtx, 16 + j] = nusel.unreco_fraction_v[j]
                except:
                    pass

        # Create vertex trace if enabled
        if show_vertices and nvertices > 0:
            nu_hover_template = """
            <b>x</b>: %{x:.1f}<br>
            <b>y</b>: %{y:.1f}<br>
            <b>z</b>: %{z:.1f}<br>
            <b>[NuCand %{customdata[12]}]</b><br>
            <b>t</b>: %{customdata[0]:.1f} usec<br>
            <b>tick</b>: %{customdata[1]:.0f}<br>
            <b>U</b>: %{customdata[2]:.0f}<br>
            <b>V</b>: %{customdata[3]:.0f}<br>
            <b>Y</b>: %{customdata[4]:.0f}<br>
            <b>nprim tracks</b>: %{customdata[5]:.0f}<br>
            <b>nprim showers</b>: %{customdata[6]:.0f}<br>
            <b>nsec tracks</b>: %{customdata[7]:.0f}<br>
            <b>nsec showers</b>: %{customdata[8]:.0f}<br>
            <b>max-kp score</b>: %{customdata[9]:.2f}<br>
            <b>nu-kp score</b>: %{customdata[10]:.2f}<br>
            <b>kp type</b>: %{customdata[11]:.0f}<br>
            """
            
            if nvertices == nselvars:
                this_template = "%s" % (nu_hover_template)
                this_template += "<b>unreco frac</b> %{customdata[13]:.2f} %{customdata[14]:.2f} %{customdata[15]:.2f} %{customdata[16]:.2f}<br>"
            else:
                this_template = nu_hover_template
            
            # Filter vertices based on selection
            vert_indices = []
            for ivtx in vertices_to_process:
                vert_indices.append(ivtx)
            
            # Create vertex trace
            filtered_vtxinfo = vtxinfo[vert_indices]
            nu_trace = {
                "type": "scatter3d",
                "x": filtered_vtxinfo[:, 0],
                "y": filtered_vtxinfo[:, 1],
                "z": filtered_vtxinfo[:, 2],
                "mode": "markers",
                "name": "recoNu",
                "hovertemplate": this_template,
                "customdata": filtered_vtxinfo[:, 3:],
                "marker": {"color": 'rgb(255,0,0)', "size": 5, "opacity": 0.3},
            }
            traces.append(nu_trace)
        
        return traces

    def register_callbacks(self, app):
        """Register callbacks specific to this plotter"""
        # Update vertex dropdown options when data is loaded
        @app.callback(
            Output('reconu-vertex-selector', 'options'),
            [Input('io-nav-button-load-entry', 'n_clicks'),
            Input('button-load-det3d-fig', 'n_clicks'),
            Input('det3d-viewer-checklist-plotchoices', 'value')],
            prevent_initial_call=True
        )
        def update_vertex_dropdown(io_clicks, plot_clicks, selected_plots):
            print("update_vertex_dropdown callback triggered")
            ctx = dash.callback_context
            if not ctx.triggered:
                return [{'label': 'All Vertices', 'value': 'all'}]
                
            # Only update if RecoNu is in selected plots
            if selected_plots is None or 'RecoNu' not in selected_plots:
                return [{'label': 'All Vertices', 'value': 'all'}]
            
            try:
                # Get the loaded RecoTree
                from lardly.ubdl.io.io_manager import get_tree_dict
                tree_dict = get_tree_dict()
                recoTree = tree_dict.get('recoTree')
                
                if recoTree is None:
                    print("RecoTree is None")
                    return [{'label': 'All Vertices', 'value': 'all'}]
                
                # Get the number of vertices
                nvertices = recoTree.nuvetoed_v.size()
                print(f"Found {nvertices} vertices")
                options = [{'label': 'All Vertices', 'value': 'all'}]
                
                # Add an option for each vertex
                for i in range(nvertices):
                    options.append({'label': f'Vertex {i}', 'value': str(i)})
                
                print(f"Returning options: {options}")
                return options
            except Exception as e:
                print(f"Error updating vertex dropdown: {e}")
                import traceback
                traceback.print_exc()
                return [{'label': 'All Vertices', 'value': 'all'}]
        
        # Store selected vertex in state when it changes
        @app.callback(
            Output('det3d-hidden-output', 'children',allow_duplicate=True),
            [Input('reconu-vertex-selector', 'value')],
            prevent_initial_call=True
        )
        def store_selected_vertex(value):
            if value is not None:
                self.set_option_value('selected_vertex', value)
            return None
        
        # Store display options in state when they change
        @app.callback(
            Output('det3d-hidden-output', 'children', allow_duplicate=True),
            [Input('reconu-display-options', 'value')],
            prevent_initial_call=True
        )
        def store_display_options(value):
            if value is not None:
                display_options = {
                    'show_tracks': 'tracks' in value,
                    'show_showers': 'showers' in value,
                    'show_vertices': 'vertices' in value
                }
                for k, v in display_options.items():
                    self.set_option_value(k, v)
            return None
