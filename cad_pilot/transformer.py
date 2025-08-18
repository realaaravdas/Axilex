from lark import Transformer, Tree, Token
from .core.geometry import Rectangle, Cube, Sphere, Cylinder, Shape
from .core.scene import Scene

class CadTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.modules = {}
        self.object_stack = [] # To handle nested transformations and boolean operations

    def _push_object(self, obj):
        self.object_stack.append(obj)
        self.scene.set_current_object(obj)

    def _pop_object(self):
        if self.object_stack:
            return self.object_stack.pop()
        return None

    def _get_current_object(self):
        if self.object_stack:
            return self.object_stack[-1]
        return None

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
        # The rest of args are the statements to apply translation to
        statements = args[3:]

        # Process nested statements first
        for stmt in statements:
            self.transform(stmt)
            current_obj = self._get_current_object()
            if current_obj:
                current_obj.translate(x, y, z)
        return None

    def rotate(self, args):
        angle, ax, ay, az = args[:4]
        statements = args[4:]
        axis = [ax, ay, az]

        for stmt in statements:
            self.transform(stmt)
            current_obj = self._get_current_object()
            if current_obj:
                current_obj.rotate(angle, axis)
        return None

    def scale(self, args):
        x, y, z = args[:3]
        statements = args[3:]

        for stmt in statements:
            self.transform(stmt)
            current_obj = self._get_current_object()
            if current_obj:
                current_obj.scale(x, y, z)
        return None

    def union(self, args):
        # All args are statements that produce shapes to union
        shapes_to_union = []
        for stmt in args:
            self.transform(stmt)
            current_obj = self._pop_object()
            if current_obj and isinstance(current_obj, Shape):
                shapes_to_union.append(current_obj)
        
        if not shapes_to_union:
            return None

        # Perform union iteratively
        result_shape = shapes_to_union[0]
        for i in range(1, len(shapes_to_union)):
            result_shape = result_shape.union(shapes_to_union[i])
        
        self._push_object(result_shape)
        return result_shape

    def subtract(self, args):
        # First arg is the main shape, rest are shapes to subtract
        main_shape = None
        shapes_to_subtract = []

        # Process the first statement for the main shape
        self.transform(args[0])
        main_shape = self._pop_object()
        if not isinstance(main_shape, Shape):
            raise ValueError("First argument to subtract must be a shape")

        # Process subsequent statements for shapes to subtract
        for stmt in args[1:]:
            self.transform(stmt)
            current_obj = self._pop_object()
            if current_obj and isinstance(current_obj, Shape):
                shapes_to_subtract.append(current_obj)
        
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
        
        # Store current object stack state to restore after module execution
        original_object_stack = list(self.object_stack)
        self.object_stack = [] # Clear stack for module execution

        for stmt_tree in module["body"]:
            # Create a new transformer instance for module body to handle local scope
            # This is a simplified approach; a more robust solution would involve proper scope management
            temp_transformer = CadTransformer() 
            temp_transformer.modules = self.modules # Share modules
            
            # Replace CNAMEs in the statement tree with their resolved values
            # This is a basic substitution; a more complex AST rewrite might be needed for full generality
            resolved_stmt_tree = self._resolve_module_vars(stmt_tree, module_vars)
            
            transformed_obj = temp_transformer.transform(resolved_stmt_tree)
            if transformed_obj and isinstance(transformed_obj, Shape):
                self._push_object(transformed_obj) # Add the result of the module to the main stack

        # Restore original object stack
        self.object_stack = original_object_stack + self.object_stack # Append module results to original stack
        
        # The last object pushed by the module is the effective current object
        return self._get_current_object()

    def _resolve_module_vars(self, tree, module_vars):
        # This is a simplified resolver. For complex nested structures, a proper AST traversal is needed.
        if isinstance(tree, Token) and tree.type == 'CNAME' and str(tree) in module_vars:
            return Token('NUMBER', str(module_vars[str(tree)]))
        elif isinstance(tree, Tree):
            new_children = []
            for child in tree.children:
                new_children.append(self._resolve_module_vars(child, module_vars))
            return Tree(tree.data, new_children)
        return tree

    def start(self, args):
        # The start rule should collect all top-level objects that remain on the stack
        # after all statements have been processed.
        self.scene.objects = [obj for obj in self.object_stack if isinstance(obj, Shape)]
        self.scene.current_object = self._get_current_object()
        return self.scene