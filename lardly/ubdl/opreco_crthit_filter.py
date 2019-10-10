from __future__ import print_function
import os,sys
from math import fabs

def filter_crthits_wopreco( event_opreco_beam, event_opreco_cosmic, event_crthit, max_dt_usec=10.0 ):
    # crt hit must be close in time to an opreco
    filtered = []
    for ihit in range(event_crthit.size()):
        crthit = event_crthit.at(ihit)
        t_usec = crthit.ts2_ns*0.001

        mindt = 1e6
        minidx = -1
        for opreco_v in [event_opreco_beam,event_opreco_cosmic]:
            for iopflash in range(opreco_v.size()):
                opflash = opreco_v.at(iopflash)
                dt = fabs(opflash.Time()-t_usec)
                if dt < mindt:
                    minidx = iopflash
                    mindt = dt
        if mindt<max_dt_usec:
            filtered.append( crthit )
    print("filtered crthits by opreco: %d of %d pass"%(len(filtered),event_crthit.size()))
    return filtered
