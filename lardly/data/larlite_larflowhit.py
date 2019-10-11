import os,sys
import numpy as np

def visualize_larlite_larflowhits( larlite_event_larflowhit, name="" ):

    npoints = larlite_event_larflowhit.size()

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()    

    print "num larflow hits: ",npoints
    xyz = np.zeros( (npoints,3 ) )
    for ipt in xrange(npoints):
        hit = larlite_event_larflowhit.at(ipt)
        xyz[ipt,0] = hit[0]
        xyz[ipt,1] = hit[1]
        xyz[ipt,2] = hit[2]
        print hit[0],hit[1],hit[2]

    larflowhits = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"markers",
        "name":name,
        "marker":{"color":"rgb(255,225,225)","size":1,"opacity":0.8},
    }

    return larflowhits
