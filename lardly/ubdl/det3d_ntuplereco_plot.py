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
            print('[det3d_ntuplereco_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('ntuplereco: no options')]

def make_traces( tree_dict ):

    eventTree = tree_dict['eventTree']
    
    print("call det3d_ntuplereco_plot.make_traces")
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5
    
    traces = []
    colors = {13:'rgba(51,102,255)',#muon-like
              2212:'rgba(255,0,0)',#proton-like
              212:'rgba(153,51,102)',#pion-like
              11:'rgba(0,255,255)',# electron-like
              22:'rgba(255,0,255)',# gamma-like
              }
    typenames = {13:"muon",
                 2212:"proton",
                 212:"pion",
                 11:"electron",
                 22:"gamma"}

    ntracks = max(eventTree.nTracks,0)
    print("[det3d_ntuplereco_plot] ntracks=",ntracks)

    # line segment plots for each true particle
    plots = []
    
    for i in range(ntracks):

        segpts = np.zeros( (2,3) )
        segpts[0,0] = eventTree.trackStartPosX[i]
        segpts[0,1] = eventTree.trackStartPosY[i]
        segpts[0,2] = eventTree.trackStartPosZ[i]        
        segpts[1,0] = eventTree.trackEndPosX[i]
        segpts[1,1] = eventTree.trackEndPosY[i]
        segpts[1,2] = eventTree.trackEndPosZ[i]
        
        trackclassified = eventTree.trackClassified[i]
        pid     = eventTree.trackPID[i]
        elscore = eventTree.trackElScore[i]
        phscore = eventTree.trackPhScore[i]
        muscore = eventTree.trackMuScore[i]
        piscore = eventTree.trackPiScore[i]
        prscore = eventTree.trackPrScore[i]
        comp    = eventTree.trackComp[i]
        pure    = eventTree.trackPurity[i]
        process = eventTree.trackProcess[i]
        prim    = eventTree.trackPrimaryScore[i]
        fromneu = eventTree.trackFromNeutralScore[i]
        fromchg = eventTree.trackFromChargedScore[i]
        recoE   = eventTree.trackRecoE[i]
        nbelow  = eventTree.trackNPlanesAbove[i]

        if pid in colors:
            color = colors[pid]
            typename  = typenames[pid]
        else:
            color = 'rgba(0,0,0,0)'
            typename = 'other'
        
        hovertext=f"""
<b>RecoTrack[{i}]</b><br>
<b>pdg</b>: {pid} {typename}<br>
<b>larpid (e,g,mu,p,pi)</b>: ({elscore:.2f},{phscore:.2f},{muscore:.2f},{prscore:.2f},{piscore:.2f})<br>
<b>nplanes below</b>: {nbelow}<br>
<b>completeness</b>: {comp:.2f}<br>
<b>purity</b>: {pure:.2f}<br>
<b>primary</b>: {prim}<br>
<b>process</b>: {process}<br>
<b>from neutral</b>: {fromneu:.2f}<br>
<b>from charged</b>: {fromchg:.2f}<br>
<b>Reco E: {recoE:.1f} MeV<br>
"""
        trace = {
            "type":"scatter3d",
            "x": segpts[:,0],
            "y": segpts[:,1],
            "z": segpts[:,2],
            "hovertext":hovertext,
            "mode":"lines",
            "name":f'track[i]',
            "line":{"color":color,"width":5}
        }

        plots.append(trace)

    nshowers = max(eventTree.nShowers,0)
    print("[det3d_ntuplereco_plot] nshowers=",nshowers)
    showerlen = 20.0
    
    for i in range(nshowers):

        segpts = np.zeros( (2,3) )
        segpts[0,0] = eventTree.showerStartPosX[i]
        segpts[0,1] = eventTree.showerStartPosY[i]
        segpts[0,2] = eventTree.showerStartPosZ[i]        
        segpts[1,0] = segpts[0,0] + eventTree.showerStartDirX[i]*20.0
        segpts[1,1] = segpts[0,1] + eventTree.showerStartDirY[i]*20.0
        segpts[1,2] = segpts[0,2] + eventTree.showerStartDirZ[i]*20.0
        
        showerclassified = eventTree.showerClassified[i]
        pid     = eventTree.showerPID[i]
        elscore = eventTree.showerElScore[i]
        phscore = eventTree.showerPhScore[i]
        muscore = eventTree.showerMuScore[i]
        piscore = eventTree.showerPiScore[i]
        prscore = eventTree.showerPrScore[i]
        comp    = eventTree.showerComp[i]
        pure    = eventTree.showerPurity[i]
        process = eventTree.showerProcess[i]
        prim    = eventTree.showerPrimaryScore[i]
        fromneu = eventTree.showerFromNeutralScore[i]
        fromchg = eventTree.showerFromChargedScore[i]
        recoE   = eventTree.showerRecoE[i]
        nbelow  = eventTree.showerNPlanesAbove[i]

        if pid in colors:
            color = colors[pid]
            typename  = typenames[pid]
        else:
            color = 'rgba(0,0,0,0)'
            typename = 'other'
        
        hovertext=f"""
<b>RecoShower[{i}]</b><br>
<b>pdg</b>: {pid} {typename}<br>
<b>larpid (e,g,mu,p,pi)</b>: ({elscore:.2f},{phscore:.2f},{muscore:.2f},{prscore:.2f},{piscore:.2f})<br>
<b>nplanes below</b>: {nbelow}<br>
<b>completeness</b>: {comp:.2f}<br>
<b>purity</b>: {pure:.2f}<br>
<b>primary</b>: {prim}<br>
<b>process</b>: {process}<br>
<b>from neutral</b>: {fromneu:.2f}<br>
<b>from charged</b>: {fromchg:.2f}<br>
<b>Reco E: {recoE:.1f} MeV<br>
"""
        trace = {
            "type":"scatter3d",
            "x": segpts[:,0],
            "y": segpts[:,1],
            "z": segpts[:,2],
            "hovertext":hovertext,
            "mode":"lines",
            "name":f'shower[i]',
            "line":{"color":color,"width":3}
        }

        plots.append(trace)
        
    return plots

register_det3d_plotter("ntuplereco",are_products_present,make_plot_option_widgets,make_traces)




