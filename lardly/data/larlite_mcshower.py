import numpy as np

def convert_mc_showerpoint( mcshower_pt, sce=None ):
    from larlite import larlite, larutil
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5

    # convert mcshower points to image pixels

    t = mcshower_pt[3]

    tick = larutil.TimeService.GetME().TPCG4Time2Tick(t) + mcshower_pt[0]/(cm_per_tick)
    x  = (tick - 3200)*cm_per_tick

    convert_pt = [x,mcshower_pt[1],mcshower_pt[2]]
    return convert_pt

import os,sys

def visualize3d_larlite_mcshower( larlite_mcshower, return_dirplot=False, fixed_cone_len_cm=20.0, origin=None ):
    shr = larlite_mcshower
    shr_start = [shr.Start().X(), shr.Start().Y(), shr.Start().Z(), shr.Start().T()]
    shr_end = [shr.End().X(), shr.End().Y(), shr.End().Z() , shr.End().T()]
    shr_dir = [shr.StartDir().X() , shr.StartDir().Y(), shr.StartDir().Z()]
    shr_start_convert = convert_mc_showerpoint(shr_start)
    shr_end_convert = convert_mc_showerpoint(shr_end)

    if origin is not None and shr.Origin()!=origin:
        return []

    if fixed_cone_len_cm is None:
        shrlen = pow(pow(shr_start_convert[0]-shr_end_convert[0],2) + pow(shr_start_convert[1]-shr_end_convert[1],2) + pow(shr_start_convert[2]-shr_end_convert[2],2),.5)
    else:
        shrlen = fixed_cone_len_cm

    if ((shr_start_convert[0] < -10) or (shr_start_convert[0] > 266) or (shr_start_convert[1] < -125) or (shr_start_convert[1] > 125) or (shr_start_convert[2] < -50) or (shr_start_convert[2] > 1100)):
        shower_trace = {
            "type":"cone",
            "x":[0],
            "y":[0],
            "z":[0],
            "u":[0],
            "v":[0],
            "w":[0],
            "anchor":"tip",
            "sizemode":"absolute",
            "opacity":0.1,
            "sizeref":(int)(0*2),
            }

    else:
        shower_trace = {
            "type":"cone",
            "x":[shr_start_convert[0]],
            "y":[shr_start_convert[1]],
            "z":[shr_start_convert[2]],
            "u":[-shrlen*shr_dir[0]],
            "v":[-shrlen*shr_dir[1]],
            "w":[-shrlen*shr_dir[2]],
            "anchor":"tip",
            "sizemode":"absolute",
            "opacity":0.1,
            "sizeref":(int)(shrlen*2),
            }

    if not return_dirplot:
        return [shower_trace]

    # add shower direction
    dirpts = np.zeros( (3,2) )
    for i in xrange(3):
        dirpts[i,0] = shr_start[i]
        dirpts[i,1] = shr_start[i] + 20.0*shr_dir[i]
        
    shower_dir_trace = {
        "type":"scatter3d",
        "x":dirpts[0,:],
        "y":dirpts[1,:],
        "z":dirpts[2,:],
        "mode":"lines",
        "name":"showerdir",
        "line":{"color":"rgb(125,125,125,)","width":2}
    }

    # profile start and direction
    profpts = np.zeros( (3,2) )
    profmom = shr.DetProfile().Momentum().Vect()
    momvec=(profmom[0],profmom[1],profmom[2])
    if momvec==(0.,0.,0.):
        print "empty det prof mom, return with profile trace"
        return [shower_trace,shower_dir_trace]
    
    #print "def prof vtx: ",[shr.DetProfile().Position()[i] for i in xrange(3)]
    #print "det prof mom: ",(profmom[0],profmom[1],profmom[2])," mag=",profmom.Mag()
    for i in xrange(3):
        profpts[i,0] = shr.DetProfile().Position()[i]
        profpts[i,1] = shr.DetProfile().Position()[i] + 50.0*profmom[i]/profmom.Mag()
        
    shower_prof_trace = {
        "type":"scatter3d",
        "x":profpts[0,:],
        "y":profpts[1,:],
        "z":profpts[2,:],
        "mode":"lines",
        "name":"sprof[%d,%d,%d]"%(shr.PdgCode(),shr.TrackID(),shr.Origin()),
        "line":{"color":"rgb(255,0,255,)","width":4}
    }
    
    
    return [shower_trace,shower_dir_trace,shower_prof_trace]

def visualize_larlite_event_mcshower( ev_mcshower, return_dirplot=False, origin=None ):
    traces_v = []

    for i in range(ev_mcshower.size()):
        shr_v = visualize3d_larlite_mcshower( ev_mcshower.at(i), return_dirplot, origin=origin )
        traces_v += shr_v

    return traces_v
