from __future__ import print_function
import os,sys

import numpy as np
from ROOT import std
from larlite import larlite,larutil

def visualize_larlite_spacepoints( larlite_spacepoint_v, color=None, opacity=1.0 ):

    pos = np.zeros( (larlite_spacepoint_v.size(),3) )
    for isp in range( larlite_spacepoint_v.size() ):
        sp = larlite_spacepoint_v.at(isp)
        for i in range(0,3):
            pos[isp,i] = sp.XYZ()[i]
            
    print("[lardly.data.visualize_larlite_spacepoints] num hits=",pos.shape[0])
    spacepoint_plot = {
        "type":"scatter3d",
        "x": pos[:,0],
        "y": pos[:,1],
        "z": pos[:,2],
        "mode":"markers",
        "name":"sp",
        "marker":{"color":'rgb(255,255,255)',"size":1,"opacity":opacity},
    }
    return spacepoint_plot
