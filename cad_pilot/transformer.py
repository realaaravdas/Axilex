from lark import Transformer, Tree, Token
from .core.geometry import Rectangle, Cube, Sphere, Cylinder, Cone, Shape
from .core.scene import Scene
import cadquery as cq

class CadTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.modules = {}
        self.object_stack = [] # To handle nested transformations and boolean operations
        self.named_objects = {} # To store objects by their assigned names

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
        
        # Crucially, push the object onto the stack here
        self._push_object(obj, name) # Pass name to _push_object for initial naming
        return obj

    def rect(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("rect", args)
        
        x, y, w, h = args
        rectangle = Rectangle(x, y, w, h)
        return rectangle

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
        print(f"Object '{obj_name}' is marked as fixed. Its position will not be altered by subsequent constraints.")
        return None
