# Building and Running Krystal Renderer

This guide provides detailed instructions for building and running the Krystal 3D renderer.

## Prerequisites

### Required

- **Rust** (latest stable version)
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  source $HOME/.cargo/env
  ```

- **Graphics Drivers**
  - Linux: Vulkan drivers
  - Windows: DirectX 12 or Vulkan
  - macOS: Metal

### System Dependencies (Linux)

On Linux, you may need additional system libraries:

```bash
# Ubuntu/Debian
sudo apt-get install -y libx11-dev libxcursor-dev libxrandr-dev libxi-dev

# Fedora/RHEL
sudo dnf install libX11-devel libXcursor-devel libXrandr-devel libXi-devel

# Arch Linux
sudo pacman -S libx11 libxcursor libxrandr libxi
```

## Building

### Development Build (faster compilation, slower runtime)

```bash
cd krystal-renderer
cargo build
```

### Release Build (slower compilation, optimized runtime)

```bash
cd krystal-renderer
cargo build --release
```

The release build is **highly recommended** for actual use as it provides significantly better performance (3-5x faster).

## Running

### Basic Usage

```bash
# From krystal-renderer directory
cargo run --release -- path/to/file.krystal
```

### Examples

```bash
# Test with simple shapes
cargo run --release -- ../examples/renderer_test.krystal

# Test with hello_krystal example
cargo run --release -- ../examples/hello_krystal.krystal

# Test with simple box
cargo run --release -- ../examples/simple_box.cadp
```

### From Anywhere

After building, you can run the binary directly:

```bash
# Find the binary
cd krystal-renderer/target/release

# Run it
./krystal-renderer ../../examples/renderer_test.krystal
```

## Verifying Installation

Run the tests to ensure everything is working:

```bash
# Test parser (from repository root)
cd krystal-parser
cargo test

# Try running renderer (requires display)
cd ../krystal-renderer
cargo run --release -- ../examples/renderer_test.krystal
```

## Troubleshooting

### "Failed to build event loop" Error

**Problem**: Error message about WAYLAND_DISPLAY or DISPLAY not being set.

**Cause**: No display available (e.g., SSH session without X11 forwarding, CI environment).

**Solution**: 
- Run on a machine with a graphical display
- Use X11 forwarding: `ssh -X user@host`
- On Windows/macOS, this shouldn't be an issue

### Missing System Libraries (Linux)

**Problem**: Errors about missing X11 libraries during build.

**Solution**: Install the development packages listed in "System Dependencies" above.

### Slow Performance

**Problem**: Low FPS or sluggish interaction.

**Solution**: 
- Build with `--release` flag: `cargo build --release`
- Update graphics drivers
- Check that hardware acceleration is enabled

### Black Screen

**Problem**: Window opens but shows nothing.

**Cause**: Invalid or empty Krystal file, or parsing errors.

**Solution**: 
- Check console for error messages
- Verify Krystal file syntax
- Try a known-good example file

### Compilation Errors

**Problem**: Build fails with errors.

**Solution**:
1. Update Rust: `rustup update`
2. Clean build: `cargo clean && cargo build`
3. Check that you're in the correct directory: `krystal-renderer/`

## Performance Tips

1. **Always use release builds** for interactive work:
   ```bash
   cargo run --release -- file.krystal
   ```

2. **Reduce model complexity** if experiencing slowdown:
   - Fewer objects in scene
   - Lower sphere tessellation (modified in code)

3. **Monitor resource usage**:
   ```bash
   # On Linux
   htop
   # Watch GPU usage
   nvidia-smi  # For NVIDIA GPUs
   ```

## Development

### Hot Reloading

For development, you can use `cargo watch` for automatic rebuilding:

```bash
cargo install cargo-watch
cargo watch -x 'run -- ../examples/renderer_test.krystal'
```

### Debug Build Performance

Debug builds are much slower but provide:
- Better error messages
- Panic backtraces
- Debug symbols for `gdb`/`lldb`

For development, debug builds are fine. Switch to release for actual use.

### Custom Features

To add new features, edit the source files in `src/`:
- `geometry.rs` - Shape parsing and rendering
- `camera.rs` - Camera controls
- `scene.rs` - Scene setup and management
- `ui.rs` - User interface
- `constraints.rs` - Constraint and collision systems

After changes, rebuild:
```bash
cargo build --release
```

## Platform-Specific Notes

### Linux

- X11 and Wayland are both supported
- Vulkan is the primary graphics API
- May need to set environment variables for some configurations

### Windows

- DirectX 12 is the default graphics API
- Vulkan also supported
- No special setup required

### macOS

- Metal is the graphics API
- Requires macOS 10.14+ (Mojave or later)
- Apple Silicon (M1/M2) fully supported

## Advanced Configuration

### Custom Window Size

Edit `main.rs` to change default window size:

```rust
resolution: WindowResolution::new(1920.0, 1080.0),
```

### Changing Default Background

Edit `ui.rs` to change the default background theme:

```rust
background: BackgroundTheme::DarkGrey,  // or White, Grey, BlueishGrey
```

### Adjusting Camera Settings

Edit `camera.rs` to modify camera behavior:

```rust
radius: 50.0,  // Default distance from origin
```

## Building for Distribution

To create a standalone executable:

```bash
cargo build --release
strip target/release/krystal-renderer  # Remove debug symbols (Linux/macOS)
```

The binary will be in `target/release/krystal-renderer` (or `.exe` on Windows).

## Next Steps

- Read the [Renderer Documentation](README.md) for usage details
- Explore the [examples/](../examples/) directory
- Check the [Language Reference](../docs/LANGUAGE_REFERENCE.md)
- Contribute improvements via pull requests

## Getting Help

If you encounter issues:
1. Check this troubleshooting guide
2. Review error messages carefully
3. Try with a simple example file
4. Check that all prerequisites are installed
5. Open an issue on GitHub with:
   - Error message
   - Operating system
   - Rust version (`rustc --version`)
   - Steps to reproduce
