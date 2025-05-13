"""
Detector outline utilities

This module provides utilities for creating detector outlines for visualization.
"""
from typing import List, Tuple, Dict, Any
import numpy as np
import plotly.graph_objects as go

class DetectorOutline:
    """
    Class for creating and manipulating detector outlines
    
    This class generates the geometric representation of detector components
    for visualization.
    """
    
    def __init__(self):
        """Initialize with TPC dimensions"""
        # TPC dimensions [min, max] for each axis
        self.tpc = [
            [0.0, 256.0],      # x-axis
            [-117.0, 117.0],   # y-axis
            [0.0, 1036.0]      # z-axis
        ]
        
        # Tick range and trigger tick
        self.dettick_range = [0.0, 9600.0]
        self.tpctrig_tick = 3200.0
        
        # Calculate detector x range based on tick range
        self.detx_range = [
            (self.dettick_range[0] - self.tpctrig_tick) * 0.5 * 0.111,
            (self.dettick_range[1] - self.tpctrig_tick) * 0.5 * 0.111
        ]

        # Define corner points of the TPC
        # Top face corners (constant y)
        self.top_pts = [
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]]
        ]
        
        # Bottom face corners (constant y)
        self.bot_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]]
        ]
        
        # Upstream face corners (constant z)
        self.up_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]]
        ]
        
        # Downstream face corners (constant z)
        self.down_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]]
        ]

    def get_lines(self, color: Tuple[int, int, int] = (255, 255, 255)) -> List[Dict[str, Any]]:
        """
        Get line traces for the detector outline
        
        Args:
            color: RGB color for the lines (0-255 scale)
            
        Returns:
            List of Plotly trace dictionaries for the detector outline
        """
        # Initialize coordinate arrays
        Xe = []
        Ye = []
        Ze = []

        # Add each face boundary to the coordinate arrays
        for boundary in [self.top_pts, self.bot_pts, self.up_pts, self.down_pts]:
            for pt in boundary:
                Xe.append(pt[0])
                Ye.append(pt[1])
                Ze.append(pt[2])
            # Add None to create a break in the line
            Xe.append(None)
            Ye.append(None)
            Ze.append(None)
        
        # Define the line trace
        lines = {
            "type": "scatter3d",
            "x": Xe,
            "y": Ye,
            "z": Ze,
            "mode": "lines",
            "name": "Detector Outline",
            "line": {"color": f"rgb({color[0]},{color[1]},{color[2]})", "width": 5},
        }
        
        return [lines]

class EVDImageOutline(DetectorOutline):
    """
    Extended detector outline for the Event Display
    
    This class extends the DetectorOutline with additional dimensions
    suitable for event display visualization.
    """
    
    def __init__(self):
        """Initialize with extended dimensions"""
        self.tpc = [
            [-800 * 0.5 * 0.111, 5248 * 0.5 * 0.111],  # x-axis
            [-117.0, 117.0],                         # y-axis
            [0.0, 1036.0]                            # z-axis
        ]
        
        self.dettick_range = [0.0, 9600.0]
        self.tpctrig_tick = 3200.0
        self.detx_range = [
            (self.dettick_range[0] - self.tpctrig_tick) * 0.5 * 0.111,
            (self.dettick_range[1] - self.tpctrig_tick) * 0.5 * 0.111
        ]

        # Define corner points as in the parent class
        self.top_pts = [
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]]
        ]
        
        self.bot_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]]
        ]
        
        self.up_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][0]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][0]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][0]]
        ]
        
        self.down_pts = [
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][1], self.tpc[1][0], self.tpc[2][1]],
            [self.tpc[0][1], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][1], self.tpc[2][1]],
            [self.tpc[0][0], self.tpc[1][0], self.tpc[2][1]]
        ]

class CRTOutline:
    """
    Cosmic Ray Tagger (CRT) outline
    
    This class generates the geometrical representation of the CRT components.
    """
    
    def __init__(self):
        """Initialize with CRT panel coordinates"""
        # Top panel coordinates
        self.top_panel = [
            (-50.0, 618.0, -100.0),
            (480.0, 618.0, -100.0),
            (480.0, 618.0, 810.0),
            (310.0, 618.0, 810.0),
            (310.0, 618.0, 1190.0),
            (-250.0, 618.0, 1190.0),
            (-250.0, 618.0, 450.0),
            (-50.0, 618.0, 450.0),
            (-50.0, 618.0, -100.0)
        ]
        
        # Bottom panel coordinates
        self.bot_panel = [
            (-120.0, -261.0, 260.0),
            (400.0, -261.0, 260.0),
            (400.0, -261.0, 600.0),
            (50.0, -261.0, 600.0),
            (50.0, -261.0, 780.0),
            (-120.0, -261.0, 780.0),
            (-120.0, -261.0, 260.0)
        ]
        
        # Feedthrough panel coordinates
        self.feedthru_panel = [
            (-142.5, -240.0, -100.0),
            (-142.5, 140.0, -100.0),
            (-142.5, 140.0, 1150.0),
            (-142.5, -240.0, 1150.0),
            (-142.5, -240.0, -100.0)
        ]
        
        # Pipe panel coordinates
        self.pipe_panel = [
            (393.0, -240.0, -100.0),
            (393.0, 280.0, -100.0),
            (393.0, 280.0, 1150.0),
            (393.0, -240.0, 1150.0),
            (393.0, -240.0, -100.0)
        ]
                                
    def get_lines(self, color=None) -> List[Dict[str, Any]]:
        """
        Get line traces for the CRT outline
        
        Args:
            color: Optional color for the lines, default is teal
            
        Returns:
            List of Plotly trace dictionaries for the CRT outline
        """
        lines_v = []

        if color is None:
            color = "rgb(0,150,150)"
        
        # Create a trace for each panel
        for panel in [self.top_panel, self.bot_panel, self.feedthru_panel, self.pipe_panel]:
            Xe = []
            Ye = []
            Ze = []

            # Add each point to the coordinate arrays
            for pt in panel:
                Xe.append(pt[0])
                Ye.append(pt[1])
                Ze.append(pt[2])
            
            # Define the line trace
            lines = {
                "type": "scatter3d",
                "x": Xe,
                "y": Ye,
                "z": Ze,
                "mode": "lines",
                "name": "CRT Outline",
                "line": {"color": color, "width": 5},
            }

            lines_v.append(lines)
        
        return lines_v

def get_tpc_boundary_plot(cryoid=0, tpcid=0, color=(0, 0, 0), use_tick_dimensions=False):
    """
    Get TPC boundary plot using larlite geometry
    
    Args:
        cryoid: Cryostat ID
        tpcid: TPC ID
        color: RGB color for the lines
        use_tick_dimensions: Whether to use tick dimensions
        
    Returns:
        Plotly trace dictionary for the TPC boundary
    """
    try:
        import ROOT as rt
        from larlite import larlite
        from larlite import larutil
    except ImportError:
        raise ValueError("Could not load ROOT, larlite, or larlite::larutil")

    detid = larutil.LArUtilConfig.Detector()

    if detid == larlite.geo.kDetIdMax:
        print("Detector Configuration not set")
        print("Call larutil.LArUtilConfig.SetDetector( DetId_t )")
        return None

    # Get TPC boundaries
    minbound = rt.TVector3()
    maxbound = rt.TVector3()
    larlite.larutil.Geometry.GetME().TPCBoundaries(minbound, maxbound, tpcid, cryoid)
    
    # Adjust for tick dimensions if requested
    if use_tick_dimensions:
        from ROOT import larutil
        nticks = float(larutil.DetectorProperties.GetME().ReadOutWindowSize())
        tpcdriftdir = larlite.larutil.Geometry.GetME().TPCDriftDir(tpcid, cryoid)
        if tpcdriftdir[0] > 0:
            minbound[0] = 0
            maxbound[0] = nticks
        else:
            minbound[0] = -nticks
            maxbound[0] = 0

    # Define corner points for each face
    top_pts = [
        [minbound[0], maxbound[1], minbound[2]],
        [maxbound[0], maxbound[1], minbound[2]],
        [maxbound[0], maxbound[1], maxbound[2]],
        [minbound[0], maxbound[1], maxbound[2]],
        [minbound[0], maxbound[1], minbound[2]]
    ]
    
    bot_pts = [
        [minbound[0], minbound[1], minbound[2]],
        [maxbound[0], minbound[1], minbound[2]],
        [maxbound[0], minbound[1], maxbound[2]],
        [minbound[0], minbound[1], maxbound[2]],
        [minbound[0], minbound[1], minbound[2]]
    ]
    
    up_pts = [
        [minbound[0], minbound[1], minbound[2]],
        [maxbound[0], minbound[1], minbound[2]],
        [maxbound[0], maxbound[1], minbound[2]],
        [minbound[0], maxbound[1], minbound[2]],
        [minbound[0], minbound[1], minbound[2]]
    ]
    
    down_pts = [
        [minbound[0], minbound[1], maxbound[2]],
        [maxbound[0], minbound[1], maxbound[2]],
        [maxbound[0], maxbound[1], maxbound[2]],
        [minbound[0], maxbound[1], maxbound[2]],
        [minbound[0], minbound[1], maxbound[2]]
    ]        

    # Initialize coordinate arrays
    Xe = []
    Ye = []
    Ze = []

    # Add each face boundary to the coordinate arrays
    for boundary in [top_pts, bot_pts, up_pts, down_pts]:
        for pt in boundary:
            Xe.append(pt[0])
            Ye.append(pt[1])
            Ze.append(pt[2])
        Xe.append(None)
        Ye.append(None)
        Ze.append(None)
        
    # Define the line trace
    lines = {
        "type": "scatter3d",
        "x": Xe,
        "y": Ye,
        "z": Ze,
        "mode": "lines",
        "name": f"TPC({cryoid},{tpcid})",
        "line": {"color": f"rgb({color[0]},{color[1]},{color[2]})", "width": 5},
    }

    return lines