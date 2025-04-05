from dash import html
import numpy as np
from .det3d_plot_factory import register_det3d_plotter
import yaml
import os
from larlite import larutil

BOUNDARY_COSMIC_TREE_NAME = "boundarycosmicnoshift"
CONTAINED_COSMIC_TREE_NAME = "containedcosmic"

def get_treenames_from_yaml():
    global BOUNDARY_COSMIC_TREE_NAME
    global CONTAINED_COSMIC_TREE_NAME
    return ["KPSRecoManagerTree"]

def are_products_present( keys ):

    required_trees = get_treenames_from_yaml()
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('[det3d_cosmictracks_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('keypoints: no options')]

def make_traces( iolarlite, iolarcv, recoTree ):
    print("call det3d_keypoints_plot.make_traces")
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5
    
    kptrack  = recoTree.kpc_track_v
    kpshower = recoTree.kpc_shower_v
    kpcosmic = recoTree.kpc_cosmic_v
    kpnu     = recoTree.kpc_nu_v
    
    print("  num in-time track keypoints: ",kptrack.size())
    print("  num shower keypoints: ",kpshower.size())
    print("  num cosmic (track) keypoints: ",kpcosmic.size())
    print("  num nu candidate keypoints: ",kpnu.size())

    traces = []
    ntracks = 0
    colors = ['rgb(255,128,128)', # shower
              'rgb(51,102,255)', # track
              'rgb(102,102,153)',# cosmic
              'rgb(50,50,50)'] # nu
    typenames = {0:"0:nu",
                 1:"1:trackstart",
                 2:"2:trackend",
                 3:"3:shower",
                 4:"4:michel",
                 5:"5:delta"}
    names = ["shower","track","cosmic","nu"]
    sizes = [3,3,2,4]
    hovertemplate="""
    <b>type</b>: %{customdata[6]:.0f}<br>
    <b>score</b>: %{customdata[5]:.2f}<br>
    <b>x</b>: %{x:.1f}<br>
    <b>y</b>: %{y:.1f}<br>
    <b>z</b>: %{z:.1f}<br>
    <b>t</b>: %{customdata[0]:.1f} usec<br>
    <b>tick</b>: %{customdata[1]:.0f}<br>
    <b>U</b>: %{customdata[2]:.0f}<br>
    <b>V</b>: %{customdata[3]:.0f}<br>
    <b>Y</b>: %{customdata[4]:.0f}<br>
    """
    
    for itype,ev_container in enumerate([kpshower,kptrack,kpcosmic,kpnu]):
        nkpts = ev_container.size()
        hitpos = np.zeros( (nkpts,3) )
        customdata = np.zeros( (nkpts,7) ) 
        for ipt in range(nkpts):
            kp = ev_container.at(ipt)
            for v in range(3):
                hitpos[ipt,v] = kp.max_pt_v.at(v)
            x = kp.max_pt_v.at(v)
            tick = 3200 + x/cm_per_tick
            t = x/cm_per_tick*0.5
            customdata[ipt,0] = t
            customdata[ipt,1] = tick
            for p in range(3):
                customdata[ipt,2+p] = larutil.Geometry.GetME().WireCoordinate( kp.max_pt_v, p )
            customdata[ipt,6] = kp._cluster_type
            customdata[ipt,5] = kp.max_score
                                
        trace = {
            "type":"scatter3d",
            "x": hitpos[:,0],
            "y": hitpos[:,1],
            "z": hitpos[:,2],
            "mode":"markers",
            "name":names[itype],
            "hovertemplate":hovertemplate,
            "customdata":customdata,
            "marker":{"color":colors[itype],"size":sizes[itype],"opacity":0.5},
        }
        traces.append(trace)

            
    return traces

register_det3d_plotter("keypoints",are_products_present,make_plot_option_widgets,make_traces)




