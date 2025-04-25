import os
from .det3d_plot_factory import register_det3d_plotter
from dash import html
import numpy as np
import lardly
from lardly.data.larlite_crttrack import visualize_larlite_event_crttrack
from lardly.data.larlite_crthit import visualize_larlite_event_crthit
from lardly.data.larlite_opflash import visualize_larlite_opflash_3d
from ublarcvapp import ublarcvapp
from larlite import larlite, larutil

def are_products_present( keys ):
    required_trees = ["crttrack_crttrack_tree"]
    hastrees = True
    for treename in required_trees:
        if treename not in keys:
            print('failed check for ',treename)
            hastrees = False
            
    return hastrees

def make_plot_option_widgets( keys ):
    """
    no options
    """
    return [html.Label('RecoCRT: no options')]

def make_traces( tree_dict ):

    iolarlite = tree_dict['iolarlite']

    print("call det3d_crt_plot.make_traces")
    ev_crttrk = iolarlite.get_data("crttrack","crttrack")
    ev_crthit = iolarlite.get_data("crthit","crthitcorr")    
    print("  num CRT track objects: ",ev_crttrk.size())
    print("  num CRT hit objects: ",ev_crthit.size())

    ev_flash = iolarlite.get_data("opflash","simpleFlashCosmic")
    flash_times = None
    if ev_flash.size()>0:
        flash_times = np.zeros( ev_flash.size() )
        for iflash in range(ev_flash.size()):
            flash = ev_flash.at(iflash)
            flash_times[iflash] = flash.Time()

    crt_traces = []
    opdet_traces = []
    if ev_crttrk.size()>0:
        track_traces = visualize_larlite_event_crttrack( ev_crttrk )

        for itrack,trace in enumerate(track_traces):
            trace['marker']['size']=4.0
            trace['name'] = f"crttrack[{itrack}]"
            if flash_times is not None:
                # filter crt track by proximity to opflash
                tusec = trace['customdata'][0,0] # (t,tick,plane)
                dt = np.abs(flash_times-tusec)
                dtmin = np.min( dt )
                iflashmin = int(np.argmin( dt ))
                #print("  ",trace['name'],": dtick=",dtick," usec, iflashmin=",iflashmin)
                if dtmin<1.0:
                    crt_traces.append( trace )
                    flash = ev_flash.at(iflashmin)
                    #opdet_traces += visualize_larlite_opflash_3d( flash, xpos_by_time=True, pe_draw_threshold=5.0 )


    if ev_crthit.size()>0:
        notimeshift = False
        hitinfo_v = []
        dv = larutil.LArProperties.GetME().DriftVelocity()
        
        crthit_hovertemplate = """
        <b>x</b>: %{x}<br>
        <b>y</b>: %{y}<br>
        <b>z</b>: %{z}<br>
        <b>t</b>: %{customdata[0]} usec<br>
        <b>tick</b>: %{customdata[1]}<br>
        <b>CRT plane</b>: %{customdata[2]}<br>
        """
        
        for ihit in range( ev_crthit.size() ):
            crthit = ev_crthit.at(ihit)
            hitinfo = np.zeros(6)
            t_usec = crthit.ts2_ns*0.001
            dx = t_usec*dv
            
            hitinfo[0] = crthit.x_pos+dx
            hitinfo[1] = crthit.y_pos
            hitinfo[2] = crthit.z_pos
            hitinfo[3] = t_usec
            hitinfo[4] = 3200 + t_usec/0.5
            hitinfo[5] = crthit.plane

            dt = np.abs(flash_times-t_usec)
            dtmin = np.min(dt)
            #print("  crthit[",ihit,"]: dt=",dt," usec")
            if dtmin<1.0:
                hitinfo_v.append( hitinfo )

        if len(hitinfo_v)>1:
            hitinfo_all = np.stack( hitinfo_v, axis=0 )
            print("   hitinfo_all.shape=",hitinfo_all.shape)
        elif len(hitinfo_v)==1:
            hitinfo_all = hitinfo_v[0]

        if len(hitinfo_v)>0:
            crthit_trace = {
                "type":"scatter3d",
                "x": hitinfo_all[:,0],
                "y": hitinfo_all[:,1],
                "z": hitinfo_all[:,2],
                "mode":"markers",
                "name":"crthits",
                "hovertemplate":crthit_hovertemplate,
                "customdata":hitinfo_all[:,3:],
                "marker":{"color":"rgb(255,0,255)","size":3,"opacity":0.5},
            }
            crt_traces.append( crthit_trace )
                
    print("  number of crttrack traces: ",len(crt_traces))
    if len(crt_traces):
        crt_traces += lardly.CRTOutline().getlines()
        crt_traces += opdet_traces
    return crt_traces

register_det3d_plotter("RecoCRT",are_products_present,make_plot_option_widgets,make_traces)

