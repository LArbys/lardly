import os,sys
from .det3d_plot_factory import register_det3d_plotter
from dash import html
import numpy as np
import lardly.data.larlite_mctrack as vis_mctrack
import lardly.data.larlite_mcshower as vis_mcshower
from ublarcvapp import ublarcvapp
from larlite import larlite, larutil

def are_products_present( keys ):
    required_trees = ["KPSRecoManagerTree"]
    hastrees = True
    print("reconu check: ",keys)
    for treename in required_trees:
        if treename not in keys:
            print('failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('RecoNu: no options')]

def make_traces( tree_dict, option_widget ):

    recoTree = tree_dict['recoTree']
    
    nvertices = recoTree.nuvetoed_v.size()
    nselvars  = recoTree.nu_sel_v.size();
    print("[det3d_reconu_plot.py] num vertices: ",nvertices, " num selection var classes: ",nselvars)
    traces = []

    # arrays for nu-vertex plot
    # [0-3] x, y, z, tick,
    # [4-7] t, U, V, Y,
    # [8-9] n_primary tracks, n_primary showers,
    # [10-13] max-kp-score, nu-score, origin kptype, ivtx
    # [14-18] (optional) unreco fracion: U pix, V pix, Y pix, all spacepoints
    if nvertices>0:
        vtxinfo = np.zeros( (nvertices, 18 ) )
    else:
        vtxinfo = None
    for ivtx in range(nvertices):
        nuvtx = recoTree.nuvetoed_v.at(ivtx)
        if nvertices==nselvars:
            nusel = recoTree.nu_sel_v.at(ivtx)
        else:
            nusel = None
            
        print("RecoNu Vertex[",ivtx,"]")
        print("  ntracks=",nuvtx.track_v.size())
        print("  nshowers=",nuvtx.shower_v.size())
        
        nshowers = nuvtx.shower_v.size()
        for ishower in range(nshowers):
            shower = nuvtx.shower_v.at(ishower) # a larlite::larflowcluster object
            npts = shower.size()
            ptpos = np.zeros((npts,3))
            for i in range(npts):
                for v in range(3):
                    ptpos[i,v] = shower.at(i)[v]
            ic = np.random.randint(0,255,3)
            rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
            shower_trace = {
                "type":"scatter3d",
                "x":ptpos[:,0],
                "y":ptpos[:,1],
                "z":ptpos[:,2],
                "mode":"markers",
                "name":f"Nu[{ivtx}]-S[{ishower}]",
                "marker":{"color":rcolor,"size":1.0,"opacity":0.5},
                #"customdata":meta,
                #"hovertemplate":hovertemplate
            }
            traces.append(shower_trace)

        ntracks = nuvtx.track_v.size()
        for itrack in range(ntracks):
            track = nuvtx.track_v.at(itrack)
            trackhits = nuvtx.track_hitcluster_v.at(itrack)
            npts = trackhits.size()
            ptpos = np.zeros((npts,3))
            for i in range(npts):
                for v in range(3):
                    ptpos[i,v] = trackhits.at(i)[v]
            ic = np.random.randint(0,255,3)
            rcolor = f'rgba({ic[0]},{ic[1]},{ic[2]},1.0)'
            trackhit_trace = {
                "type":"scatter3d",
                "x":ptpos[:,0],
                "y":ptpos[:,1],
                "z":ptpos[:,2],
                "mode":"markers",
                "name":f"Nu[{ivtx}]-T[{itrack}]",
                "marker":{"color":rcolor,"size":1.0,"opacity":0.5},
                #"customdata":meta,
                #"hovertemplate":hovertemplate
            }
            traces.append(trackhit_trace)

        # gather data for nu vertex hover text
        vtxinfo[ivtx,0] = nuvtx.pos[0]
        vtxinfo[ivtx,1] = nuvtx.pos[1]
        vtxinfo[ivtx,2] = nuvtx.pos[2]
        vtxinfo[ivtx,3] = (nuvtx.tick-3200)*0.5 # t in usec relative to trigger
        vtxinfo[ivtx,4] = nuvtx.tick
        vtxinfo[ivtx,5] = nuvtx.col_v[0] # u-plane wire
        vtxinfo[ivtx,6] = nuvtx.col_v[1] # v-plane wire
        vtxinfo[ivtx,7] = nuvtx.col_v[2] # y-plane wire
        nprim_tracks = 0
        nprim_showers = 0
        for itrack in range(nuvtx.track_v.size()):
            if itrack < nuvtx.track_isSecondary_v.size() and nuvtx.track_isSecondary_v.at(itrack)==0:
                nprim_tracks += 1
            else if nuvtx.track_isSecondary_v.size()==0:
                nprim_tracks += 1
        for ishower in range(nuvtx.shower_v.size()):
            if ishower < nuvtx.shower_isSecondary_v.size() and nuvtx.shower_isSecondary_v.at(ishower)==0:
                nprim_showers += 1.0
            else if nuvtx.shower_isSecondary_v.size()==0:
                nprim_showers += 1
                
        vtxinfo[ivtx,8] = nprim_tracks
        vtxinfo[ivtx,9] = nprim_showers
        vtxinfo[ivtx,10] = nuvtx.netScore
        vtxinfo[ivtx,11] = nuvtx.netNuScore
        vtxinfo[ivtx,12] = nuvtx.keypoint_type
        vtxinfo[ivtx,13] = ivtx
        if nusel is not None:
            try:
                for j in range(nusel.unreco_fraction_v.size()):
                    vtxinfo[ivtx,14+j] = nusel.unreco_fraction_v[j]
            except:
                pass

    nu_hover_template = """
    <b>x</b>: %{x:.1f}<br>
    <b>y</b>: %{y:.1f}<br>
    <b>z</b>: %{z:.1f}<br>
    <b>NuCand</b>: %{customdata[10]}<br>
    <b>t</b>: %{customdata[0]:.1f} usec<br>
    <b>tick</b>: %{customdata[1]:.0f}<br>
    <b>U</b>: %{customdata[2]:.0f}<br>
    <b>V</b>: %{customdata[3]:.0f}<br>
    <b>Y</b>: %{customdata[4]:.0f}<br>
    <b>nprim tracks</b>: %{customdata[5]:.0f}<br>
    <b>nprim showers</b>: %{customdata[6]:.0f}<br>
    <b>max-kp score</b>: %{customdata[7]:.2f}<br>
    <b>nu-kp score</b>: %{customdata[8]:.2f}<br>
    <b>kp type</b>: %{customdata[9]:.0f}<br>
    """
    if nvertices>0:

        if nvertices==nselvars:
            this_template = "%s"%(nu_hover_template)
            this_template += "<b>unreco frac</b> %{customdata[11]:.2f} %{customdata[12]:.2f} %{customdata[13]:.2f} %{customdata[14]:.2f}<br>"
        else:
            this_template = nu_hover_template
        
        nu_trace = {
            "type":"scatter3d",
            "x": vtxinfo[:,0],
            "y": vtxinfo[:,1],
            "z": vtxinfo[:,2],
            "mode":"markers",
            "name":"recoNu",
            "hovertemplate":this_template,
            "customdata":vtxinfo[:,3:],
            "marker":{"color":'rgb(255,0,0)',"size":5,"opacity":0.3},
        }
        traces.append( nu_trace )        

    return traces

register_det3d_plotter("RecoNu",are_products_present,make_plot_option_widgets,make_traces)
