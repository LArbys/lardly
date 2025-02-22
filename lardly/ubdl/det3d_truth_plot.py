import os,sys
from .det3d_plot_factory import register_det3d_plotter
from dash import html
import lardly.data.larlite_mctrack as vis_mctrack
import lardly.data.larlite_mcshower as vis_mcshower
from ublarcvapp import ublarcvapp

def are_products_present( keys ):
    required_trees = ["mctrack_mcreco_tree","mcshower_mcreco_tree"]
    hastrees = True

    for treename in required_trees:
        if treename not in keys:
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('truthplot: no options')]

def make_traces( iolarlite, iolarcv ):
    mcpg = ublarcvapp.mctools.MCPixelPGraph()
    mcpg.buildgraphonly(iolarlite)

    ev_mctrack = iolarlite.get_data("mctrack","mcreco")
    track_traces = vis_mctrack.visualize_larlite_event_mctrack( ev_mctrack, do_sce_correction=True, no_offset=False )
    
    # for showers use mcpg
    return track_traces

register_det3d_plotter("mcreco Trajectories",are_products_present,make_plot_option_widgets,make_traces)