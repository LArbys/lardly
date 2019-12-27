import os,sys
import numpy as np

def visualize_larlite_crthit( larlite_crthit ):

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()    
    t_usec = larlite_crthit.ts2_ns*0.001
    dx = t_usec*dv
    
    xyz = np.zeros( (1,3 ) )
    xyz[0,0] = larlite_crthit.x_pos + dx
    xyz[0,1] = larlite_crthit.y_pos
    xyz[0,2] = larlite_crthit.z_pos
    #xyz[0,3] = larlite_crthit.ts2_ns*0.001 # convert to microseconds

    crthit = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"markers",
        "name":"",
        "marker":{"color":"rgb(0,225,255)","size":8,"opacity":0.8},
    }

    return crthit

def visualize_larlite_event_crthit( larlite_event_crthit, name="", window=[-500.0,2700] ):

    npoints = larlite_event_crthit.size()
    num_in_win = 0
    hit_index = []
    for ipt in range(npoints):
        t_usec = larlite_event_crthit.at(ipt).ts2_ns*0.001
        if t_usec>=window[0] and t_usec<=window[1]:
            num_in_win += 1
            hit_index.append(ipt)
        
    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()    
    
    xyz = np.zeros( (num_in_win,4 ) )
    for ipt,idx in enumerate(hit_index):
        crthit = larlite_event_crthit.at(idx)
        xyz[ipt,0] = crthit.x_pos + dv*0.001*crthit.ts2_ns
        xyz[ipt,1] = crthit.y_pos
        xyz[ipt,2] = crthit.z_pos
        xyz[ipt,3] = (float(crthit.plane)+1.0)/4.0

    crthits = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"markers",
        "name":"crthits:{}".format(name),
        "marker":{"color":xyz[:,3],"size":4,"opacity":0.8,"colorscale":"Oryel"},
    }

    return crthits
