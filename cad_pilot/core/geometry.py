import cadquery as cq
import pyvista as pv
import io
import tempfile
import os

class Shape:
    def __init__(self, cq_solid):
        # cq_solid should be a cadquery.Shape (Solid) object
        self.cq_object = cq_solid

    def to_pyvista_mesh(self):
        if not self.cq_object:
            return None

        # Create a temporary file for STL export
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Export to STL file and load with PyVista
            cq.exporters.export(self.cq_object, temp_path, "STL")
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
        # cadquery Shape scale is uniform. For non-uniform, one would need to apply
        # a transformation matrix or rebuild the object. For simplicity, we'll
        # apply a uniform scale based on the first factor.
        if not (x == y == z):
            print("Warning: CadQuery uniform scaling applied. Non-uniform scaling is complex and not fully supported yet.")
        self.cq_object = self.cq_object.scale(x) # Apply uniform scale
        return self

    def union(self, other_shape):
        combined_cq_object = self.cq_object.union(other_shape.cq_object)
        return Shape(combined_cq_object)

    def subtract(self, other_shape):
        cut_cq_object = self.cq_object.cut(other_shape.cq_object)
        return Shape(cut_cq_object)

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def extrude(self, height):
        # Create a 2D workplane and then extrude to get a Solid
        workplane = cq.Workplane("XY").center(self.x + self.width/2, self.y + self.height/2)
        rect_2d = workplane.rect(self.width, self.height)
        extruded_solid = rect_2d.extrude(height).val() # Get the Solid object
        return Shape(extruded_solid)

class Cube(Shape):
    def __init__(self, x, y, z, size):
        # Create a Workplane, make the box, and get the Solid object
        # First create the box, then translate it
        cq_box = cq.Workplane("XY").box(size, size, size)
        cq_box_solid = cq_box.val()  # Get the Solid object first
        # Now translate the solid object
        cq_box_solid = cq_box_solid.translate((x + size/2, y + size/2, z + size/2))
        super().__init__(cq_box_solid)

class Sphere(Shape):
    def __init__(self, x, y, z, radius):
        # Create a Workplane, make the sphere, and get the Solid object
        cq_sphere = cq.Workplane("XY").sphere(radius)
        cq_sphere_solid = cq_sphere.val()  # Get the Solid object first
        # Now translate the solid object
        cq_sphere_solid = cq_sphere_solid.translate((x, y, z))
        super().__init__(cq_sphere_solid)

class Cylinder(Shape):
    def __init__(self, x, y, z, radius, height):
        # Create a Workplane, make the cylinder, and get the Solid object
        # It's created along the Z-axis.
        cq_cylinder = cq.Workplane("XY").cylinder(height, radius)
        cq_cylinder_solid = cq_cylinder.val()  # Get the Solid object first
        # Now translate the solid object
        cq_cylinder_solid = cq_cylinder_solid.translate((x, y, z + height/2))
        super().__init__(cq_cylinder_solid)
