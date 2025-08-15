from __future__ import print_function
import os,sys
from ..ubdl.pmtpos import getPMTPosByOpChannel, getPMTPosByOpDet, getOpChannelFromOpDet, getOpDetFromOpChannel
import numpy as np
from plotly import graph_objects as go

def define_circle_mesh( center, radius, value, nsteps=20, color=None, outline_color=None,x_offset=0,rgb_channel='r'):

    np_theta = np.linspace(0,2*np.pi,nsteps)    
    x = np.ones( nsteps+1 )*center[0]
    y = np.zeros( nsteps+1 )
    z = np.zeros( nsteps+1 )
    y[:nsteps] = np.sin(np_theta)*radius
    z[:nsteps] = np.cos(np_theta)*radius
    y += center[1]
    z += center[2]

    # define vertex indices
    
    i = np.ones( nsteps, dtype=np.int64)*nsteps # always points to center
    j = np.zeros( nsteps, dtype=np.int64 )
    k = np.zeros( nsteps, dtype=np.int64 )
    for n in range(nsteps):
        j[n] = n
        if n+1==nsteps:
            k[n] = 0
        else:
            k[n] = n+1

    if color is None:
        value = min(1.0,value)
        value = max(0.0,value)
        if rgb_channel=='r':
            color='rgb(%d,0,0)'%( 54+int(value*200) )
        elif rgb_channel=='g':
            color='rgb(0,%d,0)'%( 54+int(value*200) )
        elif rgb_channel=='b':
            color='rgb(0,0,%d)'%( 54+int(value*200) )
        else:
            raise ValueError("rgb_channel must either be r, g, or b")

    mesh = go.Mesh3d( x=x, y=y, z=z, i=i, j=j, k=k,
                      showscale=False, name="opflash", color=color )

    lx = np.copy(x)
    ly = np.copy(y)
    lz = np.copy(z)
    lx[nsteps] = lx[0]
    ly[nsteps] = ly[0]
    lz[nsteps] = lz[0]

    if outline_color is None:
        outline_color="rgb(255,255,255)"
        
    lines = go.Scatter3d( x=lx, y=ly, z=lz, mode="lines", name="opflash", line={"color":outline_color,"width":1} )

    return mesh,lines


def visualize_larlite_opflash_3d( opflash, pmt_radius_cm=15.24,
                                  min_pe=None, max_pe=None,
                                  use_v4_geom=False,
                                  use_opdet_index=False,
                                  xpos_by_time=False,
                                  x_offset=0,
                                  rgb_channel='r',
                                  pe_draw_threshold=0.0):
    from larlite import larlite
    from larlite import larutil
    dv = larutil.LArProperties.GetME().DriftVelocity()
    
    circles = []
    nsteps = 20
    # for ipmt in xrange(32):
    # we have to define a mesh

    if min_pe is None:
        min_pe = 0.0

    all_pe = [ 0 for x in range(32) ]
    petot = 0.0
    # The index for PE(n) is the OpChannel Number (I think)
    for n in range(opflash.nOpDets()):
        pe = opflash.PE(n)
        ch = n%100
        petot += pe
        
        if pe>0:
            #print("ch[%d,%d] %.2f"%(n,ch,opflash.PE(n)))
            if ch<32:
                all_pe[ch] = pe
    #print(petot,all_pe)
        
    if max_pe is None:
        max_pe = max(all_pe)
        max_pe = max(max_pe,1.0)
    
    for ipmt in range(32):
        pe = all_pe[ipmt]

        if pe < pe_draw_threshold:
            continue
        
        value = (pe-min_pe)/(max_pe-min_pe)
        value = min( value, 1.0 )
        value = max( value, 0 )

        # how to interpret opflash PE(n) indexing
        if not use_opdet_index:
            # default: interpret as OpChannel
            opchid = ipmt
            center = getPMTPosByOpChannel(ipmt, use_v4_geom=use_v4_geom)
            opdetid = getOpDetFromOpChannel(ipmt)
        else:
            # interpret indeex as (larsoft opdet index)
            opdetid = ipmt
            center = getPMTPosByOpDet(ipmt, use_v4_geom=use_v4_geom)
            opchid  = getOpChannelFromOpDet(ipmt)
            
        if xpos_by_time:
            t = opflash.Time()
            xpos = t*dv+x_offset
            recenter = [xpos,center[1],center[2]]
        else:
            recenter = [center[0]+x_offset,center[1],center[2]]
        
        mesh, outline = define_circle_mesh( recenter, pmt_radius_cm, value, nsteps=20, x_offset=x_offset, rgb_channel=rgb_channel )
        hovertext =  f"<b>OpChannel</b>: {opchid}<br>"
        hovertext += f"<b>OpDetID</b>: {opdetid}"
        mesh['hovertext'] = hovertext
        outline['hovertext'] = hovertext
        circles.append( mesh )
        circles.append( outline )
        
    return circles

def visualize_empty_opflash( pmt_radius_cm=15.2, use_v4_geom=True, use_opdet_index=False ):

    circles = []
    nsteps = 20
    # for ipmt in range(32):
    # we have to define a mesh
    
    for ipmt in range(32):
        pe = 0.0
        if use_opdet_index:
            opdetid = ipmt
            center = getPMTPosByOpDet(ipmt, use_v4_geom=use_v4_geom)
            opchid  = getOpChannelFromOpDet(ipmt)
        else:
            opchid = ipmt
            center = getPMTPosByOpChannel(ipmt, use_v4_geom=use_v4_geom)
            opdetid = getOpDetFromOpChannel(ipmt)

        mesh, outline = define_circle_mesh( center, pmt_radius_cm, pe, nsteps=20 )
        hovertext =  f"<b>OpChannel</b>: {opchid}<br>"
        hovertext += f"<b>OpDetID</b>: {opdetid}"
        mesh['hovertext'] = hovertext
        outline['hovertext'] = hovertext
        circles.append( mesh )
        circles.append( outline )
        
    return circles
