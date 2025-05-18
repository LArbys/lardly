"""
MCTruth plotter implementation

This module implements a plotter for Monte Carlo truth information,
including tracks and showers.
"""
from typing import Dict, Any, List, Optional
import traceback
from math import sqrt
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
        self.set_option_value("show_vertices", True)
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
                            {'label': 'Show Nu Vertices', 'value': 'vertices'},
                            {'label': 'Show Tracks', 'value': 'tracks'},
                            {'label': 'Show Showers', 'value': 'showers'},
                            {'label': 'Apply SCE Correction', 'value': 'sce'},
                            {'label': 'No Tick Offset', 'value': 'no_offset'},
                        ],
                        value=[
                            'vertices' if self.get_option_value("show_vertices", True) else None,
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
        show_vertices = 'vertices' in display_options if 'display_options' in options else self.get_option_value('show_vertices', True)
        do_sce_correction = 'sce' in display_options if 'display_options' in options else self.get_option_value('do_sce_correction', True)
        no_offset = 'no_offset' in display_options if 'display_options' in options else self.get_option_value('no_offset', False)
        
        # dump MC particle graph
        self.log_info('MCPixelPGraph Start')
        mcpg = ublarcvapp.mctools.MCPixelPGraph()
        mcpg.buildgraphonly( iolarlite )
        mcpg.printGraph(0,False)
        self.log_info('MCPixelPGraph End')

        traces = []

        if show_vertices:
            nunode = mcpg.findTrackID(0) # neutrino given trackid=0
            x = [nunode.start[0]]
            y = [nunode.start[1]]
            z = [nunode.start[2]]
            E_MeV = nunode.E_MeV
            nu_hover="""
            <b>x</b>: %{x:.2f}<br>
            <b>y</b>: %{y:.2f}<br>
            <b>z</b>: %{z:.2f}<br>
            """
            nu_hover +=f"<b>E</b>: {E_MeV} MeV<br>"
            
            nu_trace = {
                    "type":"scatter3d",
                    "x":x,
                    "y":y,
                    "z":z,
                    "mode":"markers",
                    "name":f"NuVtx",
                    "marker":{"color":'rgba(0,0,0,1)',"size":4},
                    "hovertemplate":nu_hover,
                }
            traces.append( nu_trace )
        
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
            
            # shower_traces = vis_mcshower.visualize_larlite_event_mcshower(
                # ev_mcshower,
                # origin=origin_filter,
                # apply_sce=do_sce_correction,
                # no_offset=no_offset
            # )
            # traces.extend(shower_traces)

            # an alternative shower plotter
            shower_traces = []
            for ishower in range(ev_mcshower.size()):
                shower = ev_mcshower.at(ishower)
                tid = shower.TrackID()
                pid = shower.PdgCode()
                
                originpt = [shower.Start().X(), shower.Start().Y(), shower.Start().Z(), shower.Start().T()]
                try:
                    origin_dir = [shower.StartDir().X() , shower.StartDir().Y(), shower.StartDir().Z()]
                except:
                    # bad origin, type to skip
                    continue

                dirnorm = 0.
                for i in range(3):
                    dirnorm += origin_dir[i]*origin_dir[i]
                if dirnorm<1.0e-6:
                    continue # bad

                #print(originpt)
                #print(origin_dir)
                profpts   = np.zeros( (2,3) )
                customdata = []
                try:
                    profmom = shower.DetProfile().Momentum().Vect()
                    momvec=[profmom.Px(),profmom.Py(),profmom.Pz()]
                    profstart = [ shower.DetProfile().Position().Vect()[i] for i in range(3) ]
                    for profx in profstart:
                        if profx<-1e4 or profx>1e4:
                            raise ValueError(f'Bad shower profile start value: {profx}')
                    momlen = sqrt(momvec[0]*momvec[0] + momvec[1]*momvec[1] + momvec[2]*momvec[2])
                    if momlen>0.0:
                        for i in range(3):
                            momvec[i] = momvec[i]/momlen

                    for i in range(3):
                        profpts[0,i] = shower.DetProfile().Position().Vect()[i]
                        profpts[1,i] = shower.DetProfile().Position().Vect()[i] + 20.0*momvec[i]
                    plotlabel = "showerprof"
                    

                except Exception:
                    self.log_info(f'No/Bad DetProfile info for TrackID{tid}, pdg={pid}')
                    self.log_info(traceback.format_exc())

                    for i in range(3):
                        profpts[0,i] = originpt[i]
                        profpts[1,i] = originpt[i] + 20.0*origin_dir[i]
                    plotlabel="showerorigin"
    
                profcolor = 'rgb(0,255,255)' if pid==22 else 'rgb(0,255,0)'
                print(profpts)
        
                shower_prof_trace = {
                    "type":"scatter3d",
                    "x":profpts[:,0],
                    "y":profpts[:,1],
                    "z":profpts[:,2],
                    "mode":"lines",
                    "name":f"{plotlabel}[{tid}]",
                    "line":{"color":profcolor,"width":4},
                    #"customdata":meta,
                    #"hovertemplate":hovertemplate
                }
                shower_traces.append( shower_prof_trace)
            self.log_info(f"Number of shower traces: {len(shower_traces)}")
            if len(shower_traces):
                traces += shower_traces
            
        
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
