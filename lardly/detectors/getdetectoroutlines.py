import os,sys
import numpy as np
from larlite import larlite

class DetectorOutlineFromLarlite:
    def __init__(self,detid):
        if detid not in [larlite.geo.kMicroBooNE,larlite.geo.kSBND,larlite.geo.kICARUS]:
            raise ValueError("detid=%d not implemented"%(detid))

        geo = larlite.larutil.Geometry.GetME(detid)
        
        self.tpc_dict = {} # (cryo,tpc,plane):tpc_traces
        ncryos = geo.Ncryostats()
        for icryo in range(ncryos):
            cryogeo = geo.GetCryostat(icryo)
            ntpcs = cryogeo.tpc_v.size()
            for itpc in range(ntpcs):
                #print("tpc[%d]"%(itpc))
                # the four faces
                tpcgeo = cryogeo.tpc_v.at(itpc)
                bounds = np.zeros((3,2))
                for i in range(3):
                    bounds[i,0] = tpcgeo.fBounds.at(0)(i)
                    bounds[i,1] = tpcgeo.fBounds.at(1)(i)
                #print(bounds)
                top_pts  = [ [bounds[0,0],bounds[1,1], bounds[2,0]],
                             [bounds[0,1],bounds[1,1], bounds[2,0]],
                             [bounds[0,1],bounds[1,1], bounds[2,1]],
                             [bounds[0,0],bounds[1,1], bounds[2,1]],
                             [bounds[0,0],bounds[1,1], bounds[2,0]] ]
                bot_pts  = [ [bounds[0,0],bounds[1,0], bounds[2,0]],
                             [bounds[0,1],bounds[1,0], bounds[2,0]],
                             [bounds[0,1],bounds[1,0], bounds[2,1]],
                             [bounds[0,0],bounds[1,0], bounds[2,1]],
                             [bounds[0,0],bounds[1,0], bounds[2,0]] ]
                up_pts   = [ [bounds[0,0],bounds[1,0], bounds[2,0]],
                             [bounds[0,1],bounds[1,0], bounds[2,0]],
                             [bounds[0,1],bounds[1,1], bounds[2,0]],
                             [bounds[0,0],bounds[1,1], bounds[2,0]],
                             [bounds[0,0],bounds[1,0], bounds[2,0]] ]
                down_pts = [ [bounds[0,0],bounds[1,0], bounds[2,1]],
                             [bounds[0,1],bounds[1,0], bounds[2,1]],
                             [bounds[0,1],bounds[1,1], bounds[2,1]],
                             [bounds[0,0],bounds[1,1], bounds[2,1]],
                             [bounds[0,0],bounds[1,0], bounds[2,1]] ]        
            
                Xe = []
                Ye = []
                Ze = []

                for boundary in [top_pts,bot_pts,up_pts,down_pts]:
                    for ipt, pt in enumerate(boundary):
                        Xe.append( pt[0] )
                        Ye.append( pt[1] )
                        Ze.append( pt[2] )
                Xe.append(None)
                Ye.append(None)
                Ze.append(None)
                lines = {
                    "type": "scatter3d",
                    "x": Xe,
                    "y": Ye,
                    "z": Ze,
                    "mode": "lines",
                    "name": "(%d,%d)"%(icryo,itpc),
                    "line": {"color": "rgb(0,0,0)", "width": 5},
                }
                self.tpc_dict[(icryo,itpc)] = lines


                
    def getlines(self,color=None,tpclist=[]):

        traces = []
        if len(tpclist)==0:
            for key,val in self.tpc_dict.items():
                traces.append(val)
        else:
            for key in tpclist:
                if key in self.tpc_dict:
                    traces.append( self.tpc_dict[key] )
                else:
                    print("LARDLY-WARNING: key=",key," not in list of (cryo,tpc) indices")

        if color is not None:
            for trace in traces:
                trace["line"]["color"] = "rgb(%d,%d,%d)"%color
                
        return traces

                
