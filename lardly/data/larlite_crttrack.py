import os,sys
import numpy as np

def visualize_larlite_crttrack( larlite_crttrack, notimeshift=False ):

    if notimeshift:
        dx = 0.0
        t_usec = 0.0
    else:
        from larlite import larutil
        dv = larutil.LArProperties.GetME().DriftVelocity()    
        t_usec = 0.5*(larlite_crttrack.ts2_ns_h1+larlite_crttrack.ts2_ns_h2)*0.001 # convert to microseconds
        dx = t_usec*dv
    
    xyz = np.zeros( (2,4 ) )
    xyz[0,0] = larlite_crttrack.x1_pos + dx
    xyz[0,1] = larlite_crttrack.y1_pos
    xyz[0,2] = larlite_crttrack.z1_pos
    xyz[0,3] = larlite_crttrack.ts2_ns_h1*0.001
    xyz[1,0] = larlite_crttrack.x2_pos + dx
    xyz[1,1] = larlite_crttrack.y2_pos
    xyz[1,2] = larlite_crttrack.z2_pos
    xyz[1,3] = larlite_crttrack.ts2_ns_h2*0.001

    crttrack = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"markers",
        "name":"",
        "marker":{"color":"rgb(0,225,0)","size":8,"opacity":0.8},
    }

    return crttrack

def visualize_larlite_event_crttrack( larlite_event_crttrack, name="", window=[-500.0,2700], notimeshift=False ):

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()    
    
    ntracks = larlite_event_crttrack.size()

    crttracks_v = []
    for itrack in range(ntracks):
        crttrack = larlite_event_crttrack.at(itrack)
        if notimeshift:
            dx = 0.0
        else:
            t_usec = 0.5*(crttrack.ts2_ns_h1 + crttrack.ts2_ns_h2)*0.001
            dx = t_usec*dv
        xyz = np.zeros( (2,3 ) )
        xyz[0,0] = crttrack.x1_pos + dx
        xyz[0,1] = crttrack.y1_pos
        xyz[0,2] = crttrack.z1_pos
        xyz[1,0] = crttrack.x2_pos + dx
        xyz[1,1] = crttrack.y2_pos
        xyz[1,2] = crttrack.z2_pos 

        crttrack = {
            "type":"scatter3d",
            "x": xyz[:,0],
            "y": xyz[:,1],
            "z": xyz[:,2],
            "mode":"line",
            "name":"crttracks:{}".format(name),
            "line":{"color":"rgb(0,225,0)","width":2,"opacity":0.8},
        }
        crttracks_v.append( crttrack )

    return crttracks_v
