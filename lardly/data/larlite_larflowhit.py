import os,sys
import numpy as np

def visualize_larlite_larflowhits( larlite_event_larflowhit, name="",score_threshold=0,
                                   max_hits=None, score_index=None, plot_renormed_shower_score=False ):

    npoints = larlite_event_larflowhit.size()

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()

    nplot = npoints
    sample = False
    downsample_fraction = 1.0
    if max_hits is not None and type(max_hits) is int and max_hits<npoints:
        nplot = max_hits
        sample = True
        downsample_fraction = float(nplot)/float(npoints)
    
    xyz = np.zeros( (nplot,4 ) )
    ptsused = 0
    ipt = -1
    nlaps = 0
    while ptsused<nplot and nlaps<2:
        ipt+=1
        if ipt<0:
            continue
        if ipt>=npoints:
            ipt=0
            nlaps+=1
            #print("[visualize_larlite_larflowhits] starting lap ",nlaps)
        
        hit = larlite_event_larflowhit.at(ipt)

        if hit.track_score<score_threshold:
            continue

        if sample and np.random.uniform()>downsample_fraction:
            continue
        
        xyz[ptsused,0] = hit[0]
        xyz[ptsused,1] = hit[1]
        xyz[ptsused,2] = hit[2]
        if plot_renormed_shower_score:
            xyz[ptsused,3] = hit.renormed_shower_score
        else:
            if hit.size()>=4:            
                if score_index is None or type(score_index) is not int:
                    xyz[ptsused,3] = hit.track_score
                else:
                    xyz[ptsused,3] = hit[score_index]
            else:
                xyz[ptsused,3] = 1.0
        #print (hit[0],hit[1],hit[2])
        ptsused += 1

    #print("num larflow hits given=",npoints," plotted=",ptsused)
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
