import os,sys

def visualize3d_larlite_shower( larlite_shower ):
    shr = larlite_shower
    shrlen = shr.Length()
    shower_trace = {
        "type":"cone",
        "x":[shr.ShowerStart().X()],
        "y":[shr.ShowerStart().Y()],
        "z":[shr.ShowerStart().Z()],
        "u":[shrlen*shr.Direction().X()],
        "v":[shrlen*shr.Direction().Y()],
        "w":[shrlen*shr.Direction().Z()],
        "anchor":"tip",
        "sizemode":"absolute",
        }
    return shower_trace
