from __future__ import print_function
import os,sys

import numpy as np
from ROOT import std
from larlite import larlite,larutil

def visualize_larlite_simch( event_simch_v, color=None, opacity=1.0, 
                            min_image_tick=2400, max_image_tick=8448,
                            max_num_pts=100 ):

    timeservice = larutil.TimeService.GetME()

    nsimch = event_simch_v.size()
    min_tdc = 1e9
    max_tdc = 0
    min_tick = 1e9
    max_tick = 0
    pos_v = []
    for isimch in range(nsimch):
        simch = event_simch_v.at(isimch)
        chid = simch.Channel()
        idcmap = simch.TDCIDEMap()
        nentries = idcmap.size()
        for it in idcmap:

            tdc = float(it.first)
            tick = timeservice.TPCTDC2Tick(tdc)

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
                pos_v.append( (ide.x,ide.y,ide.z,tick,ide.trackID,ide.energy) )

        #print(f"Simch[{chid}]: num ide map entries = {nentries}")
    print("tdc: [",min_tdc,",",max_tdc,"]")
    print("tick: [",min_tick,",",max_tick,"]")
    print("Number of deposits within image tick bounds: ",len(pos_v))

    data = np.array( pos_v )
    print("data array: ",data.shape)

    if data.shape[0]>max_num_pts:
        indexlist = np.arange(data.shape[0])
        np.random.shuffle(indexlist)
        data = data[indexlist[:max_num_pts],:]
        print("downsampled data array: ",data.shape)
    
    print(data[:10])

    simch_plot = {
        "type":"scatter3d",
        "x":data[:,0],
        "y":data[:,1],
        "z":data[:,2],
        "mode":"markers",
        "name":"simch",
        "marker":{"color":'rgba(255,255,255,1.0)','opacity':0.5},
    }

    return simch_plot

if __name__=="__main__":

    import dash
    import dash_core_components as dcc
    import dash_html_components as html
    from dash.dependencies import Input, Output, State
    from dash.exceptions import PreventUpdate

    import lardly
    from lardly.detectoroutline import DetectorOutline

    detdata = DetectorOutline()

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
    simch_plot = visualize_larlite_simch( event_simch )

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
                    "data": detdata.getlines()+[simch_plot],
                    "layout": plot_layout,
                },
                config={"editable": True, "scrollZoom": False},
            )],
            className="graph__container"),
        ] )

    app.run_server(debug=True)

