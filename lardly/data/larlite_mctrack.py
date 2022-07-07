import numpy as np

default_pid_colors = {2212:'rgb(153,55,255)', # protons
                      13:'rgb(255,0,0)', # muons
                      -13:'rgb(255,0,0)', # muons
                      211:'rgb(255,128,255)',# pions
                      -211:'rgb(255,128,255)',# pions
                      0:'rgb(0,0,0)'# other
                      }

try:
    from ublarcvapp import ublarcvapp
    tracksce = ublarcvapp.mctools.TruthTrackSCE()
except:
    tracksce = None

def extract_mctrackpts( mctrack, sce=None, no_offset=False ):
    from larlite import larlite, larutil
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5

    # convert mctrack points to image pixels
    steps_np  = np.zeros( (mctrack.size(),3) )
    for istep in range(mctrack.size()):
        step = mctrack.at(istep)
        t = step.T()

        tick = larutil.TimeService.GetME().TPCG4Time2Tick(t) + step.X()/(cm_per_tick)
        x  = (tick - 3200)*cm_per_tick

        if no_offset: # plot raw mcstep X position instead of conversion above
            steps_np[istep,:] = (step.X(),step.Y(),step.Z())
        else:
            steps_np[istep,:] = (x,step.Y(),step.Z())

    return steps_np

def visualize_larlite_event_mctrack( event_mctrack, origin=None,
                                     do_sce_correction=False,
                                     color_labels=default_pid_colors,
                                     width=3, color_by_origin=False, no_offset=False ):

    track_vis = []

    print ("number of mctracks: ",event_mctrack.size())

    for itrack in range(event_mctrack.size()):
        mctrack = event_mctrack.at(itrack)

        if mctrack.PdgCode()==2112:
            continue #skip neutrons

        if origin is not None and origin!=mctrack.Origin():
            continue

        trackvis = visualize_larlite_mctrack( mctrack, do_sce_correction, no_offset )
        track_vis.append( trackvis )

    return track_vis

def visualize_larlite_mctrack( mctrack, origin=None,
                                do_sce_correction=False,
                                color_labels=default_pid_colors,
                                width=3, color_by_origin=False, no_offset=False ):

    pid = mctrack.PdgCode()

    # cosmic origin
    if color_by_origin:
        color = 'rgb(0,0,255)'
        if mctrack.Origin()==1:
            # neutrino pixels
            color = 'rgb(0,255,255)'
    else:
        if pid in color_labels:
            color = color_labels[pid]
        else:
            color = color_labels[0]

    if do_sce_correction and tracksce is not None:
        lltrack = tracksce.applySCE( mctrack )
        npoints = lltrack.NumberTrajectoryPoints()
        steps_np = np.zeros( (npoints,3 ) )
        for ipt in range(npoints):
            for i in range(3):
                steps_np[ipt,i] = lltrack.LocationAtPoint(ipt)(i)
    else:
        steps_np = extract_mctrackpts( mctrack, no_offset )

    trackvis = {
        "type":"scatter3d",
        "x":steps_np[:,0],
        "y":steps_np[:,1],
        "z":steps_np[:,2],
        "mode":"lines",
        "name":"pdg[%d]\nid[%d]"%(pid,mctrack.TrackID()),
        "line":{"color":color,"width":width},
    }

    return trackvis
