from __future__ import print_function
import os,sys
import numpy as np
import plotly.graph_objs as go

def visualize_larcv_image2d( image2d, minz=0.0, maxz=200.0, reverse_ticks=False, downsample=None, dump_metainfo=False ):
    from larcv import larcv
    larcv.load_pyutil()
    
    meta = image2d.meta()
    if dump_metainfo:
        print("meta: ",meta.dump())
    imgnp = np.transpose( larcv.as_ndarray( image2d ), (1,0) )
    if meta.plane() in [0,1]:
        imgnp = imgnp[:,0:2400]
        maxx = 2400.0
    else:
        maxx = meta.max_x()
    #print("image shape: ",imgnp.shape," maxx=",maxx)
    xaxis = np.linspace( meta.min_x(), maxx, endpoint=False, num=int(maxx/meta.pixel_width()) )
    yaxis = np.linspace( meta.min_y(), meta.max_y(), endpoint=False, num=meta.rows() )
    #print(type(imgnp),type(xaxis),type(yaxis))

    imgnp[ imgnp<minz ] = 0
    imgnp[ imgnp>maxz ] = maxz

    if reverse_ticks:
        imgnp = np.flip( imgnp, axis=0 )

    heatmap = {
        #"type":"heatmapgl",
        "type":"heatmap",
        "z":imgnp,
        "x":xaxis,
        "y":yaxis,
        "colorscale":"Jet",
        }
    return heatmap
