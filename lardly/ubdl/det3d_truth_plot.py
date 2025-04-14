import os,sys
from .det3d_plot_factory import register_det3d_plotter
from dash import html
import lardly.data.larlite_mctrack as vis_mctrack
import lardly.data.larlite_mcshower as vis_mcshower
from ublarcvapp import ublarcvapp
from larlite import larlite, larutil

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

def make_traces( iolarlite, iolarcv, recotree ):

    
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5

    mcpg = ublarcvapp.mctools.MCPixelPGraph()
    mcpg.buildgraphonly(iolarlite)

    ev_mctrack = iolarlite.get_data("mctrack","mcreco")
    ev_mcshower = iolarlite.get_data("mcshower","mcreco")
    track_traces = vis_mctrack.visualize_larlite_event_mctrack( ev_mctrack, do_sce_correction=True, no_offset=False )
    print("number of track_trackes: ",len(track_traces))
    print(track_traces)
    
    shower_traces = vis_mcshower.visualize_larlite_event_mcshower( ev_mcshower )
    print("number of shower traces: ",len(shower_traces))
    print(shower_traces)

    traces = []
    if len(track_traces)>0:
        traces += track_traces
    #if len(shower_traces):
    #    traces += shower_traces

    # for showers use mcpg (if have larcv)
    # nnodes = mcpg.node_v.size()
    # for inode in range(nnodes):
    #     node = mcpg.node_v.at(inode)
    #     if node.pid in [-11,11,22]:
    #         # get the mcshower object
    #         if node.type==1:
    #             mcshower = ev_mcshower.at( node.vidx )
    #         else:
    #             mcshower = None
    #         startpt_xyzt = np.array( [node.first_edep_pos[i] for i in range(node.first_edep_pos.size())] )
    #         pmom = np.array( [node.])
    #         E_MeV = node.E_MeV
    #         if mcshower is not None:
    #             endpt = startpt

    return traces

register_det3d_plotter("mcreco Trajectories",are_products_present,make_plot_option_widgets,make_traces)
