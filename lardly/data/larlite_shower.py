import os,sys
from ROOT import std
from larlite import larlite,larutil
import numpy as np

def visualize3d_larlite_shower( larlite_shower ):
    shr = larlite_shower
    shrlen = shr.Length()
    shower_trace = {
        "type":"cone",
        "x":[shr.ShowerStart().X()],
        "y":[shr.ShowerStart().Y()],
        "z":[shr.ShowerStart().Z()],
        "u":[-shrlen*shr.Direction().X()],
        "v":[-shrlen*shr.Direction().Y()],
        "w":[-shrlen*shr.Direction().Z()],
        "anchor":"tip",
        "sizemode":"absolute",
        "opacity":0.7,
        "sizeref":(int)(shrlen*2),
        }
    return shower_trace

def visualize2d_larlite_shower( larlite_shower ):

    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5
    
    shr = larlite_shower
    shrlen = shr.Length()

    # get projections: vertex
    vtx_v = std.vector("double")(3)
    vtx_v[0] = shr.ShowerStart().X()
    vtx_v[1] = shr.ShowerStart().Y()
    vtx_v[2] = shr.ShowerStart().Z()

    # get projections: end
    end_v = std.vector("double")(3)
    end_v[0] = vtx_v[0] + shrlen*shr.Direction().X()
    end_v[1] = vtx_v[1] + shrlen*shr.Direction().Y()
    end_v[2] = vtx_v[2] + shrlen*shr.Direction().Z()

    # wire coordintes
    vtx = [ larutil.Geometry.GetME().WireCoordinate(vtx_v,p) for p in range(3) ]
    end = [ larutil.Geometry.GetME().WireCoordinate(end_v,p) for p in range(3) ]

    shower_traces = {}
    for p in range(3):
        shower_trace = {
            "type":"scatter",
            "x":[ vtx[p], end[p] ],
            "y":[ 3200+vtx_v[0]/cm_per_tick,3200+end_v[0]/cm_per_tick],
            "mode":"lines",
            "line":{"color":"rgb(255,155,255)"},
        }
        shower_traces[p] = shower_trace
        

    return shower_traces
    
