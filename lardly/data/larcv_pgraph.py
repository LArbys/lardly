from __future__ import print_function
import os,sys
import numpy as np
from larcv import larcv
larcv.load_pyutil()
import plotly.graph_objs as go

def visualize_larcv_pgraph( pgraph ):
    npoints = pgraph.NumParticles()
    xyz = np.zeros( (npoints,3 ) )
    for ipt in range(npoints):
        xyz[ipt,0] = pgraph.ParticleArray().at(ipt).X()
        xyz[ipt,1] = pgraph.ParticleArray().at(ipt).Y()
        xyz[ipt,2] = pgraph.ParticleArray().at(ipt).Z()

    points = {
        "type":"scatter3d",
        "x": xyz[:,0],
        "y": xyz[:,1],
        "z": xyz[:,2],
        'mode': 'markers',
        'marker': {'size': 4},
        "name":"",
        "line":{"color":"rgb(0,0,255)","width":2},
    }

    return points
