from .pmtpos import pmtposmap
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
    
    i = np.ones( nsteps, dtype=np.int32)*nsteps # always points to center
    j = np.zeros( nsteps, dtype=np.int32 )
    k = np.zeros( nsteps, dtype=np.int32 )
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

def make_opdet_plot( opdet_values, x_offset=0.0, pmt_radius_cm=10.0 ):

    print(opdet_values)

    all_pe = [ 0.0 for x in range(32) ]
    max_pe = 0.0
    min_pe = 1.0e9
    for i in range(32):
        #if i < len(opdet_values):
        all_pe[i] = opdet_values[i]
        if all_pe[i]>max_pe:
            max_pe = all_pe[i]
        if all_pe[i]<min_pe:
            min_pe = all_pe[i]

    circles = []
    for ipmt in range(32):
        pe = all_pe[ipmt]
        value = (pe-min_pe)/(max_pe-min_pe)
        value = min( value, 1.0 )
        value = max( value, 0 )
        center = [pmtposmap[ipmt][0]+x_offset, pmtposmap[ipmt][1], pmtposmap[ipmt][2] ]
        mesh, outline = define_circle_mesh( center, pmt_radius_cm, value, nsteps=20 )
        circles.append( mesh )
        circles.append( outline )
        
    return circles
    
