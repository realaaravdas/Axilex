# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KRYSTALcad is a Python-based CAD language and compiler that provides a custom domain-specific language (DSL) for creating 3D models. The system parses `.cadp` files, transforms them into 3D geometry using CadQuery, and renders them using PyVista.

## Development Commands

### Running the Application
```bash
python main.py
# or
python -m cad_pilot.renderer.ui.launcher
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Testing CAD Files
Test with example files in the `examples/` directory:
- `examples/simple_box.cadp` - Basic rectangle extrusion
- `examples/module_test.cadp` - Module system examples  
- `examples/advanced_example.cadp` - Complex geometry operations
- `examples/constraints_example.cadp` - Constraint system usage

## Architecture

### Core Components

**Parser (`cad_pilot/parser.py`)**
- Uses Lark parsing library with custom grammar
- Parses `.cadp` files into abstract syntax trees
- Grammar supports shapes, transformations, boolean operations, modules, and constraints

**Transformer (`cad_pilot/transformer.py`)**  
- Converts AST into 3D geometry objects using the Transformer pattern
- Manages object stack for nested operations and transformations
- Handles module system with parameter substitution
- Implements constraint solving for object positioning

**Geometry System (`cad_pilot/core/geometry.py`)**
- Wraps CadQuery objects with custom Shape class
- Provides Rectangle (2D) and 3D shapes (Cube, Sphere, Cylinder, Cone)
- Implements transformations (translate, rotate, scale, mirror)
- Boolean operations (union, subtract) 
- PyVista mesh conversion for rendering

**Scene Management (`cad_pilot/core/scene.py`)**
- Manages collections of geometry objects
- Tracks current object context

**UI System (`cad_pilot/renderer/ui/`)**
- CustomTkinter-based GUI with launcher and render views
- PyVista widget integration for 3D visualization
- File loading and export functionality

### Language Features

**Basic Shapes:**
```cadp
rect(x, y, width, height)
cube(x, y, z, size) 
sphere(x, y, z, radius)
cylinder(x, y, z, radius, height)
cone(x, y, z, radius1, radius2, height)
```

**Transformations:**
```cadp
translate(x, y, z) { ... }
rotate(angle, ax, ay, az) { ... }
scale(x, y, z) { ... }
mirror(nx, ny, nz) { ... }
```

**Boolean Operations:**
```cadp
union { ... }
subtract { ... }
```

**Module System:**
```cadp
module name(param1, param2) { ... }
use name(value1, value2)
```

**Constraints:**
- `align_x/y/z(obj1, obj2)` - Align object edges
- `center_on_x/y/z(obj1, obj2)` - Center objects
- `distance_x/y/z(obj1, obj2, dist)` - Set distances
- `fixed(obj)` - Mark object as immovable

### Key Implementation Details

- **Object Stack Management**: The transformer uses a stack-based approach to handle nested transformations and boolean operations
- **CadQuery Integration**: All 3D operations are backed by CadQuery for solid modeling
- **VTK Rendering**: PyVista provides 3D visualization through VTK
- **Temporary File Handling**: VTP format used for CadQuery to PyVista mesh conversion
- **Module Resolution**: Variables in module bodies are resolved at call time through AST transformation

### Export Capabilities

The exporter (`cad_pilot/exporter.py`) supports:
- STL format for 3D printing
- STEP format for CAD interchange  
- DXF format for 2D drawings

All exports combine multiple objects into single output files using CadQuery's export system.