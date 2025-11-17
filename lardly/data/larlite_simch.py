from __future__ import print_function
import os,sys

import numpy as np
from ROOT import std
from larlite import larlite,larutil
from ublarcvapp import ublarcvapp

def visualize_larlite_simch( event_simch_v, color_by='edep', opacity=1.0, marker_size=2.0, 
                            min_image_tick=2400, max_image_tick=8448,
                            max_num_pts=20000,
                            ioll=None ):

    timeservice = larutil.TimeService.GetME()

    nsimch = event_simch_v.size()
    min_tdc = 1e9
    max_tdc = 0
    min_tick = 50000
    max_tick = 0
    pos_v = []
    tid_v = []

    tid_map = {}
    for isimch in range(nsimch):
        simch = event_simch_v.at(isimch)
        chid = simch.Channel()
        idcmap = simch.TDCIDEMap()
        nentries = idcmap.size()
        for it in idcmap:

            tdc = float(it.first)
            tick = int(timeservice.TPCTDC2Tick(tdc))

            if min_tdc > tdc:
                min_tdc = tdc
            if max_tdc < it.first:
                max_tdc = tdc

            if min_tick > tick:
                min_tick = tick
            if max_tick < tick:
                max_tick = tick

            if tick<min_image_tick or tick>max_image_tick:
                continue

            ide_v = it.second
            nide = ide_v.size()
            for iide in range(nide):
                ide = ide_v.at(iide)
                tid = int(ide.trackID)
                if tid not in tid_map:
                    tid_map[tid] = {}
                if tick not in tid_map[tid]:
                    tid_map[tid][tick] = []
                tid_map[tid][tick].append( (chid,ide.energy,ide.x,ide.y,ide.z) )
                pos_v.append( (ide.x,ide.y,ide.z,ide.energy,chid) )
                tid_v.append( (tid) )


        #print(f"Simch[{chid}]: num ide map entries = {nentries}")
    #print("tdc: [",min_tdc,",",max_tdc,"]")
    #print("tick: [",min_tick,",",max_tick,"]")
    #print("Number of deposits within image tick bounds: ",len(pos_v))
    # for tid in tid_map:
    #     print("TRACKID[",tid,"]")
    #     tick_map = tid_map[tid]
    #     #for tick in tick_map:
    #     #    print("  tick[",tick,"]: ",tick_map[tick])

    data = np.array( pos_v )
    tid_array = np.array( tid_v )
    #print("data array: ",data.shape)

    if data.shape[0]>max_num_pts:
        indexlist = np.arange(data.shape[0])
        np.random.shuffle(indexlist)
        data = data[indexlist[:max_num_pts],:]
        tid_array = tid_array[indexlist[:max_num_pts]]
        #print("downsampled data array: ",data.shape)

    mcpg = None
    if color_by in ['instance','ancestor'] and ioll is not None:
        # replace IDs by shower mother id
        tid_showermid = {}
        mcpg = ublarcvapp.mctools.MCPixelPGraph()
        mcpg.buildgraphonly( ioll )
        unique_tid = np.unique( tid_array )
        for tid in unique_tid:
            #print("find tid: ",tid," ",type(tid))
            xtid = abs(int(tid))
            mtid = mcpg.getShowerMotherID( xtid )
            if mtid<0 and int(tid)<0:
                mtid = mcpg.getShowerMotherID( int(tid) )
            if mtid>0:
                #print("  found shower motherid: ",mtid)
                tid_showermid[int(tid)] = mtid
            else:
                tid_showermid[int(tid)] = int(tid)
        for tid in unique_tid:
            tid_mask = tid_array==tid
            tid_array[tid_mask[:]] = tid_showermid[int(tid)]


    if color_by=='ancestor' and ioll is not None:
        tid_to_ancestor = {}
        if mcpg is None:
            mcpg = ublarcvapp.mctools.MCPixelPGraph()
            mcpg.buildgraphonly( ioll )
        
        #mcpg.printAllNodeInfo()
        unique_tid = np.unique( tid_array )
        for tid in unique_tid:
            #print("find aid for tid: ",tid," ",type(tid))
            aid = mcpg.getAncestorID( xtid )
            if aid<=0:
                #print(" cannot get aid for tid=",xtid)
                tid_to_ancestor[tid] = xtid
                continue
            else:
                #print(" ancestor found: ",aid)
                tid_to_ancestor[tid] = aid

        for tid in unique_tid:
            tid_mask = tid_array==tid
            tid_array[tid_mask[:]] = tid_to_ancestor[tid]

    
    labels_v = []
    if mcpg is not None:
        print("Make customdata for hovertemplate")
        for i in range(data.shape[0]):
            xtid = int(tid_array[i])
            pid  = float(mcpg.getParticleID(xtid))
            aid  = float(mcpg.getAncestorID(xtid))
            chid = data[i,4]
            edep = data[i,3]
            labels_v.append((edep,pid,float(xtid),aid,chid))
        customdata = np.array( labels_v, dtype=np.float32 )
        hovertemplate = """
        <b>x</b>: %{x:.1f}<br>
        <b>y</b>: %{y:.1f}<br>
        <b>z</b>: %{z:.1f}<br>
        <b>edep</b>: %{customdata[0]:.3f} MeV<br>
        <b>PID</b>:  %{customdata[1]:d}<br>
        <b>TID</b>:  %{customdata[2]:d}<br>
        <b>AID</b>:  %{customdata[3]:d}<br>
        <b>ChID</b>: %{customdata[4]:d}<br>
        """
    else:
        customdata = None
        hovertemplate = None

    simch_plots = []
    if color_by=='edep':
        simch_plot = {
             "type":"scatter3d",
             "x":data[:,0],
             "y":data[:,1],
             "z":data[:,2],
             "mode":"markers",
             "name":"simch",
             "marker":{"color":data[:,3],'opacity':opacity,'size':marker_size},
        }
        simch_plots.append( simch_plot )
    elif color_by in ['instance','ancestor']:
        unique_tid = np.unique( tid_array )
        for tid in unique_tid:
            instance_mask = tid_array==tid
            xdata = data[instance_mask[:],:]
            if customdata is not None:
                xcustomdata = customdata[instance_mask[:],:]
            rcolor = np.random.randint(0,255,3)
            strcolor = "rgba(%d,%d,%d,1.0)"%(rcolor[0],rcolor[1],rcolor[2])
            if hovertemplate is None:
                simch_plot = {
                    "type":"scatter3d",
                    "x":xdata[:,0],
                    "y":xdata[:,1],
                    "z":xdata[:,2],
                    "mode":"markers",
                    "name":f"tid[{tid}]",
                    "marker":{"color":strcolor,"opacity":opacity,"size":marker_size}
                }
            else:
                #print("simch plot with template")
                simch_plot = {
                    "type":"scatter3d",
                    "x":xdata[:,0],
                    "y":xdata[:,1],
                    "z":xdata[:,2],
                    "mode":"markers",
                    "name":f"tid[{tid}]",
                    "customdata":xcustomdata,
                    "hovertemplate":hovertemplate,
                    "marker":{"color":strcolor,"opacity":opacity,"size":marker_size}
                }                
            simch_plots.append( simch_plot )
    else:
        raise ValueError("Unrecognized color_by option: ",color_by)

    return simch_plots

if __name__=="__main__":

    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output, State
    from dash.exceptions import PreventUpdate

    import lardly
    from lardly.detectoroutline import DetectorOutline

    detdata = DetectorOutline()
    colorby = 'instance'
    #colorby = 'ancestor'
    #colorby = 'edep'

    input_larlite_file = sys.argv[1]
    if len(sys.argv)>=3:
        producer = sys.argv[2]
    else:
        producer = "largeant"

    print("Dump SimCh Info from file: ",input_larlite_file)
    print("Producer: ",producer)
    ioll = larlite.storage_manager(larlite.storage_manager.kREAD)
    ioll.add_in_filename( input_larlite_file )
    ioll.set_verbosity(1)
    ioll.open()
    nentries = ioll.get_entries()

    # for ientry in range(nentries):
    #     ioll.go_to(ientry)
    #     event_simch = ioll.get_data("simch",producer)
    #     simch_plot = visualize_larlite_simch( event_simch )
    #     print("[enter] to continue")
    #     input()
    # print("fin")

    ioll.go_to(0)
    event_simch = ioll.get_data("simch",producer)
    simch_plots = visualize_larlite_simch( event_simch, color_by=colorby, ioll=ioll )

    traces = detdata.getlines()+simch_plots

    if False:
        sys.exit(0)

    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )

    server = app.server

    axis_template = {
        "showbackground": True,
        "backgroundcolor": "#141414",
        "gridcolor": "rgb(255, 255, 255)",
        "zerolinecolor": "rgb(255, 255, 255)",
    }

    plot_layout = {
        "title": "",
        "height":800,
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
        "font": {"size": 12, "color": "white"},
        "showlegend": False,
        "plot_bgcolor": "#141414",
        "paper_bgcolor": "#141414",
        "scene": {
            "xaxis": axis_template,
            "yaxis": axis_template,
            "zaxis": axis_template,
            "aspectratio": {"x": 1, "y": 1, "z": 4},
            "camera": {"eye": {"x": 2, "y": 2, "z": 2},
                       "up":dict(x=0, y=1, z=0)},
            "annotations": [],
        },
    }

    


    app.layout = html.Div( [
        html.Div( [
            dcc.Graph(
                id="det3d",
                figure={
                    "data": traces,
                    "layout": plot_layout,
                },
                config={"editable": True, "scrollZoom": False},
            )],
            className="graph__container"),
        ] )

    app.run_server(debug=True)

