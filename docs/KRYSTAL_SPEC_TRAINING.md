# Krystal CAD Language - Complete Training Specification

## Overview
**Language Name:** Krystal
**File Extension:** `.krystal` (modern), `.cadp` (legacy/Python implementation)
**Application:** Axilex
**Purpose:** Domain-specific language for 3D CAD modeling and solid geometry
**Paradigm:** Declarative, procedural
**Typing:** Dynamic values, static structure

## Core Concepts

### Philosophy
Krystal is designed for creating 3D CAD models through declarative geometry definitions. Users describe shapes and their relationships, and the system generates 3D models. The language supports:
- Constructive Solid Geometry (CSG)
- Parametric design through modules
- Constraint-based positioning
- Engineering tolerances and specifications
- Reusable component libraries

### Execution Model
1. Parse source code into Abstract Syntax Tree (AST)
2. Process statements sequentially
3. Build geometry scene with named objects
4. Apply transformations and boolean operations
5. Resolve constraints and position objects
6. Validate collisions and containment
7. Generate 3D geometry output
8. Export to formats (STL, STEP, DXF)

## Lexical Structure

### Comments
```krystal
# This is a single-line comment
# Comments start with # and continue to end of line
```

### Identifiers
- Start with letter or underscore
- Contain letters, digits, underscores
- Case-sensitive
- Examples: `box1`, `my_module`, `_temp`, `BearingMount`

### Numbers
- Integer: `42`, `-17`
- Float: `3.14`, `-0.5`, `2.0`
- Scientific notation not currently supported

### Strings
- Enclosed in double quotes: `"i"`, `"metric"`, `"XY"`
- Used for type specifiers and enum values

### Operators
- Arithmetic: `+` (add), `-` (subtract), `*` (multiply), `/` (divide)
- Precedence: `*` `/` higher than `+` `-`
- Parentheses for grouping: `(expr)`

### Delimiters
- Parentheses: `()` for parameters
- Braces: `{}` for statement blocks
- Comma: `,` for parameter separation

## Type System

### Value Types

#### Number
Floating-point values for dimensions, coordinates, angles.
```krystal
10        # Integer
5.5       # Float
-3.14     # Negative
```

#### Identifier
Reference to parameter, variable, or named object.
```krystal
width     # Parameter name
box1      # Named object
my_var    # Variable
```

#### Expression
Arithmetic combination of values.
```krystal
width * 2
height + 10
(x + y) / 2
```

## Basic Shapes

### 2D Shapes (for extrusion)

#### Rectangle
```krystal
rect(x, y, width, height)
```
- Creates rectangle at position (x, y)
- Used as profile for extrusion
- Example: `rect(0, 0, 10, 20)`

#### Circle
```krystal
circle(x, y, radius)
```
- Creates circle at center (x, y)
- Can be extruded to cylinder
- Example: `circle(5, 5, 3)`

#### Ellipse
```krystal
ellipse(x, y, major_radius, minor_radius)
```
- Creates ellipse centered at (x, y)
- Two radii define axes
- Example: `ellipse(10, 10, 8, 4)`

#### Polygon
```krystal
polygon(x, y, radius, sides)
```
- Creates regular polygon at (x, y)
- Circumscribed by circle of given radius
- Example: `polygon(0, 0, 5, 6)  # Hexagon`

### 3D Shapes

#### Cube
```krystal
cube(x, y, z, size)
```
- Creates cube with corner at (x, y, z)
- Size applies to all dimensions
- Example: `cube(0, 0, 0, 10) as box1`

#### Sphere
```krystal
sphere(x, y, z, radius)
```
- Creates sphere centered at (x, y, z)
- Example: `sphere(20, 20, 20, 5) as ball`

#### Cylinder
```krystal
cylinder(x, y, z, radius, height)
```
- Base center at (x, y, z)
- Extends along Z-axis
- Example: `cylinder(0, 0, 0, 4, 15)`

#### Cone
```krystal
cone(x, y, z, bottom_radius, top_radius, height)
```
- Tapered cylinder from bottom to top radius
- Base at (x, y, z)
- Example: `cone(0, 0, 0, 5, 2, 12)`

#### Torus
```krystal
torus(x, y, z, major_radius, minor_radius)
```
- Donut shape centered at (x, y, z)
- Major radius: center to tube center
- Minor radius: tube thickness
- Example: `torus(0, 0, 0, 8, 2)`

#### Prism
```krystal
prism(x, y, z, radius, sides, height)
```
- Extruded regular polygon
- Base at (x, y, z)
- Example: `prism(0, 0, 0, 5, 6, 15)  # Hexagonal prism`

### Negative Space

#### Hole
```krystal
hole(x, y, z, radius, depth)
```
- Creates cylindrical negative space
- For subtracting from solids
- Example: `hole(10, 10, 5, 2, 10)`

### Specialized Components

#### Gear
```krystal
gear(x, y, z, module, teeth, pressure_angle, height)
```
- Involute gear profile
- Module: gear size metric
- Pressure angle: typically 20°
- Example: `gear(0, 0, 0, 2, 20, 20, 5)`

#### Spring
```krystal
spring(x, y, z, radius, wire_diameter, coils, pitch)
```
- Helical coil spring
- Pitch: distance between coils
- Example: `spring(0, 0, 0, 5, 1, 10, 2)`

#### Beam
```krystal
beam(x, y, z, length, width, type)
```
- Structural beam profiles
- Types: `"i"`, `"t"`, `"l"`, `"c"`, `"box"`
- Example: `beam(0, 0, 0, 50, 10, "i")`

#### Bearing
```krystal
bearing(x, y, z, inner_diameter, outer_diameter, width)
```
- Bearing housing geometry
- Example: `bearing(0, 0, 0, 10, 20, 8)`

## Transformations

### Translate
```krystal
translate(x, y, z) {
    statements...
}
```
- Moves enclosed shapes by offset (x, y, z)
- Applied to all nested statements
- Transformations stack/compose
- Example:
```krystal
translate(10, 0, 0) {
    cube(0, 0, 0, 5)  # Actually at (10, 0, 0)
}
```

### Rotate
```krystal
rotate(angle, axis_x, axis_y, axis_z) {
    statements...
}
```
- Rotates around axis vector
- Angle in degrees
- Axis normalized automatically
- Example:
```krystal
rotate(45, 0, 0, 1) {  # 45° around Z-axis
    cube(0, 0, 0, 10)
}
```

### Scale
```krysal
scale(factor_x, factor_y, factor_z) {
    statements...
}
```
- Scales along each axis independently
- Factor > 1 enlarges, < 1 shrinks
- Example:
```krystal
scale(2, 1, 0.5) {
    cube(0, 0, 0, 10)  # Stretched in X, compressed in Z
}
```

### Mirror
```krystal
mirror(normal_x, normal_y, normal_z) {
    statements...
}
```
- Reflects across plane with given normal
- Example:
```krystal
mirror(1, 0, 0) {  # Mirror across YZ plane
    cylinder(5, 0, 0, 2, 10)
}
```

## Boolean Operations

### Union
```krystal
union {
    shape1
    shape2
    shape3
}
```
- Combines all enclosed shapes
- Creates single merged solid
- Example:
```krystal
union {
    cube(0, 0, 0, 10)
    sphere(5, 5, 5, 8)
}
```

### Subtract
```krystal
subtract {
    main_shape
    shape_to_remove1
    shape_to_remove2
}
```
- First shape is main body
- Subsequent shapes subtracted from it
- Creates holes, cavities
- Example:
```krystal
subtract {
    cube(0, 0, 0, 20)
    cylinder(10, 10, 0, 5, 20)  # Hole through center
}
```

### Intersect
```krystal
intersect {
    shape1
    shape2
}
```
- Keeps only overlapping volume
- Example:
```krystal
intersect {
    cube(0, 0, 0, 10)
    sphere(5, 5, 5, 8)  # Rounded cube corner
}
```

## Extrusion

### Basic Extrusion
```krystal
rect(0, 0, 10, 5)
extrude(height)
```
- Extrudes previous 2D shape into 3D
- Height along Z-axis
- Example:
```krystal
circle(0, 0, 5)
extrude(20)  # Creates cylinder
```

### Extrusion Options
```krystal
extrude(height) cone        # Tapered extrusion
extrude(height) dome        # Domed top
extrude(height) hemisphere  # Hemispherical cap
```

## Surface Operations

### Revolve
```krystal
revolve(axis_x, axis_y, axis_z, angle) {
    profile_shape
}
```
- Rotates profile around axis
- Creates surfaces of revolution
- Example:
```krystal
revolve(0, 1, 0, 360) {  # Around Y-axis
    rect(10, 0, 5, 20)   # Creates vase-like shape
}
```

### Sweep
```krystal
sweep(path) {
    profile_shape
}
```
- Extrudes profile along path
- Path: curve, spline, or arc
- Example:
```krystal
sweep(spline((0,0,0), (10,5,0), (20,0,5), "bezier")) {
    circle(0, 0, 2)
}
```

### Loft
```krystal
loft {
    profile1
    profile2
    profile3
}
```
- Interpolates between multiple profiles
- Creates smooth transition
- Example:
```krystal
loft {
    circle(0, 0, 5)
    polygon(0, 0, 4, 4)
    circle(0, 0, 3)
}
```

### Shell
```krystal
shell(thickness)
```
- Hollows out solid
- Leaves wall of specified thickness
- Example: `shell(2)`

### Offset
```krystal
offset(distance)
```
- Expands or contracts faces
- Positive: expand, Negative: contract
- Example: `offset(1.5)`

### Fillet
```krystal
fillet(radius, edges("selector"))
```
- Rounds selected edges
- Example: `fillet(2, edges(">Z"))`

### Chamfer
```krystal
chamfer(distance, edges("selector"))
```
- Bevels selected edges
- Example: `chamfer(1, edges("|Z"))`

### Bevel
```krystal
bevel(distance, angle)
```
- Angled chamfer
- Example: `bevel(2, 45)`

### Thread
```krystal
thread(diameter, pitch, length, type)
```
- Creates threaded feature
- Types: `"metric"`, `"imperial"`, `"acme"`, `"buttress"`
- Example: `thread(10, 1.5, 20, "metric")`

## Paths and Curves

### Curve
```krystal
curve((x1,y1,z1), (x2,y2,z2), ...)
```
- Polyline through points

### Spline
```krystal
spline((p1), (p2), (p3), ..., type)
```
- Types: `"interpolate"`, `"approximate"`, `"bezier"`
- Smooth curve through/near points

### Arc
```krystal
arc(center_x, center_y, radius, start_angle, end_angle)
```
- Circular arc segment
- Angles in degrees

## Work Planes

```krystal
plane("XY") {
    # Shapes defined in XY plane
}

plane("XZ") {
    # Shapes defined in XZ plane
}

plane("YZ") {
    # Shapes defined in YZ plane
}

plane("custom"(ox, oy, oz, nx, ny, nz)) {
    # Custom plane at origin (ox,oy,oz) with normal (nx,ny,nz)
}
```

## Hole Patterns

### Linear Holes
```krystal
linear_holes(x, y, z, radius, depth, count, spacing)
```
- Line of holes along X-axis
- Spacing: uniform or non-uniform
- Example:
```krystal
linear_holes(0, 5, 0, 2, 10, 5, uniform(10))
```

### Circular Holes
```krystal
circular_holes(cx, cy, cz, pattern_radius, hole_radius, hole_depth, count)
```
- Holes arranged in circle
- Example:
```krystal
circular_holes(0, 0, 0, 20, 3, 10, 8)
```

### Grid Holes
```krystal
grid_holes(x, y, z, radius, depth, rows, cols, spacing)
```
- Rectangular grid of holes
- Example:
```krystal
grid_holes(0, 0, 0, 2, 10, 4, 6, 15)
```

## Module System

### Module Definition
```krystal
module module_name(param1, param2, param3) {
    # Body uses parameters
    cube(0, 0, 0, param1)
    translate(param1, 0, 0) {
        sphere(0, 0, 0, param2)
    }
}
```
- Reusable parametric components
- Parameters are identifiers
- Resolved at call time

### Module Use
```krystal
use module_name(value1, value2, value3)
```
- Instantiates module with arguments
- Values replace parameters
- Example:
```krystal
module box(w, h, d) {
    rect(0, 0, w, h)
    extrude(d)
}

use box(10, 20, 5)
use box(15, 15, 8)
```

## Constraints

### Alignment Constraints
```krystal
align_x(obj1, obj2)  # Align minimum X coordinates
align_y(obj1, obj2)  # Align minimum Y coordinates  
align_z(obj1, obj2)  # Align minimum Z coordinates
```

### Centering Constraints
```krystal
center_on_x(obj1, obj2)  # Center obj1 on obj2 along X
center_on_y(obj1, obj2)  # Center obj1 on obj2 along Y
center_on_z(obj1, obj2)  # Center obj1 on obj2 along Z
```

### Distance Constraints
```krystal
distance_x(obj1, obj2, value)  # Set X-distance between objects
distance_y(obj1, obj2, value)  # Set Y-distance between objects
distance_z(obj1, obj2, value)  # Set Z-distance between objects
```
- Distance from max of obj1 to min of obj2

### Geometric Constraints
```krystal
tangent(obj1, obj2)         # Make surfaces tangent
perpendicular(obj1, obj2)   # Perpendicular faces
parallel(obj1, obj2)        # Parallel faces
angle(obj1, obj2, degrees)  # Set angle between objects
```

### Validation Constraints
```krystal
no_collision(obj1, obj2)    # Verify no overlap
contained_in(obj1, obj2)    # obj1 fully inside obj2
fixed(obj)                  # Mark as immovable reference
```

## Tolerances

### Dimensional Tolerance
```krystal
tolerance(object_name, plus_value, minus_value)
```
- Specifies acceptable dimension variation
- Example: `tolerance(shaft, 0.02, 0.01)`

### Geometric Tolerance (GD&T)
```krystal
geometric_tolerance(object_name, type, value)
```
- Types: `"flatness"`, `"straightness"`, `"circularity"`, `"cylindricity"`, `"perpendicularity"`, `"parallelism"`, `"angularity"`, `"position"`, `"concentricity"`, `"symmetry"`, `"runout"`
- Example: `geometric_tolerance(plate, "flatness", 0.05)`

### Fit Tolerance
```krystal
fit(obj1, obj2, fit_type)
```
- Types: `"clearance"`, `"transition"`, `"interference"`
- Example: `fit(shaft, hole, "clearance")`

## Naming Objects

```krystal
shape(...) as identifier
```
- Assigns name for later reference
- Required for constraints
- Example:
```krystal
cube(0, 0, 0, 10) as base_block
sphere(5, 5, 10, 4) as top_sphere
center_on_x(top_sphere, base_block)
```

## Code Simplifier

### Protection Markers
Prevent automatic code simplification in regions:
```krystal
# @noformat
# Code in here will not be modified by simplifier
translate(0, 0, 0) {  # Kept even though redundant
    cube(0, 0, 0, 10)
}
# @noformat_end
```

### Simplification Rules
The Rust simplifier applies these transformations:
1. **Remove redundant operations**: `translate(0,0,0)`, `scale(1,1,1)`, `rotate(0,...)
2. **Normalize whitespace**: Consistent spacing, remove excessive blank lines
3. **Simplify expressions**: Evaluate constant expressions (future)
4. **Sort modules**: Organize module definitions (optional)

Protected regions are never modified, even if they contain inefficiencies.

## Complete Examples

### Simple Part
```krystal
# Create a mounting bracket
cube(0, 0, 0, 20) as base
translate(0, 0, 20) {
    cube(0, 0, 0, 5) as top_plate
}

# Add mounting holes
subtract {
    use base
    cylinder(5, 10, 0, 2, 20)
    cylinder(15, 10, 0, 2, 20)
}
```

### Parametric Component
```krystal
# Configurable bearing mount
module bearing_mount(inner_d, outer_d, height, thickness) {
    # Outer housing
    cylinder(0, 0, 0, outer_d/2 + thickness, height) as housing
    
    # Remove bearing cavity
    subtract {
        use housing
        cylinder(0, 0, 0, outer_d/2, height)
    }
}

use bearing_mount(10, 20, 15, 3)
```

### Assembly with Constraints
```krystal
# Two-part assembly
cube(0, 0, 0, 30) as part_a
cube(0, 0, 0, 20) as part_b

# Position part_b relative to part_a
align_x(part_b, part_a)
center_on_y(part_b, part_a)
distance_z(part_a, part_b, 5)

# Verify no collision
no_collision(part_a, part_b)
```

## Implementation Notes

### Current Status
- **Parser**: Implemented in Rust using Pest parser generator
- **Simplifier**: Implemented in Rust with protection markers
- **Geometry Backend**: To be implemented (Python version exists)
- **Constraint Solver**: To be implemented
- **Export**: STL, STEP, DXF formats planned

### Future Extensions
- Variables and assignments
- Conditional logic
- Loops and iteration
- Import/include system
- Material properties
- Assembly metadata
- Bill of materials generation

## Error Handling

Common errors caught by parser:
- Syntax errors in shape definitions
- Missing parameters
- Invalid identifiers
- Unmatched braces
- Circular module dependencies (runtime)
- Constraint conflicts (runtime)
- Geometry errors (runtime)

## Best Practices

1. **Name important objects**: Use `as name` for shapes you'll reference
2. **Modularize**: Create reusable modules for common patterns
3. **Comment complex logic**: Use `#` comments to explain intent
4. **Protect special formatting**: Use `@noformat` when manual spacing matters
5. **Check constraints**: Use validation constraints to catch errors early
6. **Parameterize**: Use module parameters instead of magic numbers
7. **Test incrementally**: Build complex models from simple verified parts

## File Extension

**Primary Extension:** `.krystal`
- Modern, semantic name
- Reflects language name
- Easy to recognize

**Legacy Extension:** `.cadp` 
- Used by Python implementation
- May be supported for compatibility
- New files should use `.krystal`

## Tooling

- **Parser**: Rust implementation using Pest
- **Simplifier**: Rust implementation with protection markers
- **Python Backend**: Legacy implementation for geometry
- **VS Code**: Syntax highlighting (future)
- **Language Server**: IDE support (future)
