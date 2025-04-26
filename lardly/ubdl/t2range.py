import os
import numpy as np
import ROOT as rt
from larlite import larutil
from math import sqrt

class T2Range:
    def __init__(self):
        # load range file, make inverse spline
        self.rangefile_path = os.environ['LARFLOW_BASEDIR']+'/larflow/Reco/data/Proton_Muon_Range_dEdx_LAr_TSplines.root'
        self.rangefile = rt.TFile( self.rangefile_path, 'open' )

        proton_r2t = self.rangefile.Get("sProtonRange2T")
        muon_r2t = self.rangefile.Get("sMuonRange2T")

        # make graph between 0 to 10 meters at 1 cm increments
        self.gproton = rt.TGraph(1000)
        self.gmuon   = rt.TGraph(1000)
        for i in range(0,1000):
            r = i*1.0
            ke_p = 0.0
            ke_mu = 0.0
            if i>0:
                ke_p  = proton_r2t.Eval(r)
                ke_mu = muon_r2t.Eval(r)
            self.gproton.SetPoint(i,ke_p,r)
            self.gmuon.SetPoint(i,ke_mu,r)
        self.sproton = rt.TSpline3( "sProtonT2Range", self.gproton )
        self.smuon   = rt.TSpline3( "sMuonT2Range", self.gmuon )

    def get_range_muon( self, T_MeV ):
        return self.smuon.Eval( T_MeV )

    def get_range_proton( self, T_MeV):
        return self.sproton.Eval( T_MeV )

__t2range_util = T2Range()

def get_t2range_util():
    global __t2range_util
    return __t2range_util
