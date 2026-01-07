# KRYSTALcad Language Quick Reference

## Basic Syntax

```cadp
# Comments start with #

# Create shapes with parameters
shape_name(param1, param2, ...) [as object_name]

# Apply transformations
transform(params) {
    shapes...
}

# Boolean operations
operation {
    shapes...
}

# Define modules (functions)
module name(param1, param2) {
    body...
}

# Use modules
use name(value1, value2)

# Apply constraints
constraint_name(object1, object2, ...)

# Set tolerances
tolerance_spec(object, values...)
```

## 2D Shapes

| Shape | Syntax | Parameters |
|-------|--------|------------|
| Rectangle | `rect(x, y, w, h)` | x, y, width, height |
| Circle | `circle(x, y, r)` | x, y, radius |
| Ellipse | `ellipse(x, y, rx, ry)` | x, y, major_radius, minor_radius |
| Polygon | `polygon(x, y, r, n)` | x, y, radius, sides |

## 3D Shapes

| Shape | Syntax | Parameters |
|-------|--------|------------|
| Cube | `cube(x, y, z, size)` | x, y, z, size |
| Sphere | `sphere(x, y, z, r)` | x, y, z, radius |
| Cylinder | `cylinder(x, y, z, r, h)` | x, y, z, radius, height |
| Cone | `cone(x, y, z, r1, r2, h)` | x, y, z, bottom_r, top_r, height |
| Torus | `torus(x, y, z, R, r)` | x, y, z, major_r, minor_r |
| Prism | `prism(x, y, z, r, n, h)` | x, y, z, radius, sides, height |
| Hole | `hole(x, y, z, r, d)` | x, y, z, radius, depth |

## Specialized Components

| Component | Syntax | Parameters |
|-----------|--------|------------|
| Gear | `gear(x, y, z, m, t, a, h)` | x, y, z, module, teeth, pressure_angle, height |
| Spring | `spring(x, y, z, r, d, n, p)` | x, y, z, radius, wire_dia, coils, pitch |
| Beam | `beam(x, y, z, l, w, type)` | x, y, z, length, width, "i"/"t"/"l"/"c"/"box" |
| Bearing | `bearing(x, y, z, id, od, w)` | x, y, z, inner_dia, outer_dia, width |

## Transformations

| Transform | Syntax | Parameters |
|-----------|--------|------------|
| Translate | `translate(x, y, z) { ... }` | x, y, z offset |
| Rotate | `rotate(a, x, y, z) { ... }` | angle (deg), axis x, y, z |
| Scale | `scale(x, y, z) { ... }` | x, y, z scale factors |
| Mirror | `mirror(x, y, z) { ... }` | normal vector x, y, z |

## Boolean Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| Union | `union { shape1 shape2 ... }` | Combine shapes |
| Subtract | `subtract { base subtract1 ... }` | Subtract from base |
| Intersect | `intersect { shape1 shape2 ... }` | Common volume |

## Extrusion & Surface Operations

| Operation | Syntax | Description |
|-----------|--------|-------------|
| Extrude | `extrude(height)` | Basic extrusion |
| Extrude Cone | `extrude(height) cone` | Tapered extrusion |
| Extrude Dome | `extrude(height) dome` | Dome extrusion |
| Revolve | `revolve(ax, ay, az, angle) { ... }` | Rotate profile around axis |
| Sweep | `sweep(path) { profile }` | Sweep along path |
| Loft | `loft { profile1 profile2 ... }` | Blend between profiles |
| Shell | `shell(thickness)` | Hollow out object |
| Offset | `offset(distance)` | Expand/contract shape |
| Fillet | `fillet(radius, edges("spec"))` | Round edges |
| Chamfer | `chamfer(distance, edges("spec"))` | Bevel edges |
| Bevel | `bevel(distance, angle)` | Bevel at angle |
| Thread | `thread(d, p, l, "type")` | Add threads |

Thread types: `"metric"`, `"imperial"`, `"acme"`, `"buttress"`

## Curves & Paths

| Curve | Syntax | Description |
|-------|--------|-------------|
| Arc | `arc(cx, cy, r, start, end)` | Circular arc |
| Curve | `curve((x1,y1,z1), (x2,y2,z2), ...)` | Curve through points |
| Spline | `spline(...points, "type")` | Spline curve |

Spline types: `"interpolate"`, `"approximate"`, `"bezier"`

## Work Planes

| Plane | Syntax | Description |
|-------|--------|-------------|
| XY | `plane("XY") { ... }` | Horizontal plane |
| XZ | `plane("XZ") { ... }` | Front plane |
| YZ | `plane("YZ") { ... }` | Side plane |
| Custom | `plane("custom"(ox,oy,oz,nx,ny,nz)) { ... }` | Custom plane |

## Hole Patterns

| Pattern | Syntax | Parameters |
|---------|--------|------------|
| Linear | `linear_holes(x, y, z, r, d, n, spacing)` | Position, radius, depth, count, spacing |
| Circular | `circular_holes(cx, cy, cz, R, r, d, n)` | Center, pattern_r, hole_r, depth, count |
| Grid | `grid_holes(x, y, z, r, d, rows, cols, s)` | Position, radius, depth, rows, cols, spacing |

Spacing: `uniform(distance)` or `non_uniform(d1, d2, ...)`

## Constraints

### Alignment
- `align_x(obj1, obj2)` - Align min X edges
- `align_y(obj1, obj2)` - Align min Y edges
- `align_z(obj1, obj2)` - Align min Z edges

### Centering
- `center_on_x(obj1, obj2)` - Center obj1 on obj2's X
- `center_on_y(obj1, obj2)` - Center obj1 on obj2's Y
- `center_on_z(obj1, obj2)` - Center obj1 on obj2's Z

### Distance
- `distance_x(obj1, obj2, dist)` - X-axis distance
- `distance_y(obj1, obj2, dist)` - Y-axis distance
- `distance_z(obj1, obj2, dist)` - Z-axis distance

### Geometric
- `tangent(obj1, obj2)` - Touch but don't overlap
- `perpendicular(obj1, obj2)` - 90° relationship
- `parallel(obj1, obj2)` - Parallel alignment
- `angle(obj1, obj2, degrees)` - Specific angle

### Validation
- `fixed(obj)` - Mark as immovable
- `no_collision(obj1, obj2)` - Ensure no overlap
- `contained_in(obj1, obj2)` - obj1 inside obj2

## Tolerances

### Dimensional
```cadp
tolerance(object, plus, minus)
```
Example: `tolerance(part1, 0.1, 0.05)` means +0.1/-0.05

### Geometric (GD&T)
```cadp
geometric_tolerance(object, "type", value)
```

Types: `"flatness"`, `"straightness"`, `"circularity"`, `"cylindricity"`, 
`"perpendicularity"`, `"parallelism"`, `"angularity"`, `"position"`, 
`"concentricity"`, `"symmetry"`, `"runout"`

### Fit
```cadp
fit(obj1, obj2, "type")
```

Types: 
- `"clearance"` - Loose fit (shaft < hole)
- `"transition"` - May have clearance or interference
- `"interference"` - Tight fit (shaft > hole)

## Module System

```cadp
# Define a reusable module
module bolt(diameter, length) {
    cylinder(0, 0, 0, diameter/2, length) as shaft
    cylinder(0, 0, 0, diameter*0.8, diameter*0.5) as head
    thread(diameter, diameter*0.15, length*0.8, "metric")
}

# Use the module
use bolt(10, 50)
use bolt(8, 40)
```

## Error Handling

The language validates:
- ✓ Collision detection (`no_collision`)
- ✓ Containment checking (`contained_in`)
- ✓ Fit compatibility
- ✓ Dimension validity (no negatives)
- ✓ Enum values (thread types, etc.)
- ✓ Tolerance specifications
- ✓ Constraint conflicts

Errors raised:
- `ConstraintError` - Constraint cannot be satisfied
- `GeometryError` - Invalid geometry parameters
- `ToleranceError` - Invalid tolerance specification

## Expressions

```cadp
# Arithmetic in parameters
cube(10, 20, 30, 5 + 3)
cube(0, 0, 0, 10 * 2)
circle(15 / 3, 20 - 5, 10)

# Using module parameters
module box(width, height) {
    cube(0, 0, 0, width)
    translate(width/2, height/2, 0) {
        sphere(0, 0, 0, width/4)
    }
}
```

## Complete Example

```cadp
# Motor mount assembly

module motor_mount(motor_dia, mount_height) {
    # Base plate
    subtract {
        cube(0, 0, 0, motor_dia + 40)
        
        # Mounting holes (4 corners)
        linear_holes(10, 10, 0, 3, 5, 2, uniform(motor_dia + 20))
        translate(0, motor_dia + 20, 0) {
            linear_holes(10, 0, 0, 3, 5, 2, uniform(motor_dia + 20))
        }
    }
    
    # Motor shaft hole
    translate((motor_dia + 40)/2, (motor_dia + 40)/2, 0) {
        cylinder(0, 0, 0, motor_dia/2 + 0.5, 5) as shaft_hole
        
        # Bearing seat
        translate(0, 0, 3) {
            bearing(0, 0, 0, motor_dia/2, motor_dia/2 + 8, 7) as bearing_seat
        }
    }
}

# Create motor mount
use motor_mount(42, 50) as mount1

# Add tolerances
tolerance(mount1, 0.1, 0.1)
geometric_tolerance(mount1, "flatness", 0.05)
```

## Tips

1. **Name Important Objects**: Use `as name` for constraints
2. **Fix Reference Objects**: Use `fixed(obj)` on base parts
3. **Check Fits**: Use `fit()` for mating parts
4. **Prevent Collisions**: Use `no_collision()` for moving parts
5. **Module Reusability**: Create modules for repeated patterns
6. **Tolerance First**: Set tolerances before constraints
7. **Validate Early**: Use constraints to catch design errors

## File Extension

Save files with `.cadp` extension (CAD Pilot)

## Comments

```cadp
# This is a single-line comment
# Comments are ignored by the parser

cube(0, 0, 0, 10)  # Inline comments work too
```
