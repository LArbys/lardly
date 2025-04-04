from dash import html
import numpy as np
from .det3d_plot_factory import register_det3d_plotter
import yaml
import os

INTIME_TREE_NAME = "larmatch"

def get_larmatchhits_treename_from_yaml():
    global INTIME_TREE_NAME
    print("config file exists: ",os.path.exists("dlviewer.cfg"))
    with open('dlviewer.cfg') as f:
        cfg = yaml.safe_load(f.read())
        config_key = 'larmatchhits_tree_name'
        print(cfg)
        if config_key in cfg:
            treename = cfg[config_key]
            print(f"getting '{configkey}' from config file: {treename}")
            INTIME_TREE_NAME = treename[len("opflash_"):-len("_tree")]
            return [cfg[config_key]]
    
    return ["larflow3dhit_larmatch_tree"]

def are_products_present( keys ):

    required_trees = get_larmatchhits_treename_from_yaml()
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('[det3d_larmatchhits_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('larmatchhits: no options')]

def make_traces( iolarlite, iolarcv, recoTree ):
    print("call det3d_larmatchhits_plot.make_traces")
    
    ev_hits = iolarlite.get_data("larflow3dhit",INTIME_TREE_NAME)
    print("  num larmatch hits (in ",INTIME_TREE_NAME,"): ",ev_hits.size())

    if ev_hits.size()==0:
        return []
    
    hitinfo = np.zeros( (ev_hits.size(),4) )
    customdata = np.zeros( (ev_hits.size(),4) )
    for ihit in range(ev_hits.size()):
        hit = ev_hits.at(ihit)
        hitinfo[ihit,0] = hit[0]
        hitinfo[ihit,1] = hit[1]
        hitinfo[ihit,2] = hit[2]
        hitinfo[ihit,3] = hit.track_score # this is larmatch score -- abuse of class
        customdata[ihit,0] = hit.targetwire[0]
        customdata[ihit,1] = hit.targetwire[1]
        customdata[ihit,2] = hit.targetwire[2]
        customdata[ihit,3] = hit.tick
    hovertemplate="""
    <b>x</b>: %{x}<br>
    <b>y</b>: %{y}<br>
    <b>z</b>: %{z}<br>
    <b>tick</b>: %{customdata[3]}<br>
    <b>U</b>: %{customdata[0]}<br>
    <b>V</b>: %{customdata[1]}<br>
    <b>Y</b>: %{customdata[2]}<br>
    """
        
    larflowhits = {
        "type":"scatter3d",
        "x": hitinfo[:,0],
        "y": hitinfo[:,1],
        "z": hitinfo[:,2],
        "mode":"markers",
        "name":"larmatch",
        "hovertemplate":hovertemplate,
        "customdata":customdata,
        "marker":{"color":hitinfo[:,3],"size":1,"opacity":0.8,"colorscale":'Viridis',"cmax":1.0,"cmin":0.0},
    }

    return [larflowhits]

register_det3d_plotter("larmatchhits",are_products_present,make_plot_option_widgets,make_traces)




