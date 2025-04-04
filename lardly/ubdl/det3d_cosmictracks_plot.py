from dash import html
import numpy as np
from .det3d_plot_factory import register_det3d_plotter
import yaml
import os
from lardly.data.larlite_track import visualize_larlite_track

BOUNDARY_COSMIC_TREE_NAME = "boundarycosmicnoshift"
CONTAINED_COSMIC_TREE_NAME = "containedcosmic"

def get_treenames_from_yaml():
    global BOUNDARY_COSMIC_TREE_NAME
    global CONTAINED_COSMIC_TREE_NAME
    return ["track_boundarycosmicnoshift_tree","track_containedcosmic_tree"]

def are_products_present( keys ):

    required_trees = get_treenames_from_yaml()
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('[det3d_cosmictracks_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('cosmictracks: no options')]

def make_traces( iolarlite, iolarcv, recoTree ):
    print("call det3d_cosmictracks_plot.make_traces")
    
    ev_boundary  = iolarlite.get_data("track",BOUNDARY_COSMIC_TREE_NAME)
    ev_contained = iolarlite.get_data("track",CONTAINED_COSMIC_TREE_NAME)
    nboundary = ev_boundary.size()
    ncontained = ev_contained.size()
    print("  num boundary cosmic tracks: ",nboundary)
    print("  num contained cosmic tracks: ",ncontained)

    if nboundary+ncontained==0:
        return []

    traces = []
    ntracks = 0
    colors = ['rgb(102,102,53)','rgb(153,51,0)']
    for itype,ev_container in enumerate([ev_boundary,ev_contained]):
        for itrack in range(ev_container.size()):
            track = ev_container.at(itrack)
            track_trace = visualize_larlite_track( track, track_id=ntracks, color=colors[itype] )
            traces.append(track_trace)
            ntracks += 1
            
    return traces

register_det3d_plotter("cosmictracks",are_products_present,make_plot_option_widgets,make_traces)




