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

def visualize3d_larlite_mcshower( larlite_mcshower ):
    shr = larlite_mcshower
    shr_start = [shr.Start().X(), shr.Start().Y(), shr.Start().Z(), shr.Start().T()]
    shr_end = [shr.End().X(), shr.End().Y(), shr.End().Z() , shr.End().T()]
    shr_dir = [shr.StartDir().X() , shr.StartDir().Y(), shr.StartDir().Z()]
    shr_start_convert = convert_mc_showerpoint(shr_start)
    shr_end_convert = convert_mc_showerpoint(shr_end)

    shrlen = pow(pow(shr_start_convert[0]-shr_end_convert[0],2) + pow(shr_start_convert[1]-shr_end_convert[1],2) + pow(shr_start_convert[2]-shr_end_convert[2],2),.5)
    shower_trace = 0
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
            "opacity":0.0,
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
            "opacity":0.7,
            "sizeref":(int)(shrlen*2),
            }
    return shower_trace
