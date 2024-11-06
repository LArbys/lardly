import os,sys
import numpy as np

def visualize_pcaxis( llpca, color=None, idnum=0 ):
    pca_pts = np.zeros( (3,3) )
    for i in range(3):
        pca_pts[0,i] = llpca.getEigenVectors()[3][i]
        pca_pts[1,i] = llpca.getAvePosition()[i]
        pca_pts[2,i] = llpca.getEigenVectors()[4][i]

    # random color
    if color is None:
        rand = np.random.randint(low=0,high=255,size=3)
        pcacolor = "rgb(%d,%d,%d)"%(rand[0],rand[1],rand[2])
    else:
        pcacolor = color
        
    pca_plot = {
        "type":"scatter3d",
        "x":pca_pts[:,0],
        "y":pca_pts[:,1],
        "z":pca_pts[:,2],
        "mode":"lines",
        "name":"pca[%d]"%(idnum),
        "line":{"color":pcacolor,"width":2}
    }
    return pca_plot

def visualize_event_pcaxis( evpcaxis, color=None ):

    traces_v = []


    for icluster in range(evpcaxis.size()):
    
        # PCA-axis
        pca_plot = visualize_pcaxis( evpcaxis.at(icluster), color=color, idnum=icluster )
    
        traces_v.append( pca_plot )

    return traces_v
