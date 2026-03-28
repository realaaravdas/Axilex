# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

KRYSTALcad is a Rust-based CAD DSL toolchain. It consists of two crates:
- **`krystal-parser`** — Pest-based parser and AST for `.krystal` files
- **`krystal-renderer`** — Interactive 3D renderer built on Bevy ECS

The language uses `.krystal` files (legacy: `.cadp`). See `docs/LANGUAGE_REFERENCE.md` for the full spec.

## Development Commands

```bash
# Build parser
cd krystal-parser && cargo build

# Build renderer (release recommended for performance)
cd krystal-renderer && cargo build --release

# Run renderer with a file
cd krystal-renderer && cargo run --release -- ../examples/hello_krystal.krystal

# Run parser unit tests
cd krystal-parser && cargo test

# Run a single test by name
cd krystal-parser && cargo test <test_name>
```

## Architecture

### Parser (`krystal-parser`)

**Data flow:** source text → `KrystalParser::parse_program()` → `Program` AST → `KrystalSimplifier`

- `krystal.pest` — Pest grammar (209 lines); the source of truth for language syntax
- `parser.rs` — Wraps Pest, exposes `parse_program()` and `validate_syntax()`; AST building is currently a stub
- `ast.rs` — All AST node types: `Statement`, `Shape` (14 variants), `Transform`, `BooleanOperation`, `Constraint` (16 types), `ToleranceSpec`, `HolePattern`, `Value`
- `simplifier.rs` — Whitespace normalizer; respects `@noformat` / `@noformat_end` markers

### Renderer (`krystal-renderer`)

Uses Bevy's Entity Component System. At startup, `geometry.rs` calls the parser once to read the scene; then interactive systems run each frame.

**Startup path:** `main.rs` → `setup_scene()` → `parse_and_create_geometry()` → spawns Bevy entities

**Per-frame systems:** `camera_controls`, `object_interaction`, `apply_constraints`, `check_collisions`, `handle_background_change`, `update_axis_grid`

**ECS components:** `KrystalObject`, `Selectable`, `Selected`, `CollisionRadius`, `Constraint`, `OrbitCamera`

**Coordinate system:** Krystal uses right-handed XYZ (Y-up); renderer converts to Bevy's XZY at entity spawn time (`geometry.rs:64–68`).

**Implemented shapes:** `cube`, `sphere`, `cylinder`, `cone`. All other AST shapes exist but are not yet rendered.

### Inter-crate dependency

`krystal-renderer/Cargo.toml` references `krystal_parser` as a local path dependency (`../krystal-parser`). Changes to the parser crate's public API will break the renderer.

## Language Syntax (Quick Reference)

```krystal
# Named shape
cube(0, 0, 0, 20) as main_box

# Transformation block
translate(10, 0, 0) {
    sphere(0, 0, 0, 5)
}

# Boolean operation
subtract {
    use main_box
    cylinder(10, 10, 0, 5, 20)
}

# Module definition and use
module bracket(width, height) {
    cube(0, 0, 0, width)
}
use bracket(15, 10)

# Constraints
center_on_x(top_sphere, main_box)
distance_z(main_box, top_sphere, 5)
fixed(main_box)
```

## Interactive Renderer Controls

| Action | Control |
|--------|---------|
| Orbit | Right-click drag or arrow keys |
| Pan (mouse) | Shift + right-click drag |
| Move forward/back | W / S (camera-relative, horizontal) |
| Strafe left/right | A / D |
| Move up/down | Q / E |
| Zoom | Scroll wheel or +/- |
| Select object | Left click |
| Move selected | I/K (Z), J/L (X), U/O (Y) |
| Cycle background | B |
| Toggle axis grid | G |
| Toggle axis style (dots/lines) | X |
| Exit | ESC |

## Implementation Status

The parser's AST is fully defined but `parse_program()` returns a stub `Program`. Only `validate_syntax()` (Pest-based) is complete. The renderer implements shapes, camera, object interaction, sphere-based collision, and basic constraints. Boolean ops, full transforms, module instantiation, and advanced shapes are planned.
