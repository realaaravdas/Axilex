from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf, gp_Ax1, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE

import pyvista as pv
import numpy as np

class Shape:
    def __init__(self, occt_shape: TopoDS_Shape):
        self.occt_shape = occt_shape

    def to_pyvista_mesh(self):
        if not self.occt_shape:
            return None

        # Generate mesh from OCCT shape
        mesh_algo = BRepMesh_IncrementalMesh(self.occt_shape, 0.1) # Tolerance 0.1
        mesh_algo.Perform()

        vertices = []
        faces = []
        
        # Iterate through faces to get triangulation
        explorer = TopExp_Explorer(self.occt_shape, TopAbs_FACE)
        while explorer.More():
            face = explorer.Current()
            location = TopLoc_Location()
            # Get the triangulation of the face
            face_triangulation = BRep_Tool.Triangulation(face, location)
            if face_triangulation:
                trsf = location.Transformation()
                
                # Add vertices
                current_vertex_count = len(vertices)
                for i in range(1, face_triangulation.NbNodes() + 1):
                    p = face_triangulation.Node(i).Transformed(trsf)
                    vertices.append([p.X(), p.Y(), p.Z()])
                
                # Add faces (triangles)
                triangles = face_triangulation.Triangles()
                for i in range(1, triangles.Length() + 1):
                    t = triangles.Value(i)
                    n1, n2, n3 = t.Value(1), t.Value(2), t.Value(3)
                    faces.extend([3, n1 - 1 + current_vertex_count, n2 - 1 + current_vertex_count, n3 - 1 + current_vertex_count])
            explorer.Next()

        if not vertices:
            return None

        return pv.PolyData(np.array(vertices), np.array(faces))

    def translate(self, x, y, z):
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(x, y, z))
        builder = BRepBuilderAPI_Transform(self.occt_shape, trsf)
        builder.Perform()
        self.occt_shape = builder.Shape()
        return self

    def rotate(self, angle, ax, ay, az):
        # OCCT rotation requires an axis and an angle in radians
        # Assuming rotation around origin for simplicity, can be extended to arbitrary axis
        axis_dir = gp_Dir(ax, ay, az)
        axis = gp_Ax1(gp_Pnt(0, 0, 0), axis_dir)
        trsf = gp_Trsf()
        trsf.SetRotation(axis, np.radians(angle))
        builder = BRepBuilderAPI_Transform(self.occt_shape, trsf)
        builder.Perform()
        self.occt_shape = builder.Shape()
        return self

    def scale(self, x, y, z):
        # OCCT scaling is uniform around a point. For non-uniform scaling, more complex operations are needed.
        # For now, we'll apply uniform scaling based on the average of x, y, z
        # Or, if we want true non-uniform scaling, we'd need to decompose and re-build or use a more advanced transform.
        # For simplicity, let's assume uniform scaling for now, or apply it as a series of non-uniform transforms if possible.
        # OCCT's gp_Trsf.SetScale is uniform. For non-uniform, one might need to use affine transformations or more complex BRep operations.
        # Given the complexity, let's simplify: if x=y=z, use uniform scale. Otherwise, it's more involved.
        # For now, I'll implement a uniform scale based on the first factor, and note the limitation.
        if not (x == y == z):
            print("Warning: OCCT uniform scaling applied. Non-uniform scaling is complex and not fully supported yet.")
        
        trsf = gp_Trsf()
        trsf.SetScale(gp_Pnt(0,0,0), x) # Scale around origin
        builder = BRepBuilderAPI_Transform(self.occt_shape, trsf)
        builder.Perform()
        self.occt_shape = builder.Shape()
        return self

    def union(self, other_shape):
        fuser = BRepAlgoAPI_Fuse(self.occt_shape, other_shape.occt_shape)
        fuser.Perform()
        if not fuser.IsDone():
            raise RuntimeError("Boolean union failed.")
        return Shape(fuser.Shape())

    def subtract(self, other_shape):
        cutter = BRepAlgoAPI_Cut(self.occt_shape, other_shape.occt_shape)
        cutter.Perform()
        if not cutter.IsDone():
            raise RuntimeError("Boolean subtraction failed.")
        return Shape(cutter.Shape())

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def extrude(self, height):
        # Create a wire from the rectangle points
        from OCC.Core.GC import GC_MakeSegment
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace

        p1 = gp_Pnt(self.x, self.y, 0)
        p2 = gp_Pnt(self.x + self.width, self.y, 0)
        p3 = gp_Pnt(self.x + self.width, self.y + self.height, 0)
        p4 = gp_Pnt(self.x, self.y + self.height, 0)

        edge1 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p1, p2).Value()).Edge()
        edge2 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p2, p3).Value()).Edge()
        edge3 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p3, p4).Value()).Edge()
        edge4 = BRepBuilderAPI_MakeEdge(GC_MakeSegment(p4, p1).Value()).Edge()

        wire_builder = BRepBuilderAPI_MakeWire(edge1, edge2, edge3, edge4)
        if not wire_builder.IsDone():
            raise RuntimeError("Failed to make wire for extrusion.")
        wire = wire_builder.Wire()

        face_builder = BRepBuilderAPI_MakeFace(wire)
        if not face_builder.IsDone():
            raise RuntimeError("Failed to make face for extrusion.")
        face = face_builder.Face()

        # Extrude the face
        prism = BRepPrimAPI_MakePrism(face, gp_Vec(0, 0, height))
        prism.Perform()
        if not prism.IsDone():
            raise RuntimeError("Failed to extrude rectangle.")
        return Shape(prism.Shape())

class Cube(Shape):
    def __init__(self, x, y, z, size):
        # OCCT box is defined by two corner points
        p_min = gp_Pnt(x, y, z)
        p_max = gp_Pnt(x + size, y + size, z + size)
        occt_box = BRepPrimAPI_MakeBox(p_min, p_max).Shape()
        super().__init__(occt_box)

class Sphere(Shape):
    def __init__(self, x, y, z, radius):
        # OCCT sphere is defined by center and radius
        center = gp_Pnt(x, y, z)
        occt_sphere = BRepPrimAPI_MakeSphere(center, radius).Shape()
        super().__init__(occt_sphere)

class Cylinder(Shape):
    def __init__(self, x, y, z, radius, height):
        # OCCT cylinder is defined by axis, radius, and height
        # Default axis is Z-axis, centered at (x,y,z) for the base
        axis = gp_Ax1(gp_Pnt(x, y, z), gp_Dir(0, 0, 1)) # Base center at (x,y,z), along Z
        occt_cylinder = BRepPrimAPI_MakeCylinder(axis, radius, height).Shape()
        super().__init__(occt_cylinder)
