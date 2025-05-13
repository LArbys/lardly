from dash import html
from .det3d_plot_factory import register_det3d_plotter
from lardly.data.larlite_opflash import visualize_larlite_opflash_3d, visualize_empty_opflash
import yaml
import os
import numpy as np

INPUT_TREES_PRESENT=[]

def are_products_present( keys ):
    global INPUT_TREES_PRESENT
    hastrees = False
    possible_input_tree_list = ["showergoodhit","trackprojsplit_wcfilter"]
    """
  KEY: TTree	larflowcluster_cosmicproton_tree;1	larflowcluster Tree by cosmicproton
  KEY: TTree	larflowcluster_hip_tree;1	larflowcluster Tree by hip
  KEY: TTree	larflowcluster_showergoodhit_tree;1	larflowcluster Tree by showergoodhit
  KEY: TTree	larflowcluster_showerkp_tree;1	larflowcluster Tree by showerkp
  KEY: TTree	larflowcluster_trackprojsplit_wcfilter_tree;1	larflowcluster Tree by trackprojsplit_wcfilter
    """
    print("check trees for nuinputclusters")
    for treename in possible_input_tree_list:
        lltree = f'larflowcluster_{treename}_tree'
        if lltree in keys:
            hastrees = True
            INPUT_TREES_PRESENT.append( treename )
            print("  recognized: ",lltree)
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('IntimeFlash: no options')]

def make_traces( tree_dict ):

    iolarlite = tree_dict['iolarlite']
    
    print("call det3d_nuinputclusters_plot.make_traces")
    global INPUT_TREES_PRESENT

    hovertemplate="""
    <b>x</b>: %{x}<br>
    <b>y</b>: %{y}<br>
    <b>z</b>: %{z}<br>
    <b>tick</b>: %{customdata[3]}<br>
    <b>U</b>: %{customdata[0]}<br>
    <b>V</b>: %{customdata[1]}<br>
    <b>Y</b>: %{customdata[2]}<br>
    <b>shower</b>: %{customdata[4]:.2f}<br>
    <b>e</b>:  %{customdata[5]:.2f}<br>
    <b>g</b>:  %{customdata[6]:.2f}<br>
    <b>mu</b>: %{customdata[7]:.2f}<br>
    <b>p</b>:  %{customdata[8]:.2f}<br>
    <b>pi</b>: %{customdata[9]:.2f}<br>
    """
    
    
    traces = []    
    for inputtree in INPUT_TREES_PRESENT:        
        ev_cluster = iolarlite.get_data("larflowcluster",inputtree)
        print("  num clusters (in ",inputtree,"): ",ev_cluster.size())

        nclusters = ev_cluster.size()
        for icluster in range(nclusters):
            cluster = ev_cluster.at(icluster)
            npts = cluster.size()
            pos = np.zeros( (npts,3) )
            customdata = np.zeros( (npts,10) )
            for isp in range( npts ):
                hit = cluster.at(isp)
                for i in range(0,3):
                    pos[isp,i] = hit[i]

                customdata[isp,0] = hit.targetwire[0]
                customdata[isp,1] = hit.targetwire[1]
                customdata[isp,2] = hit.targetwire[2]
                customdata[isp,3] = hit.tick
                customdata[isp,4] = hit.renormed_shower_score
                for c in range(5):
                    customdata[isp,5+c] = hit[10+c]
            # end of hit loop
            
            # make trace
            cluster_plot = {
                "type":"scatter3d",
                "x": pos[:,0],
                "y": pos[:,1],
                "z": pos[:,2],
	        "mode":"markers",
	        "name":f"[{icluster}]",
                "hovertemplate":hovertemplate,
                "customdata":customdata,
                "marker":{"color":customdata[:,4],"size":1,"opacity":0.2,"colorscale":"bluered","cmin":0.0,"cmax":1.0}
            }
            traces.append(cluster_plot)
        # end of cluster loop
    #end of tree loop

    return traces

register_det3d_plotter("nuinputclustersbyssnet",are_products_present,make_plot_option_widgets,make_traces)




