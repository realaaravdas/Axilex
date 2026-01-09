# Krystal Renderer

A 3D interactive renderer for the Krystal CAD language, built with Rust and Bevy.

## Features

- **Real-time 3D rendering** of Krystal CAD models
- **Interactive camera controls** - orbit, pan, and zoom
- **Object interaction** - select and move objects
- **Multiple background themes** - Grey, White, Dark Grey, Blueish Grey
- **Axis grid system** - Solid or dotted axis lines
- **Proper shading and lighting** - PBR materials with multiple light sources
- **Constraint-aware** - Objects maintain their constraints (basic implementation)

## Installation

### Prerequisites

- Rust (latest stable version)
- Graphics drivers supporting Vulkan, DirectX 12, or Metal

### Building

```bash
cd krystal-renderer
cargo build --release
```

## Usage

Run the renderer with a Krystal file:

```bash
cargo run --release -- path/to/file.krystal
```

### Example

```bash
# From the krystal-renderer directory
cargo run --release -- ../examples/hello_krystal.krystal

# Or from the repository root
cd krystal-renderer
cargo run --release -- ../examples/simple_box.cadp
```

## Controls

### Camera

- **Right Click + Drag** - Orbit around the scene
- **Shift + Right Click + Drag** - Pan the camera
- **Middle Mouse + Drag** - Orbit (alternative)
- **Scroll Wheel** - Zoom in/out
- **Arrow Keys** - Orbit (Up/Down/Left/Right)
- **W/A/S/D** - Pan the camera
- **+/-** (or Numpad +/-) - Zoom in/out

### Object Interaction

- **Left Click** - Select an object
- **I/K** - Move selected object forward/backward (Z axis)
- **J/L** - Move selected object left/right (X axis)
- **U/O** - Move selected object up/down (Y axis)

### Settings

- **B** - Cycle through background themes (Grey → White → Dark Grey → Blueish Grey)
- **G** - Toggle axis grid visibility
- **X** - Toggle axis line style (dotted/solid)
- **ESC** - Exit application

## Background Themes

1. **Grey** - Standard grey background (default)
2. **White** - White background for documentation/screenshots
3. **Dark Grey** - Dark theme for low-light environments
4. **Blueish Grey** - Professional blueish-grey tone

## Architecture

### Components

- **geometry.rs** - Parses Krystal code and creates 3D geometry
  - Supports: Cubes, Spheres, Cylinders, Cones
  - Basic shapes rendered with PBR materials
  
- **camera.rs** - Orbit camera system with keyboard and mouse controls
  - Spherical coordinate system for smooth orbiting
  - Multi-input support (mouse, keyboard, scroll)

- **scene.rs** - Scene management and object interaction
  - Multi-light setup for proper shading
  - Axis grid with solid/dotted options
  - Object selection and movement

- **ui.rs** - User interface and settings
  - Help text overlay
  - Background theme switching
  - Axis visibility controls

## Supported Krystal Features

Currently implemented:
- ✅ Basic shapes (cube, sphere, cylinder, cone)
- ✅ Positioning (x, y, z coordinates)
- ✅ Object naming
- ✅ Multiple objects in a scene
- ✅ Sphere-based collision detection
- ✅ Basic constraint system (alignment, distance)

Planned for future releases:
- ⏳ Boolean operations (union, subtract, intersect)
- ⏳ Transformations (translate, rotate, scale, mirror)
- ⏳ Module system
- ⏳ Full constraint solving
- ⏳ Advanced shapes (torus, prism, etc.)
- ⏳ 2D shape extrusion
- ⏳ Material properties
- ⏳ Export functionality (STL, STEP)

## Technical Details

- **Engine**: Bevy 0.14
- **Graphics**: Vulkan/DirectX 12/Metal (via wgpu)
- **Shading**: PBR (Physically Based Rendering)
- **Lighting**: Directional + Point lights for realistic shading
- **Collision Detection**: Sphere-based bounding volumes
- **Constraints**: Real-time constraint solving for object positioning

### Architecture Details

The renderer is built with a modular architecture:

1. **Parser Integration** - Uses the `krystal_parser` crate to parse `.krystal` files into AST
2. **Geometry Generation** - Converts AST nodes into Bevy mesh primitives
3. **ECS Design** - Leverages Bevy's Entity Component System for efficient scene management
4. **Component-Based Interaction** - Objects are entities with components:
   - `KrystalObject` - Core object data (name, moveability)
   - `Selectable` - Marks objects as selectable
   - `Selected` - Marks currently selected object
   - `CollisionRadius` - Bounding sphere for collision detection
   - `Constraint` - Defines positional constraints

### Coordinate System

Krystal uses a right-handed coordinate system with Y-up. The renderer automatically converts to Bevy's coordinate system internally.

### Collision System

Objects have spherical bounding volumes for collision detection. When objects overlap:
1. Calculate distance between centers
2. If distance < sum of radii, objects collide
3. Push objects apart along the collision normal
4. Apply 50% of separation to each object

### Constraint System

Constraints are applied each frame after user input:
- **Fixed** - Object cannot move
- **AlignX/Y/Z** - Align object position with target on specified axis
- **DistanceX/Y/Z** - Maintain fixed distance from target on specified axis

Constraints are enforced in order, allowing for constraint hierarchies.

## Performance

The renderer is optimized for interactive performance:
- Real-time rendering at 60+ FPS for typical CAD models
- Efficient mesh generation using Bevy's built-in primitives
- Low memory footprint

## Troubleshooting

### "Failed to build event loop" error
This occurs when no display is available (e.g., in CI/headless environments). The renderer requires a display to run.

### Black screen or missing objects
Check that your Krystal file syntax is correct. The parser will print errors to the console if it cannot parse the file.

### Poor performance
Try building with `--release` flag for optimized performance:
```bash
cargo build --release
cargo run --release -- your_file.krystal
```

## Development

### Running Tests

```bash
cargo test
```

### Code Structure

```
krystal-renderer/
├── src/
│   ├── main.rs         # Application entry point
│   ├── geometry.rs     # Geometry parsing and creation
│   ├── camera.rs       # Camera controls
│   ├── scene.rs        # Scene setup and interaction
│   └── ui.rs           # UI and settings
└── Cargo.toml
```

## License

Part of the Axilex/Krystal project.
