import os,sys
import numpy as np
from ROOT import std
from larlite import larlite,larutil

def visualize_larlite_track( larlite_track, track_id=None, color=None, show_projection_info=True ):

    npoints = larlite_track.NumberTrajectoryPoints()
    xyz = np.zeros( (npoints,3 ) )
    for ipt in range(npoints):
        for i in range(3):
            xyz[ipt,i] = larlite_track.LocationAtPoint(ipt)(i)


    if track_id is None:
        name = ""
    else:
        name = ""
        if type(track_id) is int:
            name = "tid[{}]".format(track_id)
        elif type(track_id) is str:
            name = track_id

    if color is None:
        color = "rgb(255,0,0)"
    elif type(color) is str and "dqdx" in color:
        p_dqdx = 2
        if "-" in color:
            p_dqdx = int(color.split("-")[-1])
        ndqdx = larlite_track.NumberdQdx(0)
        vcolor = np.zeros( npoints )
        if  ndqdx>0:
            for ipt in range(npoints):
                vcolor[ipt] = larlite_track.DQdxAtPoint(ipt,p_dqdx)
    elif type(color) is str and 'rgb' in color:
        pass
    else:
        color = "rgb({},{},{})".format(color[0],color[1],color[2])

    track = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "mode":"lines",
        "name":name,
        "line":{"color":color,"width":2},
    }
        
    if show_projection_info:
        cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5                
        customdata = np.zeros( (npoints,5) )
        hovertemplate="""
        <b>x</b>: %{x:.1f}<br>
        <b>y</b>: %{y:.1f}<br>
        <b>z</b>: %{z:.1f}<br>
        <b>t</b>: %{customdata[0]:.1f} usec<br>
        <b>tick</b>: %{customdata[1]:.0f}<br>
        <b>U</b>: %{customdata[2]:.0f}<br>
        <b>V</b>: %{customdata[3]:.0f}<br>
        <b>Y</b>: %{customdata[4]:.0f}<br>
        """

        for ipt in range(npoints):
            loc = larlite_track.LocationAtPoint(ipt)
            x = larlite_track.LocationAtPoint(ipt)[0]
            tick = 3200 + x/cm_per_tick
            t = x/cm_per_tick*0.5
            customdata[ipt,0] = t
            customdata[ipt,1] = tick
            for p in range(3):
                customdata[ipt,2+p] = larutil.Geometry.GetME().WireCoordinate( loc, p )

        track['hovertemplate'] = hovertemplate
        track['customdata'] = customdata

    if type(color) is str and "dqdx" in color:
        track["mode"] = "lines+markers"
        track["marker"] = {"color":vcolor,"size":3.0,"colorscale":"Viridis"}        
        track["line"]["color"] = "rgb(255,0,0)"

    return track

def visualize_larlite_track_vtx( larlite_track ):

    xyz = np.zeros( (1,3 ) )
    xyz[0,0] = larlite_track.Vertex().x()
    xyz[0,1] = larlite_track.Vertex().y()
    xyz[0,2] = larlite_track.Vertex().z()
    vtx = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        'mode': 'markers',
        'marker': {'size': 4},
        "name":"",
        "line":{"color":"rgb(0,255,0)","width":2},
    }

    return vtx

def visualize_larlite_track_end( larlite_track ):

    xyz = np.zeros( (1,3 ) )
    xyz[0,0] = larlite_track.End().x()
    xyz[0,1] = larlite_track.End().y()
    xyz[0,2] = larlite_track.End().z()
    End = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        'mode': 'markers',
        'marker': {'size': 4},
        "name":"",
        "line":{"color":"rgb(255,255,0)","width":2},
    }

    return End

def visualize2d_larlite_track( larlite_track, larcv_image2d_v, track_id=None, color=None ):
    """ plot path projected into wire planes """

    npoints = larlite_track.NumberTrajectoryPoints()
    cm_per_tick = larutil.LArProperties.GetME().DriftVelocity()*0.5        

    if color is None:
        color = "rgb(255,0,0)"
    else:
        color = "rgb({},{},{})".format(color[0],color[1],color[2])
    
    name = ""
    if type(track_id) is str:
        name = track_id
    elif type(track_id) is int:
        name = "id[{}]".format(track_id)
        
    traces2d = {}
    for p in range(larcv_image2d_v.size()):

        wt = np.zeros( (npoints,2) )

        for ipt in range(npoints):
            wire = larutil.Geometry.GetME().WireCoordinate( larlite_track.LocationAtPoint(ipt), p )
            x = larlite_track.LocationAtPoint(ipt)[0]
            tick = 3200 + x/cm_per_tick
            wt[ipt,0] = wire
            wt[ipt,1] = tick
        traces2d[p] = {
            "type":"scatter",
            "x":wt[:,0],
            "y":wt[:,1],
            "mode":"lines",
            "name":name,
            "line":{"color":color,"width":2},
        }
        
    return traces2d

    
