from __future__ import print_function
import os,sys
from math import fabs

def filter_crthits_wopreco( event_opreco_beam, event_opreco_cosmic, event_crthit, max_dt_usec=1.5, verbose=False ):
    # crt hit must be close in time to an opreco
    filtered = []
    nopflash_matched = {}
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
        if verbose:
            print("[filter_crthits_wopreco] crthit[%d] min dt=%.1f opflash[%d]"%(ihit,mindt,minidx))
        if mindt<max_dt_usec:
            filtered.append( crthit )
            if minidx not in nopflash_matched:
                nopflash_matched[minidx] = 0
            nopflash_matched[minidx] += 1
            
    print("filtered crthits by opreco: %d of %d pass"%(len(filtered),event_crthit.size()))
    if verbose:
        ophits_with_matches = nopflash_matched.keys()
        ophits_with_matches.sort()
        for iopflash in ophits_with_matches:
            print("  ophit[%d] %d matches"%(iopflash,nopflash_matched[iopflash]))
    return filtered
