import os,sys
import numpy as np

def visualize_larlite_larflowhits( larlite_event_larflowhit, name="",score_threshold=0 ):

    npoints = larlite_event_larflowhit.size()

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()

    xyz = np.zeros( (npoints,4 ) )
    ptsused = 0
    for ipt in xrange(npoints):
        hit = larlite_event_larflowhit.at(ipt)

        if hit.track_score<score_threshold:
            continue

        xyz[ptsused,0] = hit[0]
        xyz[ptsused,1] = hit[1]
        xyz[ptsused,2] = hit[2]
        if hit.size()>=4:
            xyz[ptsused,3] = hit.track_score
        else:
            xyz[ptsused,3] = 1.0
        #print (hit[0],hit[1],hit[2])
        ptsused += 1

    print("num larflow hits=",npoints," abovethreshold(plotted)=",ptsused)
    larflowhits = {
        "type":"scatter3d",
        "x": xyz[:ptsused,0],
        "y": xyz[:ptsused,1],
        "z": xyz[:ptsused,2],
        "mode":"markers",
        "name":name,
        "marker":{"color":xyz[:ptsused,3],"size":1,"opacity":0.8,"colorscale":'Viridis'},
    }

    return larflowhits
