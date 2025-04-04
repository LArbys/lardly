import os,sys
from .det3d_plot_factory import register_det3d_plotter
from dash import html
import numpy as np
import lardly.data.larlite_mctrack as vis_mctrack
import lardly.data.larlite_mcshower as vis_mcshower
from ublarcvapp import ublarcvapp
from larlite import larlite, larutil

def are_products_present( keys ):
    required_trees = ["KPSRecoManagerTree"]
    hastrees = True
    print("recoshower check: ",keys)
    for treename in required_trees:
        if treename not in keys:
            print('failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('RecoNu: no options')]

def make_traces( iolarlite, iolarcv, recoTree ):
    
    nvertices = recoTree.nuvetoed_v.size()
    print("[det3d_recoshower_plot.py] num vertices: ",nvertices)
    traces = []
    for ivtx in range(nvertices):
        nuvtx = recoTree.nuvetoed_v.at(ivtx)
        nshowers = nuvtx.shower_v.size()
        for ishower in range(nshowers):
            shower = nuvtx.shower_v.at(ishower) # a larlite::larflowcluster object
            npts = shower.size()
            ptpos = np.zeros((npts,3))
            for i in range(npts):
                for v in range(3):
                    ptpos[i,v] = shower.at(i)[v]
            ic = np.random.randint(0,255,3)
            rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
            shower_trace = {
                "type":"scatter3d",
                "x":ptpos[:,0],
                "y":ptpos[:,1],
                "z":ptpos[:,2],
                "mode":"markers",
                "name":f"recoShower[{ivtx},{ishower}]",
                "marker":{"color":rcolor,"size":1.0,"opacity":0.5},
                #"customdata":meta,
                #"hovertemplate":hovertemplate
            }
            traces.append(shower_trace)

        ntracks = nuvtx.track_v.size()
        for itrack in range(ntracks):
            track = nuvtx.track_v.at(itrack)
            trackhits = nuvtx.track_hitcluster_v.at(itrack)
            npts = trackhits.size()
            ptpos = np.zeros((npts,3))
            for i in range(npts):
                for v in range(3):
                    ptpos[i,v] = trackhits.at(i)[v]
            ic = np.random.randint(0,255,3)
            rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
            trackhit_trace = {
                "type":"scatter3d",
                "x":ptpos[:,0],
                "y":ptpos[:,1],
                "z":ptpos[:,2],
                "mode":"markers",
                "name":f"recoTrack[{ivtx},{itrack}]",
                "marker":{"color":rcolor,"size":1.0,"opacity":0.5},
                #"customdata":meta,
                #"hovertemplate":hovertemplate
            }
            traces.append(trackhit_trace)

    return traces

register_det3d_plotter("RecoNu",are_products_present,make_plot_option_widgets,make_traces)
