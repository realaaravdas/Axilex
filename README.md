# Axilex - Krystal CAD Language

**Application:** Axilex  
**Language:** Krystal  
**File Extension:** `.krystal` (modern) / `.cadp` (legacy)

A comprehensive CAD language with a custom domain-specific language (DSL) for creating 3D models. Features a Rust-based parser and interactive 3D renderer.

## Features

Krystal provides a powerful, intuitive language for CAD modeling with:

- **50+ Language Features** including shapes, operations, constraints, and tolerances
- **11 Shape Types**: 2D (rect, circle, ellipse, polygon) and 3D (cube, sphere, cylinder, cone, torus, prism, holes)
- **Specialized Components**: Gears, springs, beams, bearings, threads
- **Advanced Operations**: Extrusion, revolve, sweep, loft, shell, fillet, chamfer, bevel
- **Constraints System**: 16 constraint types including alignment, distance, tangent, collision detection
- **Tolerance Specification**: Dimensional, geometric (GD&T), and fit tolerances
- **Hole Patterns**: Linear, circular, and grid patterns with customizable spacing
- **Work Planes**: XY, XZ, YZ, and custom plane definitions
- **Error Handling**: Comprehensive validation with collision detection and constraint checking

## Quick Start

### Installation

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build the renderer
cd krystal-renderer
cargo build --release
```

### Running the Renderer

```bash
cd krystal-renderer
cargo run --release -- ../examples/hello_krystal.krystal
```

### Basic Example

```krystal
# Create a simple box with a hole
cube(0, 0, 0, 20) as box1

# Add a cylindrical hole
subtract {
    use box1
    cylinder(10, 10, 0, 5, 20)
}
```

## File Extensions

- **`.krystal`** - Modern, semantic extension for Krystal language files
- **`.cadp`** - Legacy extension (CAD Pilot), still supported for compatibility

New projects should use `.krystal` extension.

## Documentation

- **[Krystal Specification (Minimal)](docs/KRYSTAL_SPEC_MINIMAL.md)** - Token-optimized spec for AI models (2KB)
- **[Krystal Specification (Training)](docs/KRYSTAL_SPEC_TRAINING.md)** - Comprehensive training spec (16KB)
- **[Language Reference](docs/LANGUAGE_REFERENCE.md)** - Complete language documentation (18KB)
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Quick syntax guide (8KB)
- **[Feature Matrix](docs/FEATURE_MATRIX.md)** - Visual feature overview (10KB)
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details (10KB)
- **[Renderer Documentation](krystal-renderer/README.md)** - 3D renderer usage and controls

## Examples

See the `examples/` directory for comprehensive examples:

- `hello_krystal.krystal` - **NEW!** Modern example using `.krystal` extension
- `complete_language_demo.cadp` - Demonstrates all 50+ language features
- `error_handling_demo.cadp` - Error detection and validation examples
- `simple_box.cadp` - Basic shapes
- `advanced_example.cadp` - Complex assemblies
- `constraints_example.cadp` - Constraint system usage

## Architecture

### Rust Renderer (New!)

**Krystal Renderer** (`krystal-renderer/`)
- Interactive 3D visualization with Bevy game engine
- Real-time rendering with PBR materials
- Camera controls: orbit, pan, zoom
- Object selection and movement
- Multiple background themes
- Axis grid system with dotted/solid options
- Keyboard and mouse controls

**Status:** Core rendering implemented. Basic shape support, interactive camera, and object manipulation functional.

See [krystal-renderer/README.md](krystal-renderer/README.md) for detailed usage.

### Rust Parser

**Krystal Parser** (`krystal-parser/`)
- Fast syntax validation using Pest parser
- Complete AST definitions
- Code simplifier with `@noformat` protection markers
- Foundation for the 3D renderer

**Status:** Parser and AST complete. Geometry evaluation integrated with renderer.

See [krystal-parser/README.md](krystal-parser/README.md) for details.

## Language Features

### Shapes
- 2D: rectangles, circles, ellipses, polygons
- 3D: cubes, spheres, cylinders, cones, tori, prisms
- Specialized: gears, springs, beams, bearings, holes

### Operations (Planned)
- Transformations: translate, rotate, scale, mirror
- Boolean: union, subtract, intersect
- Surface: revolve, sweep, loft, shell, offset, fillet, chamfer, bevel

### Constraints (Planned)
- Alignment: align_x, align_y, align_z
- Centering: center_on_x, center_on_y, center_on_z
- Distance: distance_x, distance_y, distance_z
- Geometric: tangent, perpendicular, parallel, angle
- Validation: no_collision, contained_in, fixed

### Advanced Features (Planned)
- Tolerances (dimensional, geometric GD&T, fit types)
- Hole patterns (linear, circular, grid)
- Work planes (XY, XZ, YZ, custom)
- Module system for reusable components
- Comprehensive error detection and validation

## Development

### Building Rust Components

```bash
# Build parser
cd krystal-parser
cargo build
cargo test

# Build renderer
cd krystal-renderer
cargo build --release
```

### Running Tests

```bash
# Rust parser tests
cd krystal-parser
cargo test

# Renderer can be tested with example files
cd krystal-renderer
cargo run --release -- ../examples/hello_krystal.krystal
```

## Project Structure

```
-Axilex/
├── krystal-renderer/      # 🆕 Rust 3D renderer
│   ├── src/
│   │   ├── main.rs        # Application entry
│   │   ├── geometry.rs    # Geometry parsing
│   │   ├── camera.rs      # Camera controls
│   │   ├── scene.rs       # Scene management
│   │   └── ui.rs          # UI and settings
│   ├── Cargo.toml
│   └── README.md
├── krystal-parser/        # Rust parser
│   ├── src/
│   │   ├── lib.rs         # Main library
│   │   ├── parser.rs      # Pest-based parser
│   │   ├── ast.rs         # AST definitions
│   │   ├── simplifier.rs  # Code simplifier
│   │   └── krystal.pest   # Grammar definition
│   ├── Cargo.toml
│   └── README.md
├── docs/                  # Documentation
│   ├── KRYSTAL_SPEC_MINIMAL.md     # Token-optimized AI spec
│   ├── KRYSTAL_SPEC_TRAINING.md    # Training AI spec
│   ├── LANGUAGE_REFERENCE.md
│   └── ...
├── examples/              # Example files
│   ├── hello_krystal.krystal  # Modern .krystal example
│   ├── *.cadp             # Legacy examples
│   └── ...
└── README.md
```

## Controls (Renderer)

### Camera
- Right Click + Drag: Orbit
- Shift + Right Click + Drag: Pan
- Scroll Wheel: Zoom
- Arrow Keys: Orbit
- W/A/S/D: Pan
- +/-: Zoom

### Interaction
- Left Click: Select Object
- I/K/J/L/U/O: Move Selected Object

### Settings
- B: Change Background
- G: Toggle Axis Grid
- X: Toggle Axis Style (dotted/solid)
- ESC: Exit

## Status

🎉 **Rust Renderer: COMPLETE (v0.1)**

- ✅ Legacy Python code removed
- ✅ Rust parser functional
- ✅ 3D interactive renderer built with Bevy
- ✅ Camera controls (orbit, pan, zoom)
- ✅ Object interaction (selection, movement)
- ✅ Multiple background themes
- ✅ Axis grid (dotted/solid)
- ✅ Proper shading and lighting
- ✅ Basic shape support (cube, sphere, cylinder, cone)
- ⏳ Advanced features (boolean ops, constraints, etc.) planned for future releases

## License

[License information to be added]

