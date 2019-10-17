from __future__ import print_function
import os,sys

import ROOT as rt
from larlite import larlite
from larcv import larcv
from ublarcvapp import ublarcvapp

from ..data import visualize2d_larcv_pgraph
from ..data import visualize_larcv_image2d

"""list of filetypes that can form a complete set"""
DLEVENT_FILESETS = [ {"larcv":["supera","vertex-larcv"],
                      "larlite":["tracker-larlite"],
                      "tickbackward":[True,True],
                      "larcv-products":[("image2d:wire"),
                                        ("pgraph:test","pixel2d:test_super","pixel2d:dlshr","partroi:croimerge_clip_union") ]} ]
                      

class DLEvent:
    """class is responsible for loading files for DL event and providing collection of plotly/dash traces for plotting"""
    
    def __init__(self, file_folder):

        self.larcv_filetypes = [""]
        
        fset = self._parse_file_folder(file_folder)
        print("[fileset found]")        
        for ll,flist in fset.items():
            print(" {}:".format(ll))
            for fname in flist:
                print("    {}".format(fname))

        self._load_io_managers(fset)


    def _parse_file_folder(self,file_folder):
        """ looks within folder. attempts to find the files we need to assemble the event"""
        flist = os.listdir(file_folder)

        for fset in DLEVENT_FILESETS:

            # gather the files
            foundset = {"larcv":[],"larlite":[],"tickbackward":[]}
            
            # look for this fileset
            complete = True
            for ll in ["larlite","larcv"]:
                for itype,ftype in enumerate(fset[ll]):
                    found = False
                    for fname in flist:
                        if ftype in fname:
                            found = True
                            foundset[ll].append( file_folder+"/"+fname )
                            if ll=="larcv":
                                foundset["tickbackward"].append( fset["tickbackward"][itype] )
                        if found:
                            break
                    if not found:
                        complete = False
                        break
                if not complete:
                    break
            if complete:
                print("complete set found")
                return foundset
        return None
                
    def _load_io_managers(self,fileset):
        self._lcvio = larcv.IOManager(larcv.IOManager.kREAD,"ioforward",larcv.IOManager.kTickForward)
        self._lcvio_backward = larcv.IOManager(larcv.IOManager.kREAD,"ioforward",larcv.IOManager.kTickBackward)
        self._llio  = larlite.storage_manager(larlite.storage_manager.kREAD)

        nlcvio = 0
        nlcvio_backward = 0
        nllio = 0

        for ifile,fname in enumerate(fileset["larcv"]):
            if fileset["tickbackward"][ifile]:
                self._lcvio_backward.add_in_file( fname )
                nlcvio_backward += 1
            else:
                self._lcvio.add_in_file( fname )
                nlcvio += 1

        for fname in fileset["larlite"]:
            self._llio.add_in_filename( fname )
            nllio += 1

        if nlcvio:
            self._lcvio.initialize()
        else:
            self._lcvio = None
            
        if nlcvio_backward:
            self._lcvio_backward.initialize()
        else:
            self._lcvio_backward = None
            
        if nllio:
            self._llio.open()
        else:
            self._llio = None

    def get_entry_data(self,ientry):
        
        if self._lcvio is not None:
            self._lcvio.read_entry(ientry)

        if self._lcvio_backward is not None:
            self._lcvio_backward.read_entry(ientry)

        if self._llio is not None:
            self._llio.go_to(ientry)

        
        traces2d = {0:[],1:[],2:[]}
        traces3d = []

        # 2D Images
        adc_v = self._lcvio_backward.get_data(larcv.kProductImage2D,"wire").Image2DArray()
        for p in range(3):
            traces2d[p].append( visualize_larcv_image2d( adc_v[p] ) )

        # vertices: 2d
        ev_pgraph = self._lcvio_backward.get_data( larcv.kProductPGraph,  "test" )
        ev_pclust = self._lcvio_backward.get_data( larcv.kProductPixel2D, "test_ctor" )
        
        pgraph_traces2d = visualize2d_larcv_pgraph( ev_pgraph, event_contour_pixels=ev_pclust )
        for p in range(3):
            traces2d[p] += pgraph_traces2d[p]

        return traces2d, traces3d
