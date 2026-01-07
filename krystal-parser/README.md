# Krystal Parser - Rust Implementation

This is the Rust-based parser and code simplifier for the Krystal CAD language.

## Status

**Current Implementation:** Partial
- ✅ Grammar definition complete (Pest)
- ✅ AST data structures defined
- ✅ Parser validates syntax
- ✅ Code simplifier with protection markers
- ⏳ Full AST building (partial/incomplete)
- ⏳ Geometry backend (to be integrated with Python implementation)

## Components

### Parser (`src/parser.rs`)
Validates Krystal syntax using the Pest parser generator.

**Usage:**
```rust
use krystal_parser::KrystalParser;

// Validate syntax
let source = r#"
    cube(0, 0, 0, 10) as box1
    sphere(5, 5, 5, 3)
"#;

match KrystalParser::validate_syntax(source) {
    Ok(()) => println!("Syntax is valid"),
    Err(e) => eprintln!("Error: {}", e),
}
```

### AST (`src/ast.rs`)
Complete Abstract Syntax Tree definitions for all Krystal language constructs.

### Simplifier (`src/simplifier.rs`)
Organizes and simplifies Krystal code while preserving functionality.

**Features:**
- Removes redundant operations (e.g., `translate(0,0,0)`)
- Normalizes whitespace
- Respects protected regions marked with `@noformat`
- Never changes functionality

**Usage:**
```rust
use krystal_parser::{KrystalSimplifier, SimplifierConfig};

let source = r#"
cube(0, 0, 0, 10)


translate(0, 0, 0) {
    sphere(5, 5, 5, 3)
}
"#;

let simplifier = KrystalSimplifier::with_default();
let simplified = simplifier.simplify(source).unwrap();
println!("{}", simplified);
```

**Protection Example:**
```krystal
cube(0, 0, 0, 10)

# @noformat
# This section won't be modified
translate(0, 0, 0) {
    sphere(5, 5, 5, 3)
}
# @noformat_end

sphere(10, 10, 10, 5)
```

## Building

```bash
cargo build
```

## Testing

```bash
cargo test
```

## Future Work

The following components are planned for future implementation:

1. **Complete AST Building**: Full parsing of all statement types into AST
2. **Geometry Backend Integration**: Connect with 3D geometry libraries
3. **Constraint Solver**: Implement constraint resolution system
4. **Module System**: Complete module instantiation and parameter substitution
5. **Error Recovery**: Better error messages and recovery strategies
6. **LSP Support**: Language Server Protocol for IDE integration
7. **WASM Target**: Compile to WebAssembly for browser use

## Grammar

The language grammar is defined in `src/krystal.pest` using the Pest parser syntax.

## Notes

This parser is designed to work alongside the existing Python implementation. The Rust parser provides:
- Fast syntax validation
- Code formatting and simplification
- Foundation for future pure-Rust geometry engine

The Python implementation continues to handle geometry evaluation and rendering.

## License

[To be determined]
