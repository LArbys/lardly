import os,sys
import numpy as np
from larcv import larcv

def visualize_larcv_pixel2dcluster(cluster,meta):
    npixels = cluster.size()
    pixnp = np.zeros( (npixels,2) )
    for ipt in range(npixels):
        col = cluster[ipt].X()
        row = cluster[ipt].Y()
        wire = meta.pos_x(col)
        tick = meta.pos_y(row)

        pixnp[ipt,0] = wire
        pixnp[ipt,1] = tick

    trace = {
        "type":"scatter",
        "x":pixnp[:,0],
        "y":pixnp[:,1],
        "opacity":0.25,
        "mode":"marker",
        "marker":{"color":"rgb(255,255,255)",
                  "size":4,
                  "symbol":"square-open"}
    }

    return trace
