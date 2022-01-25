import os,sys

from larlite import larlite
from .larlite_mctrack import visualize_larlite_event_mctrack
from .larlite_mcshower import visualize_larlite_event_mcshower

def visualize_nu_interaction( io, do_sce_correction=False ):
    """
    Takes larlite::storage_manager and gets info needed to plot neutrino interaction
    """
    # get traces for tracks
    traces_v =   visualize_larlite_event_mctrack( io.get_data(larlite.data.kMCTrack, "mcreco"),
                                                  origin=1,
                                                  do_sce_correction=do_sce_correction)

    # get traces for shower
    mcshower_v = visualize_larlite_event_mcshower( io.get_data(larlite.data.kMCShower, "mcreco"),
                                                   return_dirplot=False )
    traces_v += mcshower_v

    # make vertex
    try:
        from ublarcvapp import ublarcvapp
        vtxgetter = ublarcvapp.mctools.NeutrinoVertex()
        vtxpos = vtxgetter.getPos3DwSCE( io )

        vtxtrace = {
            "type":"scatter3d",
            "x":[vtxpos[0]],
            "y":[vtxpos[1]],
            "z":[vtxpos[2]],
            "mode":"markers",
            "name":"TrueNuVtx",
            "marker":{"color":"rgb(125,125,125)","size":5},
        }
        traces_v.append( vtxtrace )
    except:
        pass

    return traces_v
        

