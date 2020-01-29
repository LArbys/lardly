import os,sys

class CRTOutline:
    def __init__(self):

        self.top_panel = [ ( -50.0, 618.0, -100.0),
                           ( 480.0, 618.0, -100.0),
                           ( 480.0, 618.0,  810.0),
                           ( 310.0, 618.0,  810.0),
                           ( 310.0, 618.0, 1190.0),
                           (-250.0, 618.0, 1190.0),
                           (-250.0, 618.0,  450.0),
                           ( -50.0, 618.0,  450.0),
                           ( -50.0, 618.0, -100.0) ]
        self.bot_panel = [ ( -120.0, -261.0, 260.0 ),
                           (  400.0, -261.0, 260.0 ),
                           (  400.0, -261.0, 600.0 ),
                           (   50.0, -261.0, 600.0 ),
                           (   50.0, -261.0, 780.0 ),
                           ( -120.0, -261.0, 780.0 ),
                           ( -120.0, -261.0, 260.0 ) ]

        self.feedthru_panel = [ (-142.5, -240.0, -100.0),
                                (-142.5,  140.0, -100.0),
                                (-142.5,  140.0, 1150.0),
                                (-142.5, -240.0, 1150.0),
                                (-142.5, -240.0, -100.0) ]
        
        self.pipe_panel = [ (393.0, -240.0, -100.0),
                            (393.0,  280.0, -100.0),
                            (393.0,  280.0, 1150.0),
                            (393.0, -240.0, 1150.0),
                            (393.0, -240.0, -100.0) ]
                                
    def getlines(self,color=None):
        lines_v = []

        if color is None:
            color = "rgb(0,150,150)"
        
        for panel in [ self.top_panel, self.bot_panel, self.feedthru_panel, self.pipe_panel ]:

            Xe = []
            Ye = []
            Ze = []

            for ipt, pt in enumerate(panel):
                Xe.append( pt[0] )
                Ye.append( pt[1] )
                Ze.append( pt[2] )
        
        
            # define the lines to be plotted
            lines = {
                "type": "scatter3d",
                "x": Xe,
                "y": Ye,
                "z": Ze,
                "mode": "lines",
                "name": "",
                "line": {"color":color, "width": 5},
            }

            lines_v.append(lines)
        
        return lines_v

