from __future__ import print_function
import os,sys
import numpy as np
from larcv import larcv
larcv.load_pyutil()
import plotly.graph_objs as go
from .larcv_pixel2dcluster import visualize_larcv_pixel2dcluster

def visualize3d_larcv_pgraph( event_pgraph , color=None  ):
    if color is None:
        color = "rgb(0,0,255)"
    else:
        color = "rgb({},{},{})".format(color[0],color[1],color[2])
    nvertices = event_pgraph.PGraphArray().size()
    xyz = np.zeros( (nvertices,3 ) )
    hovertext = []
    for ipgraph in range(event_pgraph.PGraphArray().size()):
        pgraph = event_pgraph.PGraphArray().at(ipgraph)
        roi = pgraph.ParticleArray().at(0)
        xyz[ipgraph,0] = pgraph.ParticleArray().at(0).X()
        xyz[ipgraph,1] = pgraph.ParticleArray().at(0).Y()
        xyz[ipgraph,2] = pgraph.ParticleArray().at(0).Z()
        hovertext.append("vtx[{}]".format(ipgraph))

    points = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        'mode': 'markers',
        'marker': {'size': 3,'color':color},
        "hovertext":hovertext,
    }

    return [points]

def visualize2d_larcv_pgraph( event_pgraph, event_contour_pixels=None, color=None):
    if color is None:
        color = "rgb(255,165,0)"
    else:
        color = "rgb({},{},{})".format(color[0],color[1],color[2])
    import ROOT
    from ROOT import std
    from larlite import larutil

    traces2d = {0:[],1:[],2:[]}

    pgraph_v = event_pgraph.PGraphArray()
    vertex_np = np.zeros( (pgraph_v.size(),3,2) ) # vertex locations [vertex,plane,(row,col)]
    hovertext = []
    for vtx_idx in range(pgraph_v.size()):
        pgraph = pgraph_v[vtx_idx]
        nparticles = pgraph.NumParticles()
        nclusters  = pgraph.ClusterIndexArray().size()

        hovertext.append("vtx[{}]".format(vtx_idx))

        roi = pgraph.ParticleArray().at(0)
        vertex = std.vector("double")(3,0)
        vertex[0] = roi.X()
        vertex[1] = roi.Y()
        vertex[2] = roi.Z()

        vertex_tick = 3200 + roi.X()/larutil.LArProperties.GetME().DriftVelocity()/0.5

        #print("vertex[{}]: nparticle={} nclusters={} tick={}".format(vtx_idx,nparticles,nclusters,vertex_tick))

        for p in range(3):
            wire = larutil.Geometry.GetME().NearestWire( vertex, p )
            if wire<0:
                wire=0
            elif wire>=3456:
                wire=3455
            vertex_np[vtx_idx,p,0] = wire
            vertex_np[vtx_idx,p,1] = vertex_tick
            #print("vertex[{}] plane={} wire={}".format(vtx_idx,p,wire))

        if event_contour_pixels is not None:
            for iclust in range(pgraph.ClusterIndexArray().size()):
                clust_idx = pgraph.ClusterIndexArray().at(iclust)
                for p in range(3):
                    pixcluster = event_contour_pixels.Pixel2DClusterArray(p).at(clust_idx)
                    meta       = event_contour_pixels.ClusterMetaArray(p).at(clust_idx)
                    clust_trace = visualize_larcv_pixel2dcluster( pixcluster, meta, flip_tick=True )
                    traces2d[p].append(clust_trace)



    for p in range(3):
        vertex_trace = {
            "type":"scatter",
            "x": vertex_np[:,p,0],
            "y": vertex_np[:,p,1],
            'hovertext':hovertext,
            'mode': 'markers',
            'marker': {'size': 6,'color':color},
        }
        traces2d[p].append( vertex_trace )


    return traces2d
