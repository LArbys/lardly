from dash import html
import numpy as np
from .det3d_plot_factory import register_det3d_plotter
import yaml
import os
import ROOT as rt
from larlite import larutil
from math import sqrt
from .t2range import get_t2range_util

def get_treenames_from_yaml():
    return ["EventTree"]

def are_products_present( keys ):

    required_trees = get_treenames_from_yaml()
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('[det3d_ntupletruth_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('ntupletruth: no options')]

def make_traces( tree_dict ):

    iolarlite = tree_dict['iolarlite']
    iolarcv = tree_dict['iolarcv']
    recoTree = tree_dict['recoTree']
    eventTree = tree_dict['eventTree']
    
    print("call det3d_ntupletruth_plot.make_traces")
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5
    
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

    ntrueparts = eventTree.nTrueSimParts

    # line segment plots for each true particle
    plots = []
    
    for ipart in range(ntrueparts):
        px = eventTree.trueSimPartPx[ipart]
        py = eventTree.trueSimPartPy[ipart]
        pz = eventTree.trueSimPartPz[ipart]
        p2 = px*px + py*py + pz*pz
        pnorm = sqrt(p2)
        E  = eventTree.trueSimPartE[ipart]
        m = sqrt(max(E*E-p2,0.0))
        KE = E-m
        pdg = eventTree.trueSimPartPDG[ipart]
        tid = abs(eventTree.trueSimPartTID[ipart])
        mid = abs(eventTree.trueSimPartMID[ipart])
        abspdg = abs(pdg)
        process = eventTree.trueSimPartProcess[ipart]
        if process==0:
            sprocess="primary"
        elif process==1:
            sprocess="from-decay"
        else:
            sprocess="other"
        contained = "contained"
        if eventTree.trueSimPartContained[ipart]==0:
            contained = "uncontained"

        if abspdg in [13,211]:
            cmrange = get_t2range_util().get_range_muon( KE )
        elif abspdg in [11,22]:
            cmrange = 20.0
        else:
            cmrange = get_t2range_util().get_range_proton( KE )
        #print(" truesimpart[",ipart,"] tid=",tid," pdg=",pdg," E=",E," p=",pnorm," m=",m," KE=",KE," cmrange=",cmrange)

        dirx = px/pnorm
        diry = py/pnorm
        dirz = pz/pnorm

        segpts = np.zeros( (2,3) )
        offset = 5.0
        if pdg != 22:
            segpts[0,0] = eventTree.trueSimPartX[ipart]+offset
            segpts[0,1] = eventTree.trueSimPartY[ipart]+offset
            segpts[0,2] = eventTree.trueSimPartZ[ipart]+offset
        else:
            segpts[0,0] = eventTree.trueSimPartEDepX[ipart]+offset
            segpts[0,1] = eventTree.trueSimPartEDepY[ipart]+offset
            segpts[0,2] = eventTree.trueSimPartEDepZ[ipart]+offset
            
        segpts[1,0] = segpts[0,0] + cmrange*dirx
        segpts[1,1] = segpts[0,1] + cmrange*diry
        segpts[1,2] = segpts[0,2] + cmrange*dirz

        rcolor = np.random.randint(0,255,3)
        srgb='rgba(%d,%d,%d,1.0)'%(rcolor[0],rcolor[1],rcolor[2])

        hovertext=f"""
<b>MC Sim Particle</b><br>
<b>TID</b>: {tid}<br>
<b>PDG</b>: {pdg}<br>
<b>MID</b>: {mid}<br>
<b>4-mom MeV</b>: {E:.1f} ({px:.1f},{py:.1f},{pz:.1f})<br>
<b>process</b>: {sprocess}<br>
<b>{contained}</b> <br>
<b>start: ({segpts[0,0]:.1f}, {segpts[0,1]:.1f}, {segpts[0,2]:.1f})<br>
"""
        # if photon, maybe write origin point and MeV deposited point.
        style = "dash"
        if abspdg in [22,11]:
            style = "dot"

        trace = {
            "type":"scatter3d",
            "x": segpts[:,0],
            "y": segpts[:,1],
            "z": segpts[:,2],
            "hovertext":hovertext,
            "mode":"lines",
            "name":f'tid[{tid}]\n pdg[{pdg}]',
            "line":{"color":srgb,"width":5, "dash":style}
        }

        plots.append(trace)
            
    return plots

register_det3d_plotter("ntupletruth",are_products_present,make_plot_option_widgets,make_traces)




