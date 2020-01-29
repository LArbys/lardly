# coordinates are in larsoft coordinates
pmtposmap = {
    26:[0.558, 55.249, 87.7605],
    25:[0.703, 55.249, 128.355],
    27:[0.665, 27.431, 51.1015],
    28:[0.658, -0.303, 173.743],
    29:[0.947, -28.576, 50.4745],
    31:[0.862, -56.615, 87.8695],
    30:[0.8211, -56.203, 128.179],
    20:[0.682, 54.646, 287.976],
    19:[0.913, 54.693, 328.212],
    22:[0.949, -0.829, 242.014],
    21:[1.014, -0.706, 373.839],
    24:[1.092, -56.261, 287.639],
    23:[1.451, -57.022, 328.341],
    14:[1.116, 55.771, 500.134],
    13:[1.226, 55.822, 540.929],
    16:[1.481, -0.875, 453.096],
    15:[1.448, -0.549, 585.284],
    18:[1.505, -56.323, 500.221],
    17:[1.479, -56.205, 540.616],
    8:[1.438, 55.8, 711.073],
    7:[1.559, 55.625, 751.884],
    10:[1.475, -0.051, 664.203],
    9:[1.795, -0.502, 796.208],
    12:[1.487, -56.408, 711.274],
    11:[1.495, -56.284, 751.905],
    1:[2.265, 55.822, 911.066],
    0:[2.458, 55.313, 951.861],
    2:[2.682, 27.607, 989.712],
    3:[1.923, -0.722, 865.598],
    4:[2.645, -28.625, 990.356],
    6:[2.041, -56.309, 911.939],
    5:[2.324, -56.514, 951.865],
    35:[-161.3,-28.201 + 20/2*2.54, 280.161],
    34:[-161.3,-27.994 + 20/2*2.54, 490.501],
    33:[-161.3,-28.100 + 20/2*2.54, 550.333],
    32:[-161.3,-27.755 + 20/2*2.54, 760.575],
}

def getPosFromID( id, origin_at_detcenter=False ):
    if id in pmtposmap:
        pos = [0,0,0]
        for i in range(3):
            pos[i] =  pmtposmap[id][i]
            if origin_at_detcenter:
                pos[i] -= getDetectorCenter()[i]
        return pos
    print "[ pylard.pmtpos ] did not find channel %d"%(id)
    return None

def getDetectorCenter():
    return [125.0,0.5*(-57.022+55.8),0.5*(990.356+51.1015)]

if __name__ == "__main__":
    print "FEMCH[36][3] = {",
    for ich in range(0,36):
        print "{",pmtposmap[ich][0],",",pmtposmap[ich][1],",",pmtposmap[ich][2],"}",
        if ich!=35:
            print ",",
        print "// FEMCH%02d"%(ich)
    print "};"
        
