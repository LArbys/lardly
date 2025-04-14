from __future__ import print_function
import numpy as np
import ROOT as rt
from larlite import larlite
from math import sqrt,log

try:
    from ublarcvapp import ublarcvapp
    tracksce = ublarcvapp.mctools.TruthTrackSCE()
except:
    tracksce = None

# define the default colors for particles
from .default_pid_colors import default_pid_colors, get_pid_color

shower_eps = 550.0/18.0 # 550 MeV/Z from Ugo_Amaldi_1981_Phys._Scr._23_012

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
                                  return_origtraj_cone=False,
                                  return_dirplot=False,                                  
                                  return_detprofile=True,
                                  fixed_cone_len_cm=14.0, # radiation length
                                  no_offset=True,
                                  apply_sce=True,
                                  exclude_out_of_bounds=True,
                                  origin=None ):
    shr = larlite_mcshower

    if origin is not None and shr.Origin()!=origin:
        # apply cut on origin of shower
        return [None,None,None]

    # meta data we will use for hover text
    meta = [
        [int(shr.PdgCode()),int(shr.Origin()),float(shr.Start().E())],
        [int(shr.PdgCode()),int(shr.Origin()),float(shr.Start().E())]
    ]
    print(meta)
    hovertemplate="""
        x:%{x:.2f}<br>
        y:%{y:.2f}<br>
        z:%{z:.2f}<br>
        pdg:%{customdata[0]}<br>
        origin:%{customdata[1]}<br>
        MeV:%{customdata[2]:.2f}
        """

    # draw cone plot
    # first, we create a fake mctrack in order to use some existing tools to apply space-charge effect
    
    # use the particle creation point as the start
    start_x = rt.TLorentzVector( shr.Start().X(), shr.Start().Y(), shr.Start().Z(), shr.Start().T() )

    # get the direction
    shr_dir = [shr.StartDir().X() , shr.StartDir().Y(), shr.StartDir().Z()]
    start_p = rt.TLorentzVector( shr.StartDir().X() , shr.StartDir().Y(), shr.StartDir().Z(), 1.0 ) # fake

    # apply SCE if requested
    if apply_sce:
        shr_track = larlite.mctrack()
        shr_step  = larlite.mcstep( start_x, start_p )
        shr_track.push_back( shr_step )        
        #tracksce.set_verbosity(0)
        if tracksce is not None:
            shr_start_sce = tracksce.applySCE( shr_track )
            #print("start, pre-sce: ",start_x[0],start_x[1],start_x[2])
            shr_start = [ shr_start_sce.LocationAtPoint(0)[i] for i in range(3) ]
            shr_start.append( start_x[-1] ) # add time
            #print("start, post-sce: ",shr_start[0],shr_start[1],shr_start[2])
        else:
            print("warning SCE not loaded, but requested. not applied.")
            shr_start = start_x
    else:
        shr_start = start_x

    if no_offset is False:
        # apply drift time
        shr_start_convert = convert_mc_showerpoint(shr_start)
    else:
        # just plot locatoin
        shr_start_convert = shr_start

    # define cone length
    if fixed_cone_len_cm is None:
        # here we make some crude approximations for energy and length correlation
        # using misreading of Ugo_Amaldi_1981_Phys._Scr._23_012

        Ex = shr.Start().E()/shower_eps
        if Ex>=1:
            shrlen = 3*(log(Ex)+1.2) # this is fake
        else:
            # below critical energy, just go with linear MIP energy loss
            shrlen = shr.Start().E()/2.2
    else:
        shrlen = fixed_cone_len_cm

    if exclude_out_of_bounds:
        shower_end = [ shr_start_convert[i]+5*shrlen*shr_dir[i] for i in range(3) ]
        for loc in [shr_start_convert,shower_end]:
            if loc[0]<-100 or loc[0]>360:
                return None
            if loc[1]<-300 or loc[1]>300:
                return None
            if loc[2]<-100 or loc[2]>1136:
                return None

    # define cone plot
    if ( (return_origtraj_cone is False)
         or ((shr_start_convert[0] < -10) or (shr_start_convert[0] > 266)
             or (shr_start_convert[1] < -125) or (shr_start_convert[1] > 125)
             or (shr_start_convert[2] < -50) or (shr_start_convert[2] > 1100)) ):
        # out of bounds
        #print("shower start out of bounds")
        shower_trace = None
    else:
        shower_trace = {
            "type":"cone",
            "x":[shr_start_convert[0]],
            "y":[shr_start_convert[1]],
            "z":[shr_start_convert[2]],
            "u":[-2*shrlen*shr_dir[0]],
            "v":[-2*shrlen*shr_dir[1]],
            "w":[-2*shrlen*shr_dir[2]],
            "customdata":meta,
            "name":"shower[%d]"%(shr.TrackID()),
            "anchor":"tip",
            "sizemode":"absolute",
            "opacity":0.1,
            "hovertemplate":hovertemplate
            }
        
    # define end as start+dir*critical_length
    shr_end = [ shr_start_convert[i]+shrlen*shr_dir[i] for i in range(3) ]
    shr_end.append( shr_start[-1] )    
    if no_offset:
        shr_end_convert = shr_end
    else:
        shr_end_convert = convert_mc_showerpoint(shr_end)

    # visualize shower direction
    dirpts = np.zeros( (3,2) )
    for i in range(3):
        dirpts[i,0] = shr_start_convert[i]
        dirpts[i,1] = shr_end_convert[i]

    if return_dirplot:
        shower_dir_trace = {
            "type":"scatter3d",
            "x":dirpts[0,:],
            "y":dirpts[1,:],
            "z":dirpts[2,:],
            "mode":"lines",
            "name":"showerdir[%d]"%(shr.TrackID()),
            "customdata":meta,
            "line":{"color":get_pid_color(shr.PdgCode()),"width":2},
            "hovertemplate":hovertemplate,
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
        print("def prof vtx: ",[shr.DetProfile().Position()[i] for i in range(3)])
        print("det prof mom: ",(profmom[0],profmom[1],profmom[2])," mag=",profmom.Mag())
        for i in range(3):
            profpts[i,0] = shr.DetProfile().Position()[i]
            profpts[i,1] = shr.DetProfile().Position()[i] + shrlen*(profmom[i]/profmom.Mag())

        profcolor = 'rgb(0,255,255)' if shr.PdgCode()==22 else 'rgb(0,255,0)'
        
        shower_prof_trace = {
            "type":"scatter3d",
            "x":profpts[0,:],
            "y":profpts[1,:],
            "z":profpts[2,:],
            "mode":"lines",
            "name":"ShowerProfile[%d]"%(shr.TrackID()),
            "line":{"color":profcolor,"width":4},
            "customdata":meta,
            "hovertemplate":hovertemplate
        }

    return [shower_trace,shower_dir_trace,shower_prof_trace]

def visualize_larlite_event_mcshower( ev_mcshower,
                                      no_offset=False,
                                      apply_sce=True,
                                      return_dirplot=False,
                                      return_origtraj_cone=False,
                                      return_detprofile=True,
                                      fixed_cone_len_cm=14.0,
                                      exclude_out_of_bounds=True,                                      
                                      origin=None ):
    traces_v = []

    for i in range(ev_mcshower.size()):
        shr_v = visualize3d_larlite_mcshower( ev_mcshower.at(i),
                                              return_origtraj_cone=return_origtraj_cone,
                                              return_detprofile=return_detprofile,
                                              return_dirplot=return_dirplot,
                                              no_offset=no_offset,
                                              apply_sce=apply_sce,
                                              fixed_cone_len_cm=fixed_cone_len_cm,
                                              exclude_out_of_bounds=exclude_out_of_bounds,
                                              origin=origin )
        if exclude_out_of_bounds and shr_v is None:
            continue
        for x in shr_v:
            if x is not None:
                traces_v.append(x)

    return traces_v

