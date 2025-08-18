import trimesh
import pyvista as pv
import numpy as np

class Shape:
    def __init__(self, mesh):
        self.mesh = mesh

    def to_pyvista_mesh(self):
        if self.mesh is None:
            return None
        faces = np.hstack((np.full((len(self.mesh.faces), 1), 3), self.mesh.faces))
        return pv.PolyData(self.mesh.vertices, faces)

    def translate(self, x, y, z):
        matrix = trimesh.transformations.translation_matrix([x, y, z])
        self.mesh.apply_transform(matrix)
        return self

    def rotate(self, angle, axis):
        # axis should be a normalized vector, e.g., [1, 0, 0] for X-axis
        matrix = trimesh.transformations.rotation_matrix(np.radians(angle), axis)
        self.mesh.apply_transform(matrix)
        return self

    def scale(self, x, y, z):
        matrix = trimesh.transformations.scale_matrix([x, y, z])
        self.mesh.apply_transform(matrix)
        return self

    def union(self, other_shape):
        combined_mesh = trimesh.boolean.union([self.mesh, other_shape.mesh])
        return Shape(combined_mesh)

    def subtract(self, other_shape):
        subtracted_mesh = trimesh.boolean.difference([self.mesh, other_shape.mesh])
        return Shape(subtracted_mesh)

class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def to_path(self):
        return trimesh.path.Path2D(
            vertices=[
                [self.x, self.y],
                [self.x + self.width, self.y],
                [self.x + self.width, self.y + self.height],
                [self.x, self.y + self.height],
                [self.x, self.y],
            ],
            entities=[
                trimesh.path.entities.Line([0, 1]),
                trimesh.path.entities.Line([1, 2]),
                trimesh.path.entities.Line([2, 3]),
                trimesh.path.entities.Line([3, 4]),
            ]
        )

    def extrude(self, height):
        path = self.to_path()
        mesh = path.extrude(height)
        return Box(mesh)

class Box(Shape):
    def __init__(self, mesh):
        super().__init__(mesh)

class Cube(Shape):
    def __init__(self, x, y, z, size):
        mesh = trimesh.creation.box(extents=[size, size, size], transform=trimesh.transformations.translation_matrix([x + size/2, y + size/2, z + size/2]))
        super().__init__(mesh)

class Sphere(Shape):
    def __init__(self, x, y, z, radius):
        mesh = trimesh.creation.icosphere(radius=radius)
        mesh.apply_translation([x, y, z])
        super().__init__(mesh)

class Cylinder(Shape):
    def __init__(self, x, y, z, radius, height):
        mesh = trimesh.creation.cylinder(radius=radius, height=height)
        mesh.apply_translation([x, y, z + height/2]) # Center the cylinder base at (x,y,z)
        super().__init__(mesh)