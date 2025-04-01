from __future__ import print_function
import os,sys
from ..ubdl.pmtpos import getPMTPosByOpChannel,getPMTPosByOpDet
import numpy as np
from plotly import graph_objects as go

def define_circle_mesh( center, radius, value, nsteps=20, color=None, outline_color=None ):

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
        color='rgb(%d,0,0)'%( 54+int(value*200) )

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
                                  use_v4_geom=True, use_opdet_index=True ):

    circles = []
    nsteps = 20
    # for ipmt in xrange(32):
    # we have to define a mesh

    if min_pe is None:
        min_pe = 0.0

    all_pe = [ 0 for x in range(32) ]
    petot = 0.0
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
        value = (pe-min_pe)/(max_pe-min_pe)
        value = min( value, 1.0 )
        value = max( value, 0 )
        if use_opdet_index:
            center = getPMTPosByOpDet(ipmt, use_v4_geom=use_v4_geom)
        else:
            center = getPMTPosByOpChannel(ipmt, use_v4_geom=use_v4_geom)
        #center = [pmtposmap[ipmt][0]+x_offset, pmtposmap[ipmt][1], pmtposmap[ipmt][2] ]
        mesh, outline = define_circle_mesh( center, pmt_radius_cm, value, nsteps=20 )
        circles.append( mesh )
        circles.append( outline )
        
    return circles

def visualize_empty_opflash( pmt_radius_cm=15.2, use_v4_geom=True, use_opdet_index=True ):

    circles = []
    nsteps = 20
    # for ipmt in range(32):
    # we have to define a mesh
    
    for ipmt in range(32):
        pe = 0.0
        if use_opdet_index:
            center = getPMTPosByOpDet(ipmt, use_v4_geom=use_v4_geom)
        else:
            center = getPMTPosByOpChannel(ipmt, use_v4_geom=use_v4_geom)
        mesh, outline = define_circle_mesh( center, pmt_radius_cm, pe, nsteps=20 )
        circles.append( mesh )
        circles.append( outline )
        
    return circles
