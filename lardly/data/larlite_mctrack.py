import numpy as np
import ROOT as rt

# define the default colors for particles
from .default_pid_colors import default_pid_colors,get_pid_color

try:
    from ublarcvapp import ublarcvapp
    tracksce = ublarcvapp.mctools.TruthTrackSCE()
    tracksce.set_verbosity(2)
except:
    tracksce = None

def extract_mctrackpts( mctrack, sce=None, no_offset=False, set_tick=0, trigger_tick=3200 ):

    from larlite import larlite, larutil
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5

    geo = larlite.larutil.Geometry.GetME()

    #print("no offset ", no_offset)
    #print("set_tick in extract_mctrackpts: ", set_tick)
    if mctrack.size()==0:
        return None

    # convert mctrack points to image pixels
    steps = []
    for istep in range(mctrack.size()):
        step = mctrack.at(istep)
        t = step.T()

        loc = rt.TVector3( step.X(), step.Y(), step.Z() )
        cryo_tpc_idx = geo.GetContainingCryoAndTPCIDs( loc )
        #if cryo_tpc_idx.size()==0:
        #    continue

        if set_tick!=0:
            tick = set_tick
            #x  = step.X()+(2399-3200-(tick-3200))*cm_per_tick
            x  = step.X()+(tick-trigger_tick)*cm_per_tick
            #print("this is X WITH set_tick nonzero: ",x)
        else:
            tick = larutil.TimeService.GetME().TPCG4Time2Tick(t) + step.X()/(cm_per_tick)
            x  = (tick - trigger_tick)*cm_per_tick
            #print("this is X WITHOUT set_tick nonzero: ",x)

        if no_offset: # plot raw mcstep X position instead of conversion above
            x  = step.X()
        #    steps_np[istep,:] = (step.X(),step.Y(),step.Z())
        #else:
        #    x  = step.X()
        steps.append( [x,step.Y(),step.Z()] )

    if len(steps)==0:
        return None
    
    steps_np = np.array( steps )

    return steps_np

def visualize_larlite_event_mctrack( event_mctrack, origin=None,
                                     do_sce_correction=False,
                                     color_labels=default_pid_colors,
                                     width=3, color_by_origin=False, no_offset=False, set_tick=0 ):
    """
    Produce plotly visualization objects for an entire event's set of mctrack objects.
    
    Parameters
    ----------

    event_mctrack : larlite::event_mctrack or std::vector<larlite::mctrack>
       Container holding larlite::mctrack objects

    origin : int or None
       If integer value given, restrict what we plot to those matching origin flag.
       1: neutrino
       2: cosmics
       0: other
       If none, make plot objects for all entries in the container
       (default is None)

    do_sce_correction : bool
       If True, we apply space-charge corrections to the location of trajectory steps.

    color_labels : dict between integer keys to rgb strings (like `default_pid_colors` defined above)
       You can set up a dictionary to assign colors to different particle types.
       Particles are labeled by the Geant4 PDG codes (the usual HEP standard)

    width : int
       Width of the lines we draw for each track (default: 3)

    color_by_origin : bool
       If true, we instead color by origin flag. (default: False)

    no_offset : bool
       If true, we do not apply to t0 offset to each track that 
       comes from the ionization drfit time and relative time to the event trigger.
       (default: False)

    set_tick : int
       manually set a TPC time tick relative to which we calculate the t0 time of the track.
       if 0, then we determine the tick of each track using the TPC clock info and drift time.
       (default: 0)
    """


    track_vis = []

    print ("number of mctracks in container: ",event_mctrack.size())

    for itrack in range(event_mctrack.size()):
        mctrack = event_mctrack.at(itrack)

        if mctrack.PdgCode()==2112:
            continue #skip neutrons

        if origin is not None and origin!=mctrack.Origin():
            continue


        trackvis = visualize_larlite_mctrack( mctrack, do_sce_correction=do_sce_correction,
                                              color_labels=color_labels,
                                              width=width,
                                              color_by_origin=color_by_origin,
                                              no_offset=no_offset,
                                              set_tick=set_tick)
        if trackvis is not None:
            track_vis.append( trackvis )
    print("number of mctrack plots (zero step plots removed): ",len(track_vis))

    return track_vis

def visualize_larlite_mctrack( mctrack, origin=None,
                                do_sce_correction=False,
                                color_labels=default_pid_colors,
                                width=3, color_by_origin=False, no_offset=False, set_tick=0 ):

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

    if do_sce_correction:
        if tracksce is not None:
            #print("GETTING TO IF STATEMENT 1")
            lltrack = tracksce.applySCE( mctrack )
            npoints = lltrack.NumberTrajectoryPoints()
            steps_np = np.zeros( (npoints,3 ) )
            for ipt in range(npoints):
                for i in range(3):
                    steps_np[ipt,i] = lltrack.LocationAtPoint(ipt)(i)
        else:
            raise ValueError("SCE correction requested, but SCE class not loaded.")
    else:
        #print("GETTING TO ELSE STATEMENT 2")
        steps_np = extract_mctrackpts( mctrack, no_offset=no_offset, set_tick=set_tick )
        if steps_np is None:
            return None

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
