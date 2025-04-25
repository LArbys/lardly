from dash import html
from .det3d_plot_factory import register_det3d_plotter
from lardly.data.larlite_opflash import visualize_larlite_opflash_3d, visualize_empty_opflash
import yaml
import os

INTIME_TREE_NAME = "simpleFlashBeam"

def get_opflash_treename_from_yaml():
    global INTIME_TREE_NAME
    if os.path.exists("dlviewer.cfg"):
        print("config file exists: ",os.path.exists("dlviewer.cfg"))
        with open('dlviewer.cfg') as f:
            cfg = yaml.safe_load(f.read())
            print(cfg)
            if 'intime_tree_name' in cfg:
                treename = cfg['intime_tree_name']
                print("getting 'intime_tree_name' from config file: ",treename)
                INTIME_TREE_NAME = treename[len("opflash_"):-len("_tree")]
                return [cfg['intime_tree_name']]
    else:
        pass
    return ["opflash_simpleFlashBeam_tree"]

def are_products_present( keys ):

    required_trees = get_opflash_treename_from_yaml()
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('[det3d_intimeflash_plot.py] failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('IntimeFlash: no options')]

def make_traces( tree_dict ):

    iolarlite = tree_dict['iolarlite']
    
    print("call det3d_intimeflash_plot.make_traces")
    ev_flash = iolarlite.get_data("opflash",INTIME_TREE_NAME)
    print("  num in-time flash objects (in ",INTIME_TREE_NAME,"): ",ev_flash.size())

    traces = []
    nintime = 0
    passed_start = False
    passed_end = False
    if ev_flash.size()>0:
        print("  flashes: ")
        for iflash in range(ev_flash.size()):
            flash = ev_flash.at(iflash)
            
            t = flash.Time()
            
            if t>2.94 and not passed_start:
                print("   [ in-time window start: ",2.94," usec ]")
                passed_start = True
            print("    opflash[",iflash,"] time=",t," usec")
            if t>4.86 and not passed_end:
                print("   [ in-time window end: ",4.86," usec ]")
                passed_end = True
                
            if flash.Time()>2.94 and flash.Time()<4.86:
                flash_trace_v = visualize_larlite_opflash_3d( flash )
                traces += flash_trace_v
                nintime += 1
    print("  num intime flashes: ",nintime)
    if nintime==0:
        empty_flash_v = visualize_empty_opflash()
        traces += empty_flash_v
        
        
    print("  number of intime flash traces: ",len(traces))
    return traces

register_det3d_plotter("IntimeFlash",are_products_present,make_plot_option_widgets,make_traces)




