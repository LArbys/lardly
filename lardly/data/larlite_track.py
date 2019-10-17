import os,sys
import numpy as np

def visualize_larlite_track( larlite_track, track_id=None ):

    npoints = larlite_track.NumberTrajectoryPoints()
    xyz = np.zeros( (npoints,3 ) )
    for ipt in range(npoints):
        for i in range(3):
            xyz[ipt,i] = larlite_track.LocationAtPoint(ipt)(i)

    if track_id is None:
        name = ""
    else:
        name = ""
        if type(track_id) is int:
            name = "tid[{}]".format(track_id)
        elif type(track_id) is str:
            name = track_id
        
    track = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"lines",
        "name":name,
        "line":{"color":"rgb(255,0,0)","width":2},
    }

    return track
