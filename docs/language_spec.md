# CadPilot Language Specification

This document defines the syntax and semantics of the CadPilot language.

## Basic Concepts

CadPilot is a declarative language for defining 3D CAD models. You describe the shapes and their relationships, and the compiler generates the 3D model.

## Data Types

- **Numbers:** Floating-point numbers are used for dimensions and coordinates (e.g., `10`, `5.5`).
- **Identifiers (CNAME):** Used for module names and parameters (e.g., `my_module`, `width`).

## Basic Shapes

- `rect(x, y, width, height)`: Defines a 2D rectangle at `(x, y)` with the given `width` and `height`. This is primarily used as a base for extrusion.
- `cube(x, y, z, size)`: Defines a cube with its corner at `(x, y, z)` and the given `size` along each axis.
- `sphere(x, y, z, radius)`: Defines a sphere centered at `(x, y, z)` with the given `radius`.
- `cylinder(x, y, z, radius, height)`: Defines a cylinder with its base center at `(x, y, z)`, and the given `radius` and `height`.

## Transformations

Transformations apply to all statements within their curly braces `{}`. They are applied in a hierarchical manner.

- `translate(x, y, z) { ... }`: Moves the enclosed shapes by `(x, y, z)` units.
- `rotate(angle, ax, ay, az) { ... }`: Rotates the enclosed shapes by `angle` degrees around the axis defined by the vector `(ax, ay, az)`.
- `scale(x, y, z) { ... }`: Scales the enclosed shapes by factors `x`, `y`, and `z` along their respective axes.

## Boolean Operations

Boolean operations combine shapes. The operations are performed on the results of the statements within their curly braces.

- `union { ... }`: Combines all enclosed shapes into a single shape.
- `subtract { main_shape ... shapes_to_subtract }`: Subtracts subsequent shapes from the `main_shape`. The first shape defined within the `subtract` block is the main shape, and all subsequent shapes are subtracted from it.

## Extrusion

- `extrude(height)`: Extrudes the previously defined 2D `rect` shape into a 3D object with the given `height`.

## Modules

Modules allow you to define reusable components with parameters.

- `module <name>(<param1>, <param2>, ...) { ... }`: Defines a module with a given `name` and a list of `parameters`. The body of the module contains CadPilot statements.
- `use <name>(<value1>, <value2>, ...)`: Instantiates a module by its `name`, passing `values` for its parameters. The values can be numbers or other identifiers that resolve to numbers.

## Example Usage

```cadp
# Define a custom module for a simple table leg
module table_leg(width, depth, height) {
    cube(0, 0, 0, width)
    translate(0, 0, width) {
        cube(0, 0, 0, depth)
    }
    translate(0, 0, width + depth) {
        cube(0, 0, 0, height - width - depth)
    }
}

# Define a custom module for a table top
module table_top(length, width, thickness) {
    cube(0, 0, 0, length)
    scale(1, width/length, thickness/length) {
        cube(0, 0, 0, length)
    }
}

# Create a table using modules
use table_leg(5, 5, 50) # Front-left leg
translate(95, 0, 0) {
    use table_leg(5, 5, 50) # Front-right leg
}
translate(0, 95, 0) {
    use table_leg(5, 5, 50) # Back-left leg
}
translate(95, 95, 0) {
    use table_leg(5, 5, 50) # Back-right leg
}

translate(0, 0, 50) {
    use table_top(100, 100, 5) # Table top
}

# Example of boolean operation: creating a hole in a cube
union {
    cube(10, 10, 60, 20)
    subtract {
        cube(10, 10, 60, 20)
        cylinder(15, 15, 60, 5, 20) # Hole in the center
    }
}

# Example of a sphere and cylinder
sphere(50, 50, 25, 20)
cylinder(70, 50, 25, 10, 30)
```