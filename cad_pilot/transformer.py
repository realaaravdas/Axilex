from lark import Transformer, Tree, Token
from .core.geometry import Rectangle, Cube, Sphere, Cylinder, Cone, Shape
from .core.scene import Scene
import cadquery as cq
import warnings

class ConstraintError(Exception):
    """Raised when a constraint cannot be satisfied"""
    pass

class GeometryError(Exception):
    """Raised when geometry operations are invalid"""
    pass

class ToleranceError(Exception):
    """Raised when tolerance specifications are invalid"""
    pass

class CadTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.modules = {}
        self.object_stack = [] # To handle nested transformations and boolean operations
        self.named_objects = {} # To store objects by their assigned names
        self.constraints = []  # Store constraints for validation
        self.tolerances = {}  # Store tolerance specifications
        self.fixed_objects = set()  # Track fixed objects

    def _push_object(self, obj, name=None):
        self.object_stack.append(obj)
        self.scene.set_current_object(obj)
        if name:
            self.named_objects[name] = obj

    def _pop_object(self):
        if self.object_stack:
            return self.object_stack.pop()
        return None

    def _get_current_object(self):
        if self.object_stack:
            return self.object_stack[-1]
        return None

    def _get_named_object(self, name):
        obj = self.named_objects.get(name)
        if not obj:
            raise ValueError(f"Object '{name}' not found.")
        return obj

    def value(self, args):
        if len(args) == 1:
            return args[0]
        left, op, right = args
        if op == '+':
            return left + right
        if op == '-':
            return left - right

    def term(self, args):
        if len(args) == 1:
            return args[0]
        left, op, right = args
        if op == '*':
            return left * right
        if op == '/':
            return left / right

    def factor(self, args):
        item = args[0]
        if isinstance(item, Token):
            if item.type == 'NUMBER':
                return float(item)
            elif item.type == 'CNAME':
                return str(item)
        return item

    def shape(self, args):
        # This rule handles the optional 'as CNAME' part
        obj = args[0] # The actual shape object (Rectangle, Cube, etc.)
        name = None
        if len(args) > 1: # If 'as CNAME' is present
            name = str(args[1])
            # Update the named_objects dictionary with the created object
            self.named_objects[name] = obj
        
        # Crucially, push the object onto the stack here ONLY IF IT'S A 3D SHAPE
        if isinstance(obj, Shape):
            self._push_object(obj, name) # Pass name to _push_object for initial naming
        return obj

    def rect(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("rect", args)
        
        x, y, w, h = args
        rectangle = Rectangle(x, y, w, h)
        return rectangle

    def extrude(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("extrude", args)

        height, = args
        current_obj = self._get_current_object()
        if isinstance(current_obj, Rectangle):
            extruded_obj = current_obj.extrude(height)
            self._pop_object() # Pop the Rectangle
            self._push_object(extruded_obj) # Push the new extruded object
            return extruded_obj
        elif isinstance(current_obj, Shape):
            # If it's already a 3D shape, extrude it further (though this might not be desired behavior)
            # For now, we'll just return the current object if it's not a Rectangle
            return current_obj
        return None

    def cube(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("cube", args)
        
        x, y, z, size = args
        cube = Cube(x, y, z, size)
        return cube

    def sphere(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("sphere", args)
        
        x, y, z, radius = args
        sphere = Sphere(x, y, z, radius)
        return sphere

    def cylinder(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("cylinder", args)
        
        x, y, z, radius, height = args
        cylinder = Cylinder(x, y, z, radius, height)
        return cylinder

    def cone(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("cone", args)
        
        x, y, z, radius1, radius2, height = args
        cone = Cone(x, y, z, radius1, radius2, height)
        return cone

    def extrude(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("extrude", args)

        height, = args
        current_obj = self._get_current_object()
        if isinstance(current_obj, Rectangle):
            extruded_obj = current_obj.extrude(height)
            self._pop_object() # Pop the Rectangle
            self._push_object(extruded_obj) # Push the new extruded object
            return extruded_obj
        return None

    def _apply_transformation(self, transformation, args, statements):
        nested_objects = []
        for stmt in statements:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            nested_objects.extend(self.object_stack)
            self.object_stack = temp_stack
        
        for obj in nested_objects:
            if isinstance(obj, Shape):
                transformation(obj, *args)
                self._push_object(obj) 
        return None

    def translate(self, args):
        x, y, z = args[:3]
        statements = args[3:]
        return self._apply_transformation(lambda obj, x, y, z: obj.translate(x, y, z), (x, y, z), statements)

    def rotate(self, args):
        angle, ax, ay, az = args[:4]
        statements = args[4:]
        return self._apply_transformation(lambda obj, angle, ax, ay, az: obj.rotate(angle, ax, ay, az), (angle, ax, ay, az), statements)

    def scale(self, args):
        x, y, z = args[:3]
        statements = args[3:]
        return self._apply_transformation(lambda obj, x, y, z: obj.scale(x, y, z), (x, y, z), statements)

    def mirror(self, args):
        nx, ny, nz = args[:3]
        statements = args[3:]
        return self._apply_transformation(lambda obj, nx, ny, nz: obj.mirror(nx, ny, nz), (nx, ny, nz), statements)

    def union(self, args):
        shapes_to_union = []
        for stmt in args:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            if self.object_stack and isinstance(self.object_stack[-1], Shape):
                shapes_to_union.append(self.object_stack[-1])
            self.object_stack = temp_stack 
        
        if not shapes_to_union:
            return None

        result_shape = shapes_to_union[0]
        for i in range(1, len(shapes_to_union)):
            result_shape = result_shape.union(shapes_to_union[i])
        
        self._push_object(result_shape)
        return result_shape

    def subtract(self, args):
        main_shape = None
        shapes_to_subtract = []

        temp_stack = list(self.object_stack)
        self.object_stack = []
        self.transform(args[0])
        if self.object_stack and isinstance(self.object_stack[-1], Shape):
            main_shape = self.object_stack[-1]
        self.object_stack = temp_stack

        if not isinstance(main_shape, Shape):
            raise ValueError("First argument to subtract must be a shape")

        for stmt in args[1:]:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            if self.object_stack and isinstance(self.object_stack[-1], Shape):
                shapes_to_subtract.append(self.object_stack[-1])
            self.object_stack = temp_stack
        
        if not shapes_to_subtract:
            self._push_object(main_shape)
            return main_shape

        result_shape = main_shape
        for shape_to_sub in shapes_to_subtract:
            result_shape = result_shape.subtract(shape_to_sub)
        
        self._push_object(result_shape)
        return result_shape

    def module(self, args):
        module_name = args[0]
        
        params = []
        body = None
        for arg in args[1:]:
            if isinstance(arg, Tree):
                body = arg
                break
            else:
                params.append(arg)

        self.modules[str(module_name)] = {"params": [str(p) for p in params], "body": body.children}
        return None

    def use(self, args):
        module_name = str(args[0])
        call_args = args[1:]
        
        module = self.modules.get(module_name)
        if not module:
            raise ValueError(f"Module {module_name} not defined")

        if len(call_args) != len(module["params"]):
            raise ValueError(f"Incorrect number of arguments for module {module_name}")

        module_vars = dict(zip(module["params"], call_args))
        
        original_object_stack = list(self.object_stack)
        original_named_objects = dict(self.named_objects) 
        self.object_stack = [] 
        self.named_objects = {} 

        temp_transformer = CadTransformer() 
        temp_transformer.modules = self.modules 
        temp_transformer.named_objects = self.named_objects 

        for stmt_tree in module["body"]:
            resolved_stmt_tree = self._resolve_module_vars(stmt_tree, module_vars)
            
            transformed_obj = temp_transformer.transform(resolved_stmt_tree)
            if transformed_obj and isinstance(transformed_obj, Shape):
                self._push_object(transformed_obj) 

        self.object_stack = original_object_stack + temp_transformer.object_stack 
        self.named_objects = original_named_objects 
        
        return self._get_current_object()

    def _resolve_module_vars(self, tree, module_vars):
        if isinstance(tree, Token) and tree.type == 'CNAME' and str(tree) in module_vars:
            return Token('NUMBER', str(module_vars[str(tree)]))
        elif isinstance(tree, Tree):
            new_children = []
            for child in tree.children:
                new_children.append(self._resolve_module_vars(child, module_vars))
            return Tree(tree.data, new_children)
        return tree

    def start(self, args):
        self.scene.objects = [obj for obj in self.object_stack if isinstance(obj, Shape)]
        self.scene.current_object = self._get_current_object()
        return self.scene

    # Constraint Implementations
    def align_x(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        # Now obj1.cq_object and obj2.cq_object are cadquery.Shape (Solid) objects
        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        dx = bb2.xmin - bb1.xmin
        obj1.translate(dx, 0, 0)
        return None

    def align_y(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        dy = bb2.ymin - bb1.ymin
        obj1.translate(0, dy, 0)
        return None

    def align_z(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        dz = bb2.zmin - bb1.zmin
        obj1.translate(0, 0, dz)
        return None

    def center_on_x(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        center1_x = (bb1.xmin + bb1.xmax) / 2
        center2_x = (bb2.xmin + bb2.xmax) / 2

        dx = center2_x - center1_x
        obj1.translate(dx, 0, 0)
        return None

    def center_on_y(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        center1_y = (bb1.ymin + bb1.ymax) / 2
        center2_y = (bb2.ymin + bb2.ymax) / 2

        dy = center2_y - center1_y
        obj1.translate(0, dy, 0)
        return None

    def center_on_z(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        center1_z = (bb1.zmin + bb1.zmax) / 2
        center2_z = (bb2.zmin + bb2.zmax) / 2

        dz = center2_z - center1_z
        obj1.translate(0, 0, dz)
        return None

    def distance_x(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        current_dist_x = bb2.xmin - bb1.xmax
        dx = dist - current_dist_x
        obj2.translate(dx, 0, 0)
        return None

    def distance_y(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        current_dist_y = bb2.ymin - bb1.ymax
        dy = dist - current_dist_y
        obj2.translate(0, dy, 0)
        return None

    def distance_z(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()

        current_dist_z = bb2.zmin - bb1.zmax
        dz = dist - current_dist_z
        obj2.translate(0, 0, dz)
        return None

    def fixed(self, args):
        obj_name = args[0]
        obj = self._get_named_object(obj_name)
        self.fixed_objects.add(obj_name)
        print(f"Object '{obj_name}' is marked as fixed. Its position will not be altered by subsequent constraints.")
        return None
    
    # ========================================================================
    # NEW 2D SHAPES
    # ========================================================================
    
    def circle(self, args):
        """Circle (x, y, radius)"""
        if any(isinstance(arg, str) for arg in args):
            return ("circle", args)
        
        x, y, radius = args
        # Create a 2D circle - returns a Rectangle-like object that can be extruded
        # For now, using a placeholder similar to Rectangle
        print(f"[STUB] Creating circle at ({x}, {y}) with radius {radius}")
        # TODO: Implement actual Circle class
        return Rectangle(x - radius, y - radius, radius * 2, radius * 2)
    
    def ellipse(self, args):
        """Ellipse (x, y, major_radius, minor_radius)"""
        if any(isinstance(arg, str) for arg in args):
            return ("ellipse", args)
        
        x, y, major_r, minor_r = args
        print(f"[STUB] Creating ellipse at ({x}, {y}) with radii ({major_r}, {minor_r})")
        # TODO: Implement actual Ellipse class
        return Rectangle(x - major_r, y - minor_r, major_r * 2, minor_r * 2)
    
    def polygon(self, args):
        """Polygon (x, y, radius, sides)"""
        if any(isinstance(arg, str) for arg in args):
            return ("polygon", args)
        
        x, y, radius, sides = args
        print(f"[STUB] Creating {int(sides)}-sided polygon at ({x}, {y}) with radius {radius}")
        # TODO: Implement actual Polygon class
        return Rectangle(x - radius, y - radius, radius * 2, radius * 2)
    
    # ========================================================================
    # NEW 3D SHAPES
    # ========================================================================
    
    def torus(self, args):
        """Torus (x, y, z, major_radius, minor_radius)"""
        if any(isinstance(arg, str) for arg in args):
            return ("torus", args)
        
        x, y, z, major_r, minor_r = args
        print(f"[STUB] Creating torus at ({x}, {y}, {z}) with radii ({major_r}, {minor_r})")
        # TODO: Implement actual Torus class using CadQuery
        # For now, return a placeholder sphere
        return Sphere(x, y, z, major_r)
    
    def prism(self, args):
        """Prism (x, y, z, radius, sides, height)"""
        if any(isinstance(arg, str) for arg in args):
            return ("prism", args)
        
        x, y, z, radius, sides, height = args
        print(f"[STUB] Creating {int(sides)}-sided prism at ({x}, {y}, {z})")
        # TODO: Implement actual Prism class
        return Cylinder(x, y, z, radius, height)
    
    def hole(self, args):
        """Hole (x, y, z, radius, depth) - negative space"""
        if any(isinstance(arg, str) for arg in args):
            return ("hole", args)
        
        x, y, z, radius, depth = args
        print(f"[STUB] Creating hole at ({x}, {y}, {z}) with radius {radius}, depth {depth}")
        # Holes are represented as cylinders that will be subtracted
        # TODO: Mark as negative space for automatic subtraction
        hole_cyl = Cylinder(x, y, z, radius, depth)
        # Mark it as a hole somehow
        hole_cyl._is_hole = True
        return hole_cyl
    
    # ========================================================================
    # SPECIALIZED COMPONENTS
    # ========================================================================
    
    def gear(self, args):
        """Gear (x, y, z, module, teeth, pressure_angle, height)"""
        if any(isinstance(arg, str) for arg in args):
            return ("gear", args)
        
        x, y, z, module, teeth, pressure_angle, height = args
        print(f"[STUB] Creating gear at ({x}, {y}, {z}) with {int(teeth)} teeth, module {module}")
        
        # Basic validation
        if teeth < 6:
            raise GeometryError(f"Gear must have at least 6 teeth, got {teeth}")
        
        # TODO: Implement actual involute gear generation
        # For now, approximate as a cylinder
        pitch_diameter = module * teeth
        return Cylinder(x, y, z, pitch_diameter / 2, height)
    
    def spring(self, args):
        """Spring (x, y, z, radius, wire_diameter, coils, pitch)"""
        if any(isinstance(arg, str) for arg in args):
            return ("spring", args)
        
        x, y, z, radius, wire_dia, coils, pitch = args
        print(f"[STUB] Creating spring at ({x}, {y}, {z}) with {coils} coils")
        
        # TODO: Implement actual helical spring generation
        spring_height = coils * pitch
        return Cylinder(x, y, z, radius, spring_height)
    
    def beam(self, args):
        """Beam (x, y, z, length, width, type)"""
        if any(isinstance(arg, str) for arg in args[:-1]):  # Last arg is string type
            return ("beam", args)
        
        x, y, z, length, width = args[:5]
        beam_type = str(args[5]).strip('"')
        print(f"[STUB] Creating {beam_type}-beam at ({x}, {y}, {z})")
        
        valid_types = ["i", "t", "l", "c", "box"]
        if beam_type not in valid_types:
            raise GeometryError(f"Invalid beam type: {beam_type}. Must be one of {valid_types}")
        
        # TODO: Implement actual beam profiles
        return Cube(x, y, z, length)
    
    def bearing(self, args):
        """Bearing (x, y, z, inner_diameter, outer_diameter, width)"""
        if any(isinstance(arg, str) for arg in args):
            return ("bearing", args)
        
        x, y, z, inner_d, outer_d, width = args
        print(f"[STUB] Creating bearing at ({x}, {y}, {z})")
        
        if inner_d >= outer_d:
            raise GeometryError(f"Inner diameter ({inner_d}) must be less than outer diameter ({outer_d})")
        
        # TODO: Implement actual bearing with inner race, outer race, and balls
        # For now, just a cylinder
        return Cylinder(x, y, z, outer_d / 2, width)
    
    # ========================================================================
    # EXTRUSION OPTIONS
    # ========================================================================
    
    def extrude_option(self, args):
        """Returns the extrusion option type"""
        return str(args[0])
    
    # ========================================================================
    # SURFACE OPERATIONS
    # ========================================================================
    
    def revolve(self, args):
        """Revolve (axis_x, axis_y, axis_z, angle) { profile }"""
        axis_x, axis_y, axis_z, angle = args[:4]
        statements = args[4:]
        print(f"[STUB] Revolve around axis ({axis_x}, {axis_y}, {axis_z}) by {angle}°")
        
        # TODO: Implement revolve operation
        # Process statements and revolve the profile
        for stmt in statements:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            self.object_stack = temp_stack
        
        return None
    
    def sweep(self, args):
        """Sweep (path) { profile }"""
        path = args[0]
        statements = args[1:]
        print(f"[STUB] Sweep along path")
        
        # TODO: Implement sweep operation
        return None
    
    def loft(self, args):
        """Loft between multiple profiles"""
        print(f"[STUB] Loft between {len(args)} profiles")
        
        # TODO: Implement loft operation
        return None
    
    def shell(self, args):
        """Shell (thickness)"""
        thickness = args[0]
        print(f"[STUB] Shell with thickness {thickness}")
        
        # TODO: Apply shell operation to current object
        current_obj = self._get_current_object()
        if current_obj:
            print(f"Applying shell to {type(current_obj).__name__}")
        
        return None
    
    def offset(self, args):
        """Offset (distance)"""
        distance = args[0]
        print(f"[STUB] Offset by {distance}")
        
        # TODO: Apply offset operation to current object
        return None
    
    def fillet(self, args):
        """Fillet (radius, edge_spec)"""
        radius = args[0]
        edge_spec = args[1] if len(args) > 1 else "all"
        print(f"[STUB] Fillet with radius {radius} on edges: {edge_spec}")
        
        # TODO: Apply fillet to specified edges
        return None
    
    def chamfer(self, args):
        """Chamfer (distance, edge_spec)"""
        distance = args[0]
        edge_spec = args[1] if len(args) > 1 else "all"
        print(f"[STUB] Chamfer with distance {distance} on edges: {edge_spec}")
        
        # TODO: Apply chamfer to specified edges
        return None
    
    def bevel(self, args):
        """Bevel (distance, angle)"""
        distance, angle = args
        print(f"[STUB] Bevel with distance {distance} at angle {angle}°")
        
        # TODO: Apply bevel operation
        return None
    
    def thread(self, args):
        """Thread (diameter, pitch, length, type)"""
        diameter, pitch, length = args[:3]
        thread_type = str(args[3]).strip('"')
        print(f"[STUB] Creating {thread_type} thread: D={diameter}, P={pitch}, L={length}")
        
        valid_types = ["metric", "imperial", "acme", "buttress"]
        if thread_type not in valid_types:
            raise GeometryError(f"Invalid thread type: {thread_type}")
        
        # TODO: Generate helical thread geometry
        return None
    
    # ========================================================================
    # CURVES AND PATHS
    # ========================================================================
    
    def arc(self, args):
        """Arc (center_x, center_y, radius, start_angle, end_angle)"""
        cx, cy, radius, start_angle, end_angle = args
        print(f"[STUB] Arc at ({cx}, {cy}), R={radius}, from {start_angle}° to {end_angle}°")
        
        # TODO: Return arc path object
        return ("arc", args)
    
    def curve(self, args):
        """Curve through points"""
        print(f"[STUB] Curve through {len(args)} points")
        
        # TODO: Return curve path object
        return ("curve", args)
    
    def spline(self, args):
        """Spline (points..., type)"""
        spline_type = str(args[-1]).strip('"')
        points = args[:-1]
        print(f"[STUB] {spline_type} spline through {len(points)} points")
        
        # TODO: Return spline path object
        return ("spline", args)
    
    def point(self, args):
        """Point (x, y, z)"""
        return tuple(args)
    
    def point_list(self, args):
        """List of points"""
        return list(args)
    
    def path_spec(self, args):
        """Path specification"""
        return args[0]
    
    def edge_spec(self, args):
        """Edge specification"""
        return str(args[0]).strip('"')
    
    # ========================================================================
    # WORK PLANES
    # ========================================================================
    
    def plane_select(self, args):
        """Plane selection"""
        plane_type = args[0]
        statements = args[1:]
        print(f"[STUB] Working on plane: {plane_type}")
        
        # TODO: Set working plane and process statements
        for stmt in statements:
            self.transform(stmt)
        
        return None
    
    # ========================================================================
    # HOLE PATTERNS
    # ========================================================================
    
    def linear_holes(self, args):
        """Linear holes with spacing"""
        x, y, z, radius, depth, count = args[:6]
        spacing = args[6]
        print(f"[STUB] Creating {int(count)} linear holes at ({x}, {y}, {z})")
        
        # TODO: Generate hole pattern
        # For now, create individual cylinders
        for i in range(int(count)):
            # Calculate position based on spacing
            pass
        
        return None
    
    def circular_holes(self, args):
        """Circular hole pattern"""
        cx, cy, cz, pattern_r, hole_r, hole_d, count = args
        print(f"[STUB] Creating {int(count)} circular holes around ({cx}, {cy}, {cz})")
        
        # TODO: Generate circular hole pattern
        return None
    
    def grid_holes(self, args):
        """Grid of holes"""
        x, y, z, radius, depth, rows, cols, spacing = args
        print(f"[STUB] Creating {int(rows)}x{int(cols)} grid of holes")
        
        # TODO: Generate grid hole pattern
        return None
    
    def uniform_spacing(self, args):
        """Uniform spacing"""
        distance = args[0]
        return ("uniform", distance)
    
    def non_uniform_spacing(self, args):
        """Non-uniform spacing"""
        distances = args
        return ("non_uniform", list(distances))
    
    def spacing_spec(self, args):
        """Spacing specification"""
        return args[0]
    
    def value_list(self, args):
        """List of values"""
        return list(args)
    
    # ========================================================================
    # ENHANCED CONSTRAINTS
    # ========================================================================
    
    def tangent(self, args):
        """Tangent constraint - objects touch but don't overlap"""
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Applying tangent constraint between '{obj1_name}' and '{obj2_name}'")
        
        # TODO: Calculate tangent positions
        # Check if objects would overlap
        self.constraints.append(("tangent", obj1_name, obj2_name))
        
        return None
    
    def perpendicular(self, args):
        """Perpendicular constraint"""
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Applying perpendicular constraint between '{obj1_name}' and '{obj2_name}'")
        
        self.constraints.append(("perpendicular", obj1_name, obj2_name))
        return None
    
    def parallel(self, args):
        """Parallel constraint"""
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Applying parallel constraint between '{obj1_name}' and '{obj2_name}'")
        
        self.constraints.append(("parallel", obj1_name, obj2_name))
        return None
    
    def angle_constraint(self, args):
        """Angle constraint"""
        obj1_name, obj2_name, angle = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Applying {angle}° angle constraint between '{obj1_name}' and '{obj2_name}'")
        
        self.constraints.append(("angle", obj1_name, obj2_name, angle))
        return None
    
    def no_collision(self, args):
        """No collision constraint - ensures objects don't overlap"""
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Checking collision between '{obj1_name}' and '{obj2_name}'")
        
        # TODO: Implement actual collision detection
        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()
        
        # Simple bounding box overlap check
        overlap_x = not (bb1.xmax < bb2.xmin or bb2.xmax < bb1.xmin)
        overlap_y = not (bb1.ymax < bb2.ymin or bb2.ymax < bb1.ymin)
        overlap_z = not (bb1.zmax < bb2.zmin or bb2.zmax < bb1.zmin)
        
        if overlap_x and overlap_y and overlap_z:
            raise ConstraintError(
                f"Collision detected between '{obj1_name}' and '{obj2_name}'. "
                f"Objects overlap in space."
            )
        
        self.constraints.append(("no_collision", obj1_name, obj2_name))
        return None
    
    def contained_in(self, args):
        """Containment constraint - obj1 must be inside obj2"""
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Checking containment: '{obj1_name}' in '{obj2_name}'")
        
        # TODO: Implement actual containment check
        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()
        
        # Check if obj1's bounding box is inside obj2's bounding box
        contained = (
            bb1.xmin >= bb2.xmin and bb1.xmax <= bb2.xmax and
            bb1.ymin >= bb2.ymin and bb1.ymax <= bb2.ymax and
            bb1.zmin >= bb2.zmin and bb1.zmax <= bb2.zmax
        )
        
        if not contained:
            raise ConstraintError(
                f"Containment constraint failed: '{obj1_name}' is not fully contained within '{obj2_name}'. "
                f"Object extends outside container bounds."
            )
        
        self.constraints.append(("contained_in", obj1_name, obj2_name))
        return None
    
    # ========================================================================
    # TOLERANCES
    # ========================================================================
    
    def dimensional_tolerance(self, args):
        """Dimensional tolerance (object, plus, minus)"""
        obj_name, plus_tol, minus_tol = args
        obj = self._get_named_object(obj_name)
        
        print(f"[STUB] Setting tolerance for '{obj_name}': +{plus_tol}/-{minus_tol}")
        
        if plus_tol < 0 or minus_tol < 0:
            raise ToleranceError(f"Tolerances must be non-negative")
        
        self.tolerances[obj_name] = {
            'type': 'dimensional',
            'plus': plus_tol,
            'minus': minus_tol
        }
        
        return None
    
    def geometric_tolerance(self, args):
        """Geometric tolerance (object, type, value)"""
        obj_name = args[0]
        tol_type = str(args[1]).strip('"')
        value = args[2]
        
        obj = self._get_named_object(obj_name)
        
        print(f"[STUB] Setting {tol_type} tolerance for '{obj_name}': {value}")
        
        valid_types = [
            "flatness", "straightness", "circularity", "cylindricity",
            "perpendicularity", "parallelism", "angularity",
            "position", "concentricity", "symmetry", "runout"
        ]
        
        if tol_type not in valid_types:
            raise ToleranceError(f"Invalid tolerance type: {tol_type}")
        
        if obj_name not in self.tolerances:
            self.tolerances[obj_name] = {}
        
        self.tolerances[obj_name][tol_type] = value
        
        return None
    
    def fit_tolerance(self, args):
        """Fit tolerance (object1, object2, fit_type)"""
        obj1_name, obj2_name = args[:2]
        fit_type = str(args[2]).strip('"')
        
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)
        
        print(f"[STUB] Setting {fit_type} fit between '{obj1_name}' and '{obj2_name}'")
        
        valid_fits = ["clearance", "transition", "interference"]
        if fit_type not in valid_fits:
            raise ToleranceError(f"Invalid fit type: {fit_type}. Must be one of {valid_fits}")
        
        # TODO: Implement actual fit checking
        # For clearance fit, ensure obj1 (shaft) can fit inside obj2 (hole)
        bb1 = obj1.cq_object.BoundingBox()
        bb2 = obj2.cq_object.BoundingBox()
        
        # Simple check: compare sizes
        size1 = max(bb1.xmax - bb1.xmin, bb1.ymax - bb1.ymin)
        size2 = max(bb2.xmax - bb2.xmin, bb2.ymax - bb2.ymin)
        
        if fit_type == "clearance" and size1 >= size2:
            raise ConstraintError(
                f"Clearance fit impossible: '{obj1_name}' (size {size1:.2f}) "
                f"cannot fit with clearance in '{obj2_name}' (size {size2:.2f})"
            )
        
        self.constraints.append(("fit", obj1_name, obj2_name, fit_type))
        
        return None
    
    def tolerance_spec(self, args):
        """Tolerance specification handler"""
        return args[0]
    
    # ========================================================================
    # BOOLEAN OPERATIONS (Extended)
    # ========================================================================
    
    def intersect(self, args):
        """Intersect operation - common volume"""
        shapes_to_intersect = []
        for stmt in args:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            if self.object_stack and isinstance(self.object_stack[-1], Shape):
                shapes_to_intersect.append(self.object_stack[-1])
            self.object_stack = temp_stack
        
        if len(shapes_to_intersect) < 2:
            print("[STUB] Intersect requires at least 2 shapes")
            return None
        
        print(f"[STUB] Intersecting {len(shapes_to_intersect)} shapes")
        
        # TODO: Implement actual intersection using CadQuery
        # For now, just return the first shape
        result_shape = shapes_to_intersect[0]
        
        self._push_object(result_shape)
        return result_shape
