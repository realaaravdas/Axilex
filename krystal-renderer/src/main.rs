use bevy::prelude::*;
use bevy::window::WindowResolution;
use std::env;
use std::fs;

mod geometry;
mod camera;
mod ui;
mod scene;
mod constraints;

use camera::*;
use ui::*;
use scene::*;
use constraints::*;

fn main() {
    // Get command line arguments
    let args: Vec<String> = env::args().collect();
    
    let file_path = if args.len() > 1 {
        args[1].clone()
    } else {
        eprintln!("Usage: krystal-renderer <file.krystal>");
        eprintln!("Example: krystal-renderer examples/hello_krystal.krystal");
        std::process::exit(1);
    };

    // Read the krystal file
    let source = fs::read_to_string(&file_path)
        .unwrap_or_else(|e| {
            eprintln!("Error reading file '{}': {}", file_path, e);
            std::process::exit(1);
        });

    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: format!("Krystal Renderer - {}", file_path),
                resolution: WindowResolution::new(1280.0, 720.0),
                ..default()
            }),
            ..default()
        }))
        .insert_resource(AmbientLight {
            color: Color::WHITE,
            brightness: 200.0,
        })
        .insert_resource(KrystalSource { source, file_path })
        .insert_resource(RenderSettings::default())
        .add_systems(Startup, (setup_scene, setup_ui))
        .add_systems(Update, camera_controls)
        .add_systems(Update, handle_background_change)
        .add_systems(Update, handle_axis_toggle)
        .add_systems(Update, update_axis_grid)
        .add_systems(Update, object_interaction)
        .add_systems(Update, apply_constraints)
        .add_systems(Update, check_collisions)
        .run();
}
