import cadquery as cq
import pyvista as pv
import io

class Shape:
    def __init__(self, cq_object):
        self.cq_object = cq_object

    def to_pyvista_mesh(self):
        if not self.cq_object:
            return None

        # Export to STL in memory and load with PyVista
        stl_buffer = io.BytesIO()
        cq.exporters.export(self.cq_object, stl_buffer, "STL")
        stl_buffer.seek(0)
        return pv.read(stl_buffer)

    def translate(self, x, y, z):
        self.cq_object = self.cq_object.translate((x, y, z))
        return self

    def rotate(self, angle, ax, ay, az):
        # cadquery rotate takes an axis and an angle in degrees
        # It rotates around the origin by default. For rotation around a point,
        # one would translate to origin, rotate, then translate back.
        # For simplicity, assuming rotation around origin for now.
        self.cq_object = self.cq_object.rotate((0,0,0), (ax, ay, az), angle)
        return self

    def scale(self, x, y, z):
        # cadquery scale is uniform. For non-uniform, one would need to apply
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
        # Create a 2D workplane and then extrude
        # CadQuery workplane is centered at (0,0) by default, so we need to adjust
        # the rectangle definition to be relative to the workplane.
        # For a rectangle at (x,y) with width, height, its center is (x+w/2, y+h/2)
        # We create a workplane at (x+w/2, y+h/2) and then draw a centered rectangle.
        workplane = cq.Workplane("XY").center(self.x + self.width/2, self.y + self.height/2)
        rect_2d = workplane.rect(self.width, self.height)
        extruded_cq_object = rect_2d.extrude(height)
        return Shape(extruded_cq_object)

class Cube(Shape):
    def __init__(self, x, y, z, size):
        # CadQuery box is centered by default. We need to translate it.
        cq_box = cq.Workplane("XY").box(size, size, size).translate((x + size/2, y + size/2, z + size/2))
        super().__init__(cq_box)

class Sphere(Shape):
    def __init__(self, x, y, z, radius):
        # CadQuery sphere is centered by default. We need to translate it.
        cq_sphere = cq.Workplane("XY").sphere(radius).translate((x, y, z))
        super().__init__(cq_sphere)

class Cylinder(Shape):
    def __init__(self, x, y, z, radius, height):
        # CadQuery cylinder is centered by default. We need to translate it.
        # It's created along the Z-axis.
        cq_cylinder = cq.Workplane("XY").cylinder(height, radius).translate((x, y, z + height/2))
        super().__init__(cq_cylinder)