from __future__ import print_function
import os,sys,argparse

if "DLLEE_UNIFIED_BASEDIR" in os.environ or "DLLEE_UNIFIED_DIR" in os.environ:
    print("DLLEE UNIFIED DETECTED")
    REPO = "UNIFIED"
elif "UBDL_BASEDIR" in os.environ:
    print("UBDL DETECTED")
    REPO = "UBDL"    
else:
    print("Must setup either DLLEE_UNIFIED or UBDL repository")
    sys.exit(0)

parser = argparse.ArgumentParser("test_3d lardly viewer w/ DL Merged File")
parser.add_argument("-i","--input-file",required=True,type=str,help="dlmerged file")
parser.add_argument("-e","--entry",required=True,type=int,help="Entry to load")
parser.add_argument("-lf","--larflow",type=str,default=None,help="Provide input larflow file (optional)")
parser.add_argument("-crt","--has-crt",default=False,action='store_true',help="Plot CRT information (assumed to be available)")
parser.add_argument("-ns","--no-shower",default=True,action='store_false',help="No shower")
parser.add_argument("-mc","--mc-tracks",default=False,action='store_true',help="Plot MC Tracks")
parser.add_argument("-p","--port",default=8050,type=int,help="Set Port. Default (8050)")

args = parser.parse_args(sys.argv[1:])

import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from larlite import larlite
from larcv import larcv
from ROOT import larutil
import numpy as np
#print(larcv.load_pyutil)
#larcv.load_pyutil

import lardly

ientry = args.entry

HAS_TRACKS = True
HAS_SHOWERS = args.no_shower
HAS_PIXELS = False
HAS_LARMATCH = False
PLOT_COSMIC_TAGGER = False
if args.larflow is not None:
    HAS_LARMATCH = True
FLIP_IMAGE2D = False
if REPO=="UNIFIED":
    FLIP_IMAGE2D = True
USE_NEW_SHOWER=True


# ======================================
# IO
# --
# LARLITE
io_ll = larlite.storage_manager(larlite.storage_manager.kREAD)
io_ll.add_in_filename( args.input_file )

# BONUS: larflow hits
if HAS_LARMATCH:
    io_ll.add_in_filename( args.larflow )
    
io_ll.open()
io_ll.go_to(ientry)


# LARCV
if REPO=="UBDL":    
    io_cv = larcv.IOManager(larcv.IOManager.kREAD,"larcv",larcv.IOManager.kTickBackward)
else:
    io_cv = larcv.IOManager(larcv.IOManager.kREAD,"larcv")
io_cv.add_in_file( args.input_file )
if REPO=="UBDL":
    io_cv.reverse_all_products()
io_cv.initialize()
io_cv.read_entry(ientry)

# ======================================
# TRACE CONTAINERS
traces3d = []
traces2d = {0:[],1:[],2:[]}

ev_adc = io_cv.get_data( larcv.kProductImage2D, "wire" )
img_v  = ev_adc.Image2DArray()

# OPFLASH
evopflash_beam   = io_ll.get_data(larlite.data.kOpFlash,"simpleFlashBeam")
evopflash_cosmic = io_ll.get_data(larlite.data.kOpFlash,"simpleFlashCosmic")

# VERTEX
if True:
    # vertices: 2d
    ev_pgraph = io_cv.get_data( larcv.kProductPGraph,  "test" )
    ev_pclust = io_cv.get_data( larcv.kProductPixel2D, "test_ctor" )
    print("Number of vertices: ",ev_pgraph.PGraphArray().size())

    pgraph_traces2d = lardly.data.visualize2d_larcv_pgraph( ev_pgraph, event_contour_pixels=ev_pclust )
    for p in range(3):
        traces2d[p] += pgraph_traces2d[p]

    # 3D vertices                                                                                                                                                                                       
    pgraph_traces3d = lardly.data.visualize3d_larcv_pgraph( ev_pgraph )

    traces3d += pgraph_traces3d

# PATICLE TRACK
if True:
    evtrack     = io_ll.get_data(larlite.data.kTrack,"trackReco")
    evtrack_sce = io_ll.get_data(larlite.data.kTrack,"trackReco_sceadded")    
    print("number of tracks: ",evtrack.size())
    traces3d += [ lardly.data.visualize_larlite_track( evtrack_sce[i], color=(255,165,0) ) for i in range(evtrack_sce.size())  ]

    for itrack in range(evtrack.size()):
        track_traces = lardly.data.visualize2d_larlite_track( evtrack[itrack], img_v, color=(255,165,0) )
        for p in range(3):
            traces2d[p].append( track_traces[p] )

# SHOWER
if HAS_SHOWERS:
    # 3D Showers
    if not USE_NEW_SHOWER:
        ev_shower = io_ll.get_data( larlite.data.kShower, "showerreco" )
        print("number of showers (showerreco): ",ev_shower.size())
        shower_traces = [ lardly.data.visualize3d_larlite_shower( ev_shower.at(x) ) for x in range(ev_shower.size()) ]
        traces3d += shower_traces

        shower2d_traces = [ lardly.data.visualize2d_larlite_shower( ev_shower.at(x) ) for x in range(ev_shower.size()) ]
        for shower2d_trace in shower2d_traces:
            print("shower trace: ",shower2d_trace)
            for p in range(3):
                traces2d[p].append( shower2d_trace[p] )
    else:
        ev_shower = io_ll.get_data( larlite.data.kShower, "ssnetshowerreco" )
        print("number of showers (ssnetshowerreco): ",ev_shower.size())
        pixheight = img_v[0].meta().pixel_height()
        for ishr in xrange(ev_shower.size()):
            ll_shr = ev_shower.at(ishr)
            shower_angle = np.arctan2( ll_shr.Direction()[1], ll_shr.Direction()[0] )
            tick = ll_shr.ShowerStart()[0]/larutil.LArProperties.GetME().DriftVelocity()/0.5+3200
            wire = larutil.Geometry.GetME().WireCoordinate( ll_shr.ShowerStart(), ll_shr.best_plane() )
            row = img_v[0].meta().row(tick)
            
            np_shr = np.zeros( (4,2) )
            np_shr[0,1] = tick
            np_shr[0,0] = wire

            row1 = int(row) - int(ll_shr.Length()*np.sin( shower_angle+ll_shr.OpeningAngle() ))
            row2 = int(row) - int(ll_shr.Length()*np.sin( shower_angle-ll_shr.OpeningAngle() ))
            if row1<0 or row2<0:
                print("invalid shower[idx={}] rows: row1={} row2={}".format(ishr,row1,row2))
                if row1<0:
                    row1 = 0
                if row2<0:
                    row2 = 0
            
            np_shr[1,1] = img_v[0].meta().pos_y( row1 )
            np_shr[1,0] = wire + ll_shr.Length()*np.cos( shower_angle+ll_shr.OpeningAngle() )
            np_shr[2,1] = img_v[0].meta().pos_y( row2 )
            np_shr[2,0] = wire + ll_shr.Length()*np.cos( shower_angle-ll_shr.OpeningAngle() )
            np_shr[3,:] = np_shr[0,:]
            shower2d_trace = {
                "x":np_shr[:,0],
                "y":np_shr[:,1],
                "name":"vtx[%d]"%(ll_shr.ID()),
                "mode":"lines",
                "line":{"color":"rgb(255,155,255)"},
            }
            traces2d[ll_shr.best_plane()].append( shower2d_trace )
        
# COSMIC TRACKS
if PLOT_COSMIC_TAGGER:
    ev_cosmics = io_ll.get_data(larlite.data.kTrack,"mergedthrumu3d")
    if ev_cosmics.size()>0:
        traces3d += [ lardly.data.visualize_larlite_track( ev_cosmics[i], color=(255,0,0) ) for i in range(ev_cosmics.size())  ]

# MCTRACK
if args.mc_tracks:
    print("VISUALIZE MCTRACKS")
    mctrack_v = lardly.data.visualize_larlite_event_mctrack( io_ll.get_data(larlite.data.kMCTrack, "mcreco"))
    traces3d += mctrack_v

# LARFLOW HITS
if HAS_LARMATCH:
    print("Visualize LArFlow Hits")
    ev_lfhits = io_ll.get_data(larlite.data.kLArFlow3DHit,"larmatch")
    print("  num larflow hits: ",ev_lfhits.size())
    lfhits_v =  [ lardly.data.visualize_larlite_larflowhits( ev_lfhits, "larmatch" ) ]
    traces3d += lfhits_v

# CRT
if args.has_crt:
    print("Visualize CRT")
    ev_crthits = io_ll.get_data(larlite.data.kCRTHit,"crthitcorr")
    crthit_v = [ lardly.data.visualize_larlite_event_crthit( ev_crthits, "crthitcorr") ]
    #filtered_crthit_v = lardly.ubdl.filter_crthits_wopreco( evopflash_beam, evopflash_cosmic, ev_crthits )
    #vis_filtered_crthit_v = [ lardly.data.visualize_larlite_crthit( x ) for x in filtered_crthit_v ]
    traces3d += crthit_v
    min_crt_ns = 1.0e9
    max_crt_ns = -1.0e9
    for ihit in range(ev_crthits.size()):
        ns = ev_crthits[ihit].ts2_ns
        min_crt_ns = min(min_crt_ns,ns)
        max_crt_ns = max(max_crt_ns,ns)
    print("Min CRT time (usec): ",min_crt_ns*0.001,"  Max CRT time (usec): ",max_crt_ns*0.001)

    # CRT TRACKS
    evtracks   = io_ll.get_data(larlite.data.kCRTTrack,"crttrack")
    crttrack_v = lardly.data.visualize_larlite_event_crttrack( evtracks, "crttrack")
    traces3d += crttrack_v
    
# IMAGE2D
ev_img = io_cv.get_data( larcv.kProductImage2D, "wire" )
img2d_v = ev_img.Image2DArray()

if False:
    ev_pix = io_cv.get_data( larcv.kProductPixel2D, "allreco" )
    pix_meta_v = [ ev_pix.ClusterMetaArray(p) for p in range(3) ]
    pix_arr_v = [ ev_pix.Pixel2DClusterArray()[p] for p in range(3) ]
    pixtraces = [ lardly.data.visualize_larcv_pixel2dcluster( pix_arr_v[0][i], pix_meta_v[0][0] ) for i in range(pix_arr_v[0].size()) ]

detdata = lardly.DetectorOutline()

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
        #"aspectratio": {"x": 1, "y": 1, "z": 4},
        "camera": {"eye": {"x": 2, "y": 2, "z": 2},
                   "up":dict(x=0, y=1, z=0)},
        "annotations": [],
    },
}

testline = {
    "type":"scattergl",
    "x":[200,400,400,800],
    "y":[3200,3400,3800,4400],
    "mode":"markers",
    #"line":{"color":"rgb(255,255,255)","width":4},
    "marker":dict(size=10, symbol="triangle-up",color="rgb(255,255,255)"),
    }

app.layout = html.Div( [
    html.Div( [
        dcc.Graph(
            id="det3d",
            figure={
                "data": detdata.getlines()+traces3d,
                "layout": plot_layout,
            },
            config={"editable": True, "scrollZoom": False},
        )],
              className="graph__container"),
    html.Div( [
        dcc.Graph(
            id="image2d_plane0",
            figure={"data":[ lardly.data.visualize_larcv_image2d( img2d_v[0], reverse_ticks=FLIP_IMAGE2D )]+traces2d[0],
                    "layout":{"height":800} }),
        dcc.Graph(
            id="image2d_plane1",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[1], reverse_ticks=FLIP_IMAGE2D )]+traces2d[1],
                    "layout":{"height":800}}),
        dcc.Graph(
            id="image2d_plane2",
            figure={"data":[lardly.data.visualize_larcv_image2d( img2d_v[2], reverse_ticks=FLIP_IMAGE2D )]+traces2d[2],
                    "layout":{"height":800}}),
        ] ),
    ] )

if __name__ == "__main__":
    app.run_server(port=args.port,debug=True)
