import cadquery as cq
import pyvista as pv
import numpy as np
import tempfile
import os

class Shape:
    def __init__(self, cq_solid):
        # cq_solid should be a cadquery.Shape (Solid) object
        self.cq_object = cq_solid

    def to_pyvista_mesh(self):
        if not self.cq_object:
            return None

        # Create a temporary file for VTK export
        with tempfile.NamedTemporaryFile(suffix='.vtp', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Export to VTP file and load with PyVista
            cq.exporters.export(self.cq_object, temp_path, "VTP")
            mesh = pv.read(temp_path)
            return mesh
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def translate(self, x, y, z):
        self.cq_object = self.cq_object.translate((x, y, z))
        return self

    def rotate(self, angle, ax, ay, az):
        # cadquery Shape rotate takes an axis and an angle in degrees
        # It rotates around the origin by default. For rotation around a point,
        # one would translate to origin, rotate, then translate back.
        self.cq_object = self.cq_object.rotate((0,0,0), (ax, ay, az), angle)
        return self

    def scale(self, x, y, z):
        # CadQuery supports non-uniform scaling via a transformation matrix
        # Create a scaling matrix
        mat = cq.Matrix.from_factors((x, y, z))
        self.cq_object = self.cq_object.transform(mat)
        return self

    def union(self, other_shape):
        combined_cq_object = self.cq_object.union(other_shape.cq_object)
        return Shape(combined_cq_object)

    def subtract(self, other_shape):
        cut_cq_object = self.cq_object.cut(other_shape.cq_object)
        return Shape(cut_cq_object)

    def mirror(self, nx, ny, nz):
        mirror_plane = cq.Plane(origin=(0, 0, 0), normal=(nx, ny, nz))
        self.cq_object = self.cq_object.mirror(mirror_plane)
        return self

class Rectangle(Shape):
    def __init__(self, x, y, width, height):
        # Create a 2D workplane and then extrude to get a Solid
        workplane = cq.Workplane("XY").center(x + width/2, y + height/2)
        rect_2d = workplane.rect(width, height)
        super().__init__(rect_2d.val())

    def extrude(self, height):
        # Extrude the existing 2D rectangle to get a Solid
        extruded_solid = self.cq_object.extrude(height).val()
        return Shape(extruded_solid)

class Cube(Shape):
    def __init__(self, x, y, z, size):
        cq_box = cq.Workplane("XY").box(size, size, size).translate((x + size/2, y + size/2, z + size/2)).val()
        super().__init__(cq_box)

class Sphere(Shape):
    def __init__(self, x, y, z, radius):
        cq_sphere = cq.Workplane("XY").sphere(radius).translate((x, y, z)).val()
        super().__init__(cq_sphere)

class Cylinder(Shape):
    def __init__(self, x, y, z, radius, height):
        cq_cylinder = cq.Workplane("XY").cylinder(height, radius).translate((x, y, z + height/2)).val()
        super().__init__(cq_cylinder)

class Cone(Shape):
    def __init__(self, x, y, z, radius1, radius2, height):
        cq_cone = cq.Workplane("XY").cone(height, radius1, radius2)
        cq_cone_solid = cq_cone.val().translate((x, y, z + height/2))
        super().__init__(cq_cone_solid)
