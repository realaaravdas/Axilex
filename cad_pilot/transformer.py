from lark import Transformer, Tree, Token
from .core.geometry import Rectangle, Cube, Sphere, Cylinder, Shape
from .core.scene import Scene
from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.gp import gp_Pnt, gp_Vec

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
        item = args[0]
        if item.type == 'NUMBER':
            return float(item)
        elif item.type == 'CNAME':
            return str(item)
        return item

    def rect(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("rect", args)
        
        x, y, w, h = args
        rectangle = Rectangle(x, y, w, h)
        self._push_object(rectangle)
        return rectangle

    def cube(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("cube", args)
        
        x, y, z, size = args
        cube = Cube(x, y, z, size)
        self._push_object(cube)
        return cube

    def sphere(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("sphere", args)
        
        x, y, z, radius = args
        sphere = Sphere(x, y, z, radius)
        self._push_object(sphere)
        return sphere

    def cylinder(self, args):
        if any(isinstance(arg, str) for arg in args):
            return ("cylinder", args)
        
        x, y, z, radius, height = args
        cylinder = Cylinder(x, y, z, radius, height)
        self._push_object(cylinder)
        return cylinder

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

    def translate(self, args):
        x, y, z = args[:3]
        statements = args[3:]

        nested_objects = []
        for stmt in statements:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            nested_objects.extend(self.object_stack)
            self.object_stack = temp_stack
        
        for obj in nested_objects:
            if isinstance(obj, Shape):
                obj.translate(x, y, z)
                self._push_object(obj) 
        return None

    def rotate(self, args):
        angle, ax, ay, az = args[:4]
        statements = args[4:]
        axis = [ax, ay, az]

        nested_objects = []
        for stmt in statements:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            nested_objects.extend(self.object_stack)
            self.object_stack = temp_stack

        for obj in nested_objects:
            if isinstance(obj, Shape):
                obj.rotate(angle, axis[0], axis[1], axis[2]) 
                self._push_object(obj)
        return None

    def scale(self, args):
        x, y, z = args[:3]
        statements = args[3:]

        nested_objects = []
        for stmt in statements:
            temp_stack = list(self.object_stack)
            self.object_stack = []
            self.transform(stmt)
            nested_objects.extend(self.object_stack)
            self.object_stack = temp_stack

        for obj in nested_objects:
            if isinstance(obj, Shape):
                obj.scale(x, y, z)
                self._push_object(obj)
        return None

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
        original_named_objects = dict(self.named_objects) # Save named objects state
        self.object_stack = [] 
        self.named_objects = {} # Clear named objects for module scope

        for stmt_tree in module["body"]:
            temp_transformer = CadTransformer() 
            temp_transformer.modules = self.modules 
            temp_transformer.named_objects = self.named_objects # Pass current named objects for module scope
            
            resolved_stmt_tree = self._resolve_module_vars(stmt_tree, module_vars)
            
            transformed_obj = temp_transformer.transform(resolved_stmt_tree)
            if transformed_obj and isinstance(transformed_obj, Shape):
                self._push_object(transformed_obj) 

        self.object_stack = original_object_stack + self.object_stack 
        self.named_objects = original_named_objects # Restore named objects state
        
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

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        # Calculate translation needed to align obj1's min X with obj2's min X
        dx = bbox2.CornerMin().X() - bbox1.CornerMin().X()
        obj1.translate(dx, 0, 0)
        return None

    def align_y(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        dy = bbox2.CornerMin().Y() - bbox1.CornerMin().Y()
        obj1.translate(0, dy, 0)
        return None

    def align_z(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        dz = bbox2.CornerMin().Z() - bbox1.CornerMin().Z()
        obj1.translate(0, 0, dz)
        return None

    def center_on_x(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        center1_x = (bbox1.CornerMin().X() + bbox1.CornerMax().X()) / 2
        center2_x = (bbox2.CornerMin().X() + bbox2.CornerMax().X()) / 2

        dx = center2_x - center1_x
        obj1.translate(dx, 0, 0)
        return None

    def center_on_y(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        center1_y = (bbox1.CornerMin().Y() + bbox1.CornerMax().Y()) / 2
        center2_y = (bbox2.CornerMin().Y() + bbox2.CornerMax().Y()) / 2

        dy = center2_y - center1_y
        obj1.translate(0, dy, 0)
        return None

    def center_on_z(self, args):
        obj1_name, obj2_name = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        center1_z = (bbox1.CornerMin().Z() + bbox1.CornerMax().Z()) / 2
        center2_z = (bbox2.CornerMin().Z() + bbox2.CornerMax().Z()) / 2

        dz = center2_z - center1_z
        obj1.translate(0, 0, dz)
        return None

    def distance_x(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        current_dist_x = bbox2.CornerMin().X() - bbox1.CornerMax().X()
        dx = dist - current_dist_x
        obj2.translate(dx, 0, 0)
        return None

    def distance_y(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        current_dist_y = bbox2.CornerMin().Y() - bbox1.CornerMax().Y()
        dy = dist - current_dist_y
        obj2.translate(0, dy, 0)
        return None

    def distance_z(self, args):
        obj1_name, obj2_name, dist = args
        obj1 = self._get_named_object(obj1_name)
        obj2 = self._get_named_object(obj2_name)

        bbox1 = Bnd_Box()
        brepbndlib_Add(obj1.occt_shape, bbox1)
        bbox2 = Bnd_Box()
        brepbndlib_Add(obj2.occt_shape, bbox2)

        current_dist_z = bbox2.CornerMin().Z() - bbox1.CornerMax().Z()
        dz = dist - current_dist_z
        obj2.translate(0, 0, dz)
        return None

    def fixed(self, args):
        # For this simplified constraint system, 'fixed' means the object's position
        # is determined by its initial definition and any preceding transformations.
        # It primarily serves as a marker or for future more complex solvers.
        # In this direct application model, it doesn't perform an action itself.
        obj_name = args[0]
        obj = self._get_named_object(obj_name)
        print(f"Object '{obj_name}' is marked as fixed. Its position will not be altered by subsequent constraints.")
        return None