import os,sys
import numpy as np

def visualize_larlite_crttrack( larlite_crttrack, notimeshift=False, marker_color='rgb(0,230,0)', line_color='rgb(10,50,50)' ):

    if notimeshift:
        dx = 0.0
        t_usec = 0.0
    else:
        from larlite import larutil
        dv = larutil.LArProperties.GetME().DriftVelocity()    
        t_usec = 0.5*(larlite_crttrack.ts2_ns_h1+larlite_crttrack.ts2_ns_h2)*0.001 # convert to microseconds
        dx = t_usec*dv
    
    xyz = np.zeros( (2,4 ) )
    xyz[0,0] = larlite_crttrack.x1_pos + dx
    xyz[0,1] = larlite_crttrack.y1_pos
    xyz[0,2] = larlite_crttrack.z1_pos
    xyz[0,3] = larlite_crttrack.ts2_ns_h1*0.001
    xyz[1,0] = larlite_crttrack.x2_pos + dx
    xyz[1,1] = larlite_crttrack.y2_pos
    xyz[1,2] = larlite_crttrack.z2_pos
    xyz[1,3] = larlite_crttrack.ts2_ns_h2*0.001

    customdata = np.zeros( (2,3) ) # columns: t1 us, tick1, plane1
    customdata[0][0] = larlite_crttrack.ts2_ns_h1*0.001
    customdata[0][1] = 3200 + larlite_crttrack.ts2_ns_h1*0.001/0.5 # tpc tick
    customdata[0][2] = larlite_crttrack.plane1

    customdata[1][0] = larlite_crttrack.ts2_ns_h2*0.001
    customdata[1][1] = 3200 + larlite_crttrack.ts2_ns_h2*0.001/0.5 # tpc tick
    customdata[1][2] = larlite_crttrack.plane2
    hovertemplate = """
    <b>x</b>: %{x}<br>
    <b>y</b>: %{y}<br>
    <b>z</b>: %{z}<br>
    <b>t</b>: %{customdata[0]} usec<br>
    <b>tick</b>: %{customdata[1]}<br>
    <b>CRT plane</b>: %{customdata[2]}<br>
    """

    crttrack = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        "name":"",
        "mode":"lines+markers",
        "hovertemplate":hovertemplate,
        "customdata":customdata,
        "marker":{"color":marker_color,"size":8,"opacity":0.8},
        "line":{"color":line_color,"width":2},
    }

    return crttrack

def visualize_larlite_event_crttrack( larlite_event_crttrack, name="",
                                      window=[-500.0,2700],
                                      notimeshift=False,
                                      marker_color='rgb(0,230,0)',
                                      line_color='rgb(10,50,50)' ):

    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()    
    
    ntracks = larlite_event_crttrack.size()

    crttracks_v = []
    for itrack in range(ntracks):
        crttrack = larlite_event_crttrack.at(itrack)

        trace = visualize_larlite_crttrack( crttrack, notimeshift=notimeshift,
                                            marker_color=marker_color,
                                            line_color=line_color )
        crttracks_v.append( trace )

    return crttracks_v
