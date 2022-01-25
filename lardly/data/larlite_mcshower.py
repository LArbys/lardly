from __future__ import print_function
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

def visualize3d_larlite_mcshower( larlite_mcshower,
                                  return_origtraj=False,
                                  return_dirplot=False,                                  
                                  return_detprofile=True,
                                  fixed_cone_len_cm=20.0,
                                  origin=None ):
    shr = larlite_mcshower
    shr_start = [shr.Start().X(), shr.Start().Y(), shr.Start().Z(), shr.Start().T()]
    shr_end = [shr.End().X(), shr.End().Y(), shr.End().Z() , shr.End().T()]
    shr_dir = [shr.StartDir().X() , shr.StartDir().Y(), shr.StartDir().Z()]
    shr_start_convert = convert_mc_showerpoint(shr_start)
    shr_end_convert = convert_mc_showerpoint(shr_end)

    if origin is not None and shr.Origin()!=origin:
        # skipping this shower
        return [None,None,None]

    # define cone length
    if fixed_cone_len_cm is None:
        shrlen = 0.0
        for i in range(3):
            shrlen += pow(shr_start_convert[i]-shr_end_convert[i],2)
        shrlen = pow(shrlen,0.5)
    else:
        shrlen = fixed_cone_len_cm

    if ( (return_origtraj is False)
         or ((shr_start_convert[0] < -10) or (shr_start_convert[0] > 266)
             or (shr_start_convert[1] < -125) or (shr_start_convert[1] > 125)
             or (shr_start_convert[2] < -50) or (shr_start_convert[2] > 1100)) ):
        # out of bounds
        shower_trace = None
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


    # visualize shower direction
    dirpts = np.zeros( (3,2) )
    for i in range(3):
        dirpts[i,0] = shr_start[i]
        dirpts[i,1] = shr_start[i] + 20.0*shr_dir[i]

    if return_dirplot:
        shower_dir_trace = {
            "type":"scatter3d",
            "x":dirpts[0,:],
            "y":dirpts[1,:],
            "z":dirpts[2,:],
            "mode":"lines",
            "name":"showerdir",
            "line":{"color":"rgb(125,125,125)","width":2}
        }
    else:
        shower_dir_trace = None

    # profile start and direction
    profpts = np.zeros( (3,2) )
    profmom = shr.DetProfile().Momentum().Vect()
    momvec=(profmom[0],profmom[1],profmom[2])
    if momvec==(0.,0.,0.) or return_detprofile is False:
        shower_prof_trace = None
    else:
        #print("def prof vtx: ",[shr.DetProfile().Position()[i] for i in range(3)])
        #print("det prof mom: ",(profmom[0],profmom[1],profmom[2])," mag=",profmom.Mag())
        for i in range(3):
            profpts[i,0] = shr.DetProfile().Position()[i]
            profpts[i,1] = shr.DetProfile().Position()[i] + 50.0*profmom[i]/profmom.Mag()

        profcolor = 'rgb(255,0,125)' if shr.PdgCode()==22 else 'rgb(255,0,255)'
        
        shower_prof_trace = {
            "type":"scatter3d",
            "x":profpts[0,:],
            "y":profpts[1,:],
            "z":profpts[2,:],
            "mode":"lines",
            "name":"sprof[%d,%d,%d]"%(shr.PdgCode(),shr.TrackID(),shr.Origin()),
            "line":{"color":profcolor,"width":4}
        }

    return [shower_trace,shower_dir_trace,shower_prof_trace]

def visualize_larlite_event_mcshower( ev_mcshower,
                                      return_dirplot=False,
                                      return_origtraj=False,
                                      return_detprofile=True,
                                      origin=None ):
    traces_v = []

    for i in range(ev_mcshower.size()):
        shr_v = visualize3d_larlite_mcshower( ev_mcshower.at(i),
                                              return_origtraj=return_origtraj,
                                              return_detprofile=return_detprofile,
                                              return_dirplot=return_dirplot,
                                              origin=origin )
        for x in shr_v:
            if x is not None:
                traces_v.append(x)

    return traces_v
