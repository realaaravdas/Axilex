use bevy::prelude::*;
use krystal_parser::{KrystalParser, Statement, Shape, Value};

#[derive(Component)]
pub struct KrystalObject {
    pub name: Option<String>,
    pub moveable: bool,
}

#[derive(Component)]
pub struct Selectable;

#[derive(Component)]
pub struct Selected;

pub fn parse_and_create_geometry(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    source: &str,
) {
    // Parse the krystal source
    let program = match KrystalParser::parse_program(source) {
        Ok(prog) => prog,
        Err(e) => {
            eprintln!("Parse error: {}", e);
            return;
        }
    };

    // Create geometry from statements
    for statement in program.statements {
        create_statement_geometry(commands, meshes, materials, &statement);
    }
}

fn create_statement_geometry(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    statement: &Statement,
) {
    match statement {
        Statement::Shape(shape_stmt) => {
            create_shape_geometry(commands, meshes, materials, &shape_stmt.shape, &shape_stmt.name);
        }
        // Other statement types would be handled here
        _ => {
            // For now, we'll just create a simple placeholder for other statement types
        }
    }
}

fn create_shape_geometry(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    shape: &Shape,
    name: &Option<String>,
) {
    let (mesh, transform, color) = match shape {
        Shape::Cube { x, y, z, size } => {
            let pos = Vec3::new(
                extract_value(x),
                extract_value(z), // Swap Y and Z for Bevy's coordinate system
                extract_value(y),
            );
            let size_val = extract_value(size);
            (
                meshes.add(Cuboid::new(size_val, size_val, size_val)),
                Transform::from_translation(pos),
                Color::srgb(0.3, 0.5, 0.8),
            )
        }
        Shape::Sphere { x, y, z, radius } => {
            let pos = Vec3::new(
                extract_value(x),
                extract_value(z),
                extract_value(y),
            );
            let r = extract_value(radius);
            (
                meshes.add(Sphere::new(r).mesh().ico(32).unwrap()),
                Transform::from_translation(pos),
                Color::srgb(0.8, 0.3, 0.5),
            )
        }
        Shape::Cylinder { x, y, z, radius, height } => {
            let pos = Vec3::new(
                extract_value(x),
                extract_value(z),
                extract_value(y),
            );
            let r = extract_value(radius);
            let h = extract_value(height);
            (
                meshes.add(Cylinder::new(r, h)),
                Transform::from_translation(pos),
                Color::srgb(0.5, 0.8, 0.3),
            )
        }
        Shape::Cone { x, y, z, bottom_radius, top_radius: _, height } => {
            let pos = Vec3::new(
                extract_value(x),
                extract_value(z),
                extract_value(y),
            );
            let r = extract_value(bottom_radius);
            let h = extract_value(height);
            (
                meshes.add(Cylinder::new(r, h)), // Use cylinder for now, cone mesh builder varies by bevy version
                Transform::from_translation(pos),
                Color::srgb(0.8, 0.5, 0.3),
            )
        }
        _ => {
            // Default cube for unsupported shapes
            (
                meshes.add(Cuboid::new(10.0, 10.0, 10.0)),
                Transform::default(),
                Color::srgb(0.5, 0.5, 0.5),
            )
        }
    };

    commands.spawn((
        PbrBundle {
            mesh,
            material: materials.add(StandardMaterial {
                base_color: color,
                metallic: 0.2,
                perceptual_roughness: 0.6,
                ..default()
            }),
            transform,
            ..default()
        },
        KrystalObject {
            name: name.clone(),
            moveable: true,
        },
        Selectable,
    ));
}

fn extract_value(value: &Value) -> f32 {
    match value {
        Value::Number(n) => *n as f32,
        Value::Identifier(_) => 0.0, // Identifiers would need context to resolve
        Value::BinaryOp { .. } => 0.0, // Binary operations would need evaluation
    }
}
