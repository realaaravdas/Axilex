# KRYSTALcad Complete Language Reference

## Table of Contents
1. [Basic 2D Shapes](#basic-2d-shapes)
2. [Basic 3D Shapes](#basic-3d-shapes)
3. [Negative Space & Holes](#negative-space--holes)
4. [Specialized Components](#specialized-components)
5. [Transformations](#transformations)
6. [Boolean Operations](#boolean-operations)
7. [Extrusion & Surface Operations](#extrusion--surface-operations)
8. [Curves & Paths](#curves--paths)
9. [Work Planes](#work-planes)
10. [Hole Patterns](#hole-patterns)
11. [Constraints](#constraints)
12. [Tolerances](#tolerances)
13. [Module System](#module-system)
14. [Error Handling](#error-handling)

---

## Basic 2D Shapes

### Rectangle
```cadp
rect(x, y, width, height)
```
Creates a 2D rectangle at position (x, y) with specified width and height.

**Example:**
```cadp
rect(0, 0, 10, 5)
```

### Circle
```cadp
circle(x, y, radius)
```
Creates a 2D circle at position (x, y) with specified radius.

**Example:**
```cadp
circle(10, 10, 5)
```

### Ellipse
```cadp
ellipse(x, y, major_radius, minor_radius)
```
Creates an ellipse centered at (x, y) with major and minor radii.

**Example:**
```cadp
ellipse(20, 20, 8, 4)
```

### Polygon
```cadp
polygon(x, y, radius, sides)
```
Creates a regular polygon centered at (x, y) with specified radius and number of sides.

**Example:**
```cadp
polygon(30, 30, 5, 6)  # Creates a hexagon
```

---

## Basic 3D Shapes

### Cube
```cadp
cube(x, y, z, size)
```
Creates a cube at position (x, y, z) with specified size.

**Example:**
```cadp
cube(0, 0, 0, 10) as box1
```

### Sphere
```cadp
sphere(x, y, z, radius)
```
Creates a sphere centered at (x, y, z) with specified radius.

**Example:**
```cadp
sphere(20, 20, 20, 5) as ball1
```

### Cylinder
```cadp
cylinder(x, y, z, radius, height)
```
Creates a cylinder at position (x, y, z) with specified radius and height.

**Example:**
```cadp
cylinder(0, 0, 0, 5, 20) as cyl1
```

### Cone
```cadp
cone(x, y, z, bottom_radius, top_radius, height)
```
Creates a truncated cone (frustum) at position (x, y, z).

**Example:**
```cadp
cone(0, 0, 0, 10, 5, 20) as cone1
```

### Torus
```cadp
torus(x, y, z, major_radius, minor_radius)
```
Creates a torus (donut shape) centered at (x, y, z).

**Example:**
```cadp
torus(0, 0, 0, 10, 2) as torus1
```

### Prism
```cadp
prism(x, y, z, radius, sides, height)
```
Creates a prism with a regular polygonal base.

**Example:**
```cadp
prism(0, 0, 0, 5, 6, 15) as hex_prism  # Hexagonal prism
```

---

## Negative Space & Holes

### Hole
```cadp
hole(x, y, z, radius, depth)
```
Creates a cylindrical negative space (hole) at position (x, y, z).

**Example:**
```cadp
hole(10, 10, 0, 2, 15)
```

---

## Specialized Components

### Gear
```cadp
gear(x, y, z, module, teeth, pressure_angle, height)
```
Creates an involute spur gear.

**Parameters:**
- `module`: Gear module (size of teeth)
- `teeth`: Number of teeth
- `pressure_angle`: Pressure angle in degrees (typically 20°)
- `height`: Gear thickness

**Example:**
```cadp
gear(0, 0, 0, 2, 24, 20, 10) as gear1
```

### Spring
```cadp
spring(x, y, z, radius, wire_diameter, coils, pitch)
```
Creates a helical coil spring.

**Parameters:**
- `radius`: Spring radius (center to wire center)
- `wire_diameter`: Diameter of the spring wire
- `coils`: Number of coils
- `pitch`: Distance between coils (vertical spacing)

**Example:**
```cadp
spring(0, 0, 0, 10, 2, 8, 5) as spring1
```

### Beam
```cadp
beam(x, y, z, length, width, type)
```
Creates structural beams of various cross-sections.

**Types:**
- `"i"`: I-beam
- `"t"`: T-beam
- `"l"`: L-beam (angle)
- `"c"`: C-beam (channel)
- `"box"`: Box beam (hollow rectangular)

**Example:**
```cadp
beam(0, 0, 0, 100, 10, "i") as support_beam
```

### Bearing
```cadp
bearing(x, y, z, inner_diameter, outer_diameter, width)
```
Creates a bearing representation (ball or roller bearing).

**Example:**
```cadp
bearing(0, 0, 0, 10, 22, 7) as bearing608  # 608 bearing
```

---

## Transformations

### Translate
```cadp
translate(x, y, z) {
    # Objects to translate
}
```
Moves objects by the specified offset.

**Example:**
```cadp
translate(10, 20, 5) {
    cube(0, 0, 0, 5)
}
```

### Rotate
```cadp
rotate(angle, axis_x, axis_y, axis_z) {
    # Objects to rotate
}
```
Rotates objects by the specified angle (degrees) around the given axis.

**Example:**
```cadp
rotate(45, 0, 0, 1) {  # Rotate 45° around Z-axis
    cube(0, 0, 0, 10)
}
```

### Scale
```cadp
scale(x, y, z) {
    # Objects to scale
}
```
Scales objects by the specified factors.

**Example:**
```cadp
scale(2, 1, 0.5) {
    cube(0, 0, 0, 10)
}
```

### Mirror
```cadp
mirror(normal_x, normal_y, normal_z) {
    # Objects to mirror
}
```
Mirrors objects across a plane defined by the normal vector.

**Example:**
```cadp
mirror(1, 0, 0) {  # Mirror across YZ plane
    cube(0, 0, 0, 10)
}
```

---

## Boolean Operations

### Union
```cadp
union {
    # Objects to combine
}
```
Combines multiple objects into a single object.

**Example:**
```cadp
union {
    cube(0, 0, 0, 10)
    sphere(5, 5, 5, 8)
}
```

### Subtract
```cadp
subtract {
    # Base object (first)
    # Objects to subtract (remaining)
}
```
Subtracts all subsequent objects from the first object.

**Example:**
```cadp
subtract {
    cube(0, 0, 0, 20)
    sphere(10, 10, 10, 8)
    cylinder(10, 10, 0, 3, 20)
}
```

### Intersect
```cadp
intersect {
    # Objects to intersect
}
```
Creates an object from the common volume of all objects.

**Example:**
```cadp
intersect {
    cube(0, 0, 0, 20)
    sphere(10, 10, 10, 12)
}
```

---

## Extrusion & Surface Operations

### Extrude
```cadp
extrude(height) [option]
```
Extrudes a 2D shape into 3D.

**Options:**
- (none): Standard extrusion
- `cone`: Tapered extrusion
- `dome`: Dome-shaped extrusion
- `hemisphere`: Hemispherical extrusion

**Examples:**
```cadp
# Standard extrusion
rect(0, 0, 10, 10)
extrude(15)

# Conical extrusion
circle(20, 0, 5)
extrude(20) cone

# Dome extrusion
circle(40, 0, 5)
extrude(10) dome
```

### Revolve
```cadp
revolve(axis_x, axis_y, axis_z, angle) {
    # 2D profile to revolve
}
```
Revolves a 2D profile around an axis.

**Example:**
```cadp
revolve(0, 1, 0, 360) {  # Revolve around Y-axis
    rect(5, 0, 10, 20)
}
```

### Sweep
```cadp
sweep(path) {
    # Cross-section profile
}
```
Sweeps a profile along a path.

**Example:**
```cadp
sweep(spline((0,0,0), (10,10,0), (20,5,5), "bezier")) {
    circle(0, 0, 2)
}
```

### Loft
```cadp
loft {
    # Profile 1
    # Profile 2
    # ... Profile N
}
```
Blends between multiple profiles.

**Example:**
```cadp
loft {
    circle(0, 0, 5)
    translate(0, 0, 20) {
        rect(-3, -3, 6, 6)
    }
}
```

### Shell
```cadp
shell(thickness)
```
Hollows out a solid object, leaving walls of specified thickness.

**Example:**
```cadp
cube(0, 0, 0, 20)
shell(2)
```

### Offset
```cadp
offset(distance)
```
Expands (positive) or contracts (negative) a shape.

**Example:**
```cadp
cube(0, 0, 0, 10)
offset(2)  # Expand by 2 units
```

### Fillet
```cadp
fillet(radius, edge_spec)
```
Rounds edges with a specified radius.

**Example:**
```cadp
cube(0, 0, 0, 10)
fillet(2, edges("all"))
```

### Chamfer
```cadp
chamfer(distance, edge_spec)
```
Bevels edges at 45° with specified distance.

**Example:**
```cadp
cube(0, 0, 0, 10)
chamfer(2, edges("top"))
```

### Bevel
```cadp
bevel(distance, angle)
```
Bevels edges at a specified angle.

**Example:**
```cadp
cube(0, 0, 0, 10)
bevel(2, 30)
```

### Thread
```cadp
thread(diameter, pitch, length, type)
```
Creates helical threads on a cylindrical surface.

**Types:**
- `"metric"`: ISO metric threads
- `"imperial"`: Unified Thread Standard
- `"acme"`: ACME threads (trapezoidal)
- `"buttress"`: Buttress threads

**Example:**
```cadp
cylinder(0, 0, 0, 5, 30)
thread(10, 1.5, 25, "metric")
```

---

## Curves & Paths

### Arc
```cadp
arc(center_x, center_y, radius, start_angle, end_angle)
```
Creates a circular arc.

**Example:**
```cadp
arc(0, 0, 10, 0, 180)  # Semicircle
```

### Curve
```cadp
curve((x1,y1,z1), (x2,y2,z2), ...)
```
Creates a curve through specified points.

**Example:**
```cadp
curve((0,0,0), (10,10,5), (20,5,10))
```

### Spline
```cadp
spline((x1,y1,z1), (x2,y2,z2), ..., type)
```
Creates a spline curve through or near points.

**Types:**
- `"interpolate"`: Passes through all points
- `"approximate"`: Smoothly approximates points
- `"bezier"`: Bezier curve using control points

**Example:**
```cadp
spline((0,0,0), (10,10,0), (20,5,5), (30,15,10), "interpolate")
```

---

## Work Planes

```cadp
plane(type) {
    # Objects to create on this plane
}
```

**Standard Planes:**
- `"XY"`: Default horizontal plane
- `"XZ"`: Front vertical plane
- `"YZ"`: Side vertical plane
- `"custom"(ox, oy, oz, nx, ny, nz)`: Custom plane with origin and normal

**Examples:**
```cadp
plane("XZ") {
    rect(0, 0, 10, 10)
    extrude(5)
}

plane("custom"(10, 10, 10, 1, 1, 0)) {
    circle(0, 0, 5)
}
```

---

## Hole Patterns

### Linear Holes
```cadp
linear_holes(x, y, z, radius, depth, count, spacing)
```
Creates a line of holes.

**Spacing:**
- `uniform(distance)`: Equal spacing
- `non_uniform(d1, d2, ..., dn)`: Custom spacing

**Examples:**
```cadp
# Uniform spacing
linear_holes(0, 0, 0, 3, 15, 5, uniform(20))

# Non-uniform spacing
linear_holes(0, 0, 0, 3, 15, 4, non_uniform(10, 20, 15, 25))
```

### Circular Holes
```cadp
circular_holes(cx, cy, cz, pattern_radius, hole_radius, hole_depth, count)
```
Creates holes arranged in a circle.

**Example:**
```cadp
circular_holes(50, 50, 0, 30, 4, 20, 8)  # 8 holes in a circle
```

### Grid Holes
```cadp
grid_holes(x, y, z, radius, depth, rows, cols, spacing)
```
Creates holes in a rectangular grid pattern.

**Example:**
```cadp
grid_holes(0, 0, 0, 2, 10, 4, 5, 15)  # 4x5 grid
```

---

## Constraints

Constraints define spatial relationships between named objects.

### Alignment Constraints

Align edges of objects:
```cadp
align_x(obj1, obj2)  # Align min X edges
align_y(obj1, obj2)  # Align min Y edges
align_z(obj1, obj2)  # Align min Z edges
```

### Centering Constraints

Center objects along axes:
```cadp
center_on_x(obj1, obj2)  # Center obj1 on obj2's X
center_on_y(obj1, obj2)  # Center obj1 on obj2's Y
center_on_z(obj1, obj2)  # Center obj1 on obj2's Z
```

### Distance Constraints

Set specific distances between objects:
```cadp
distance_x(obj1, obj2, distance)  # X-axis distance
distance_y(obj1, obj2, distance)  # Y-axis distance
distance_z(obj1, obj2, distance)  # Z-axis distance
```

### Fixed Constraint

Mark an object as immovable:
```cadp
fixed(obj1)
```

### Geometric Constraints

```cadp
tangent(obj1, obj2)          # Objects touch but don't overlap
perpendicular(obj1, obj2)     # Objects are perpendicular
parallel(obj1, obj2)          # Objects are parallel
angle(obj1, obj2, degrees)    # Specific angle between objects
```

### Validation Constraints

```cadp
no_collision(obj1, obj2)      # Ensure objects don't overlap
contained_in(obj1, obj2)      # obj1 must be inside obj2
```

**Example:**
```cadp
cube(0, 0, 0, 10) as box1
cube(20, 0, 0, 8) as box2

fixed(box1)
distance_x(box1, box2, 5)
no_collision(box1, box2)
```

---

## Tolerances

### Dimensional Tolerance
```cadp
tolerance(object, plus_tolerance, minus_tolerance)
```
Specifies dimensional tolerances (±).

**Example:**
```cadp
cube(0, 0, 0, 10) as part1
tolerance(part1, 0.1, 0.05)  # +0.1/-0.05 mm
```

### Geometric Tolerance
```cadp
geometric_tolerance(object, type, value)
```
Specifies geometric dimensioning and tolerancing (GD&T).

**Types:**
- `"flatness"`: Surface flatness
- `"straightness"`: Edge straightness
- `"circularity"`: Roundness
- `"cylindricity"`: Cylindrical form
- `"perpendicularity"`: Perpendicular deviation
- `"parallelism"`: Parallel deviation
- `"angularity"`: Angular deviation
- `"position"`: True position
- `"concentricity"`: Concentricity
- `"symmetry"`: Symmetry
- `"runout"`: Runout tolerance

**Example:**
```cadp
cylinder(0, 0, 0, 5, 20) as shaft1
geometric_tolerance(shaft1, "cylindricity", 0.01)
```

### Fit Tolerance
```cadp
fit(object1, object2, fit_type)
```
Specifies the type of fit between mating parts.

**Fit Types:**
- `"clearance"`: Loose fit, parts don't touch
- `"transition"`: May have slight clearance or interference
- `"interference"`: Tight fit, parts press together

**Example:**
```cadp
cylinder(0, 0, 0, 10, 20) as shaft
cylinder(0, 0, 0, 10.1, 20) as hole
fit(shaft, hole, "clearance")
```

---

## Module System

Modules allow you to create reusable parametric components.

### Defining a Module
```cadp
module name(param1, param2, ...) {
    # Module body
}
```

### Using a Module
```cadp
use name(value1, value2, ...)
```

**Example:**
```cadp
# Define a bolt module
module bolt(diameter, length, head_diameter) {
    union {
        cylinder(0, 0, 0, head_diameter/2, diameter)
        translate(0, 0, diameter) {
            cylinder(0, 0, 0, diameter/2, length)
            thread(diameter, diameter*0.15, length, "metric")
        }
    }
}

# Use the bolt module
use bolt(10, 50, 16)
use bolt(6, 30, 10)
```

**Advanced Module Example:**
```cadp
module gear_assembly(module_val, teeth1, teeth2) {
    # Calculate center distance
    # center_distance = module_val * (teeth1 + teeth2) / 2
    
    gear(0, 0, 0, module_val, teeth1, 20, 10) as gear1
    translate(module_val * (teeth1 + teeth2) / 2, 0, 0) {
        gear(0, 0, 0, module_val, teeth2, 20, 10) as gear2
    }
    
    # Ensure gears mesh properly
    tangent(gear1, gear2)
}

use gear_assembly(2, 20, 30)
```

---

## Error Handling

The language includes validation and error detection:

### Constraint Conflicts

The system detects when constraints cannot be satisfied:

```cadp
cube(0, 0, 0, 10) as obj1
cube(5, 5, 5, 10) as obj2

# ERROR: Objects already overlap
no_collision(obj1, obj2)
```

### Impossible Geometry

```cadp
cube(0, 0, 0, 10) as container
cube(20, 20, 20, 5) as part

# ERROR: part is outside container
contained_in(part, container)
```

### Fit Violations

```cadp
cylinder(0, 0, 0, 10, 20) as shaft
cylinder(0, 0, 0, 9, 20) as hole

# ERROR: Shaft diameter > hole diameter (clearance fit impossible)
fit(shaft, hole, "clearance")
```

### Tolerance Stack-up Issues

```cadp
cube(0, 0, 0, 10) as part1
cube(11, 0, 0, 10) as part2

tolerance(part1, 0.5, 0.5)
tolerance(part2, 0.5, 0.5)

# WARNING: Tolerance stack-up may cause collision
no_collision(part1, part2)
```

### Invalid Dimensions

```cadp
# ERROR: Negative dimensions
cube(0, 0, 0, -10)

# ERROR: Zero radius
sphere(0, 0, 0, 0)

# ERROR: Invalid gear parameters
gear(0, 0, 0, 2, 5, 20, 10)  # Too few teeth for module
```

---

## Complete Assembly Example

Here's a complete example combining multiple features:

```cadp
# Parametric motor mount assembly

# Base plate with mounting holes
module base_plate(width, height, thickness, hole_count) {
    subtract {
        cube(0, 0, 0, width)
        scale(1, height/width, thickness/width) {
            cube(0, 0, 0, width)
        }
        
        # Corner mounting holes
        linear_holes(5, 5, 0, 2, thickness, 2, uniform(width-10))
        translate(0, height-5, 0) {
            linear_holes(5, 0, 0, 2, thickness, 2, uniform(width-10))
        }
    }
}

# Motor mounting bracket
module motor_bracket(motor_diameter, mounting_height) {
    subtract {
        union {
            # Base
            cube(0, 0, 0, motor_diameter + 20)
            scale(1, 0.3, 0.5) {
                cube(0, 0, 0, motor_diameter + 20)
            }
            
            # Side walls
            translate(0, 0, 0) {
                cube(0, 0, 0, 10)
                scale(1, (motor_diameter + 20)/10, mounting_height/10) {
                    cube(0, 0, 0, 10)
                }
            }
            
            translate(motor_diameter + 10, 0, 0) {
                cube(0, 0, 0, 10)
                scale(1, (motor_diameter + 20)/10, mounting_height/10) {
                    cube(0, 0, 0, 10)
                }
            }
        }
        
        # Motor shaft hole
        translate((motor_diameter + 20)/2, (motor_diameter + 20)*0.15, 0) {
            cylinder(0, 0, 0, motor_diameter/2 + 0.5, mounting_height)
        }
        
        # Bearing seat
        translate((motor_diameter + 20)/2, (motor_diameter + 20)*0.15, mounting_height - 10) {
            bearing(0, 0, 0, motor_diameter/2, motor_diameter/2 + 8, 7)
        }
    }
}

# Assemble the motor mount
use base_plate(100, 80, 5, 4) as base

translate(0, 0, 5) {
    use motor_bracket(42, 50) as bracket
}

# Add constraints
fixed(base)
align_x(bracket, base)
center_on_x(bracket, base)

# Add tolerances
tolerance(base, 0.1, 0.1)
geometric_tolerance(base, "flatness", 0.05)

fit(bracket, base, "clearance")
no_collision(bracket, base)
```

---

## Tips and Best Practices

1. **Name Important Objects**: Use `as name` to reference objects in constraints
2. **Use Modules**: Create reusable parametric components
3. **Apply Constraints Incrementally**: Start with `fixed()` on reference objects
4. **Check Tolerances Early**: Define tolerances before assembly
5. **Use Hole Patterns**: Instead of individual holes for efficiency
6. **Validate Fits**: Use `fit()` constraints for mating parts
7. **Prevent Collisions**: Use `no_collision()` for moving assemblies
8. **Document Assumptions**: Use comments to explain design intent

---

## Language Syntax Summary

```cadp
# Comments start with #

# Variable naming (for objects)
shape(...) as object_name

# Expressions support basic arithmetic
value: number | variable | (expression)
operators: + - * /

# Blocks use curly braces
transform(...) {
    statements
}

# Modules for reusability
module name(params) {
    statements
}
use name(values)

# Constraints reference named objects
constraint(object1, object2, ...)

# Strings for enums
"string_value"
```

---

This language reference covers all features of the complete KRYSTALcad language. For more examples, see `complete_language_demo.cadp`.
