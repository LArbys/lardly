import os,sys
import collada
import numpy as np
from collections import OrderedDict


class DetectorDisplay:
    def __init__(self, daefile="microboone_32pmts_nowires_cryostat.dae"):
        self.daefile = daefile
        self._load_geometry( self.daefile )

        self.default_colorscale =  [
            [0, "rgb(12,51,131)"],
            [0.25, "rgb(10,136,186)"],
            [0.5, "rgb(242,211,56)"],
            [0.75, "rgb(242,143,56)"],
            [1, "rgb(217,30,30)"],
        ]
        

    def _load_geometry( self, daefile ):
        # Make list of solids
        self.solids = self._read_daecollada( daefile )

        # generate the mesh and load 3D widget
        self.vertices, self.indices = self._flatten_solids( self.solids )

        self.lines = self._make_lines()

    def _read_daecollada( self, daefile ):
        try:
            geom = collada.Collada( daefile )
        except:
            raise RuntimeError("Could not read DAE/COLLADA file")
        
        solids = OrderedDict()
        mesh = collada.Collada( daefile )
        boundgeom = list(mesh.scene.objects('geometry'))
        for geom in boundgeom:
            solidname = geom.original.name.split("0x")[0]
            if solidname not in solids:
                solids[solidname] = {"vertices":[],"indices":[] }
                
            boundprimitives = list(geom.primitives())
            for boundprim in boundprimitives:
                triset = boundprim.triangleset()
                solids[solidname]["vertices"].append( triset.vertex )
                solids[solidname]["indices"].append( triset.vertex_index )

        return solids

    def _flatten_solids( self, solids ):
        vertices = []
        indices = []
        nvertices = 0
        for solid in solids:
            for n,(solid_vertices,solid_indices) in enumerate(zip(solids[solid]["vertices"],solids[solid]["indices"])):
                #print solid,"prim #%d, nvertices=%d, offset=%d" % ( n, len(solid_vertices),nvertices)
                #print solid_indices
                solid_indices_copy = np.copy( solid_indices )
                solid_indices_copy += nvertices
                nvertices += len(solid_vertices)
                vertices.append( solids[solid]["vertices"][n] )
                indices.append( solid_indices_copy )
        return np.concatenate(vertices), np.concatenate(indices)

    def _make_lines(self):
        tri_vertices = self.vertices[self.indices]
        Xe = []
        Ye = []
        Ze = []
        for T in tri_vertices:
            Xe += [T[k % 3][0] for k in range(4)] + [None]
            Ye += [T[k % 3][1] for k in range(4)] + [None]
            Ze += [T[k % 3][2] for k in range(4)] + [None]

        # define the lines to be plotted
        lines = {
            "type": "scatter3d",
            "x": Xe,
            "y": Ye,
            "z": Ze,
            "mode": "lines",
            "name": "",
            "line": {"color": "rgb(70,70,70)", "width": 1},
        }
        return lines

                
    def getmeshdata(self,
                    intensities=None,
                    colorscale="Viridis",
                    flatshading=False,
                    showscale=False,
                    plot_edges=False ):
        
        x = self.vertices[:,0]
        y = self.vertices[:,1]
        z = self.vertices[:,2]
        I = self.indices[:,0]
        J = self.indices[:,1]
        K = self.indices[:,2]

        if intensities is None:
            intensities = z

        if colorscale==None:
            colorscale = self.default_colorscale

        mesh = {
            "type": "mesh3d",
            "x": x,
            "y": y,
            "z": z,
            "colorscale": colorscale,
            "intensity": intensities,
            "flatshading": flatshading,
            "i": I,
            "j": J,
            "k": K,
            "name": "",
            "showscale": showscale,
            "lighting": {
                "ambient": 0.18,
                "diffuse": 1,
                "fresnel": 0.1,
                "specular": 1,
                "roughness": 0.1,
                "facenormalsepsilon": 1e-6,
                "vertexnormalsepsilon": 1e-12,
            },
            "lightposition": {"x": 100, "y": 200, "z": 0},
        }

        if showscale:
            mesh["colorbar"] = {"thickness": 20, "ticklen": 4, "len": 0.75}

        #return [mesh,self.lines]
        return [self.lines]
    #lines = create_plot_edges_lines(vertices, faces)
    #return [mesh, lines]
