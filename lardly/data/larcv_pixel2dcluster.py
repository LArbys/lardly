import os,sys
import numpy as np
from larcv import larcv

def visualize_larcv_pixel2dcluster(cluster,meta,flip_tick=False):
    npixels = cluster.size()
    pixnp = np.zeros( (npixels,2) )
    for ipt in range(npixels):
        col = cluster[ipt].X()
        row = cluster[ipt].Y()
        wire = meta.pos_x(col)        
        if flip_tick:
            tick = meta.min_y() - meta.pixel_height()*row
        else:
            tick = meta.pos_y(row)

        pixnp[ipt,0] = wire
        pixnp[ipt,1] = tick

    trace = {
        "type":"scatter",
        "x":pixnp[:,0],
        "y":pixnp[:,1],
        "opacity":0.8,
        "mode":"marker",
        "marker":{"color":"rgb(255,255,255)",
                  "size":4},
    }

    return trace
