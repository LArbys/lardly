import numpy as np

def extract_mctrackpts( mctrack, sce=None ):
    from larlite import larlite, larutil
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5

    # convert mctrack points to image pixels
    steps_np  = np.zeros( (mctrack.size(),3) )
    for istep in range(mctrack.size()):
        step = mctrack.at(istep)
        t = step.T()

        tick = larutil.TimeService.GetME().TPCG4Time2Tick(t) + step.X()/(cm_per_tick)
        x  = (tick - 3200)*cm_per_tick

        steps_np[istep,:] = (x,step.Y(),step.Z())
    return steps_np

def visualize_larlite_event_mctrack( event_mctrack, origin=None ):

    track_vis = []
    print ("number of mctracks: ",event_mctrack.size())
    for itrack in range(event_mctrack.size()):
        mctrack = event_mctrack.at(itrack)
        steps_np = extract_mctrackpts( mctrack )
        if mctrack.PdgCode()==2112:
            continue

        if origin is not None and origin!=mctrack.Origin():
            continue

        # cosmic origin
        color = 'rgb(0,0,255)'
        if mctrack.Origin()==1:
            # neutrino pixels
            color = 'rgb(0,255,255)'


        trackvis = {
            "type":"scatter3d",
            "x":steps_np[:,0],
            "y":steps_np[:,1],
            "z":steps_np[:,2],
            "mode":"lines",
            "name":"pdg[%d]\nid[%d]"%(mctrack.PdgCode(),mctrack.TrackID()),
            "line":{"color":color,"width":2},
            }
        track_vis.append( trackvis )
    return track_vis
