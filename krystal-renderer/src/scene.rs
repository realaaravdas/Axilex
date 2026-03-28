use bevy::prelude::*;
use crate::geometry::*;
use crate::camera::*;
use crate::ui::*;

#[derive(Resource)]
pub struct KrystalSource {
    pub source: String,
    pub file_path: String,
}

#[derive(Component)]
pub struct AxisGrid;

pub fn setup_scene(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    source: Res<KrystalSource>,
    settings: Res<RenderSettings>,
) {
    // Setup camera
    setup_camera(&mut commands);

    // Setup lighting
    commands.spawn(DirectionalLightBundle {
        directional_light: DirectionalLight {
            illuminance: 10000.0,
            shadows_enabled: true,
            ..default()
        },
        transform: Transform::from_xyz(10.0, 20.0, 10.0)
            .looking_at(Vec3::ZERO, Vec3::Y),
        ..default()
    });

    // Additional lights for better shading
    commands.spawn(PointLightBundle {
        point_light: PointLight {
            intensity: 2000.0,
            range: 100.0,
            ..default()
        },
        transform: Transform::from_xyz(-10.0, 15.0, -10.0),
        ..default()
    });

    commands.spawn(PointLightBundle {
        point_light: PointLight {
            intensity: 1500.0,
            range: 100.0,
            ..default()
        },
        transform: Transform::from_xyz(10.0, 10.0, 15.0),
        ..default()
    });

    // Parse and create geometry from Krystal source
    parse_and_create_geometry(&mut commands, &mut meshes, &mut materials, &source.source);

    // Create axis grid
    if settings.show_axis {
        create_axis_grid(&mut commands, &mut meshes, &mut materials, settings.axis_dotted);
    }
}

fn create_axis_grid(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    dotted: bool,
) {
    let grid_size = 50.0;
    let grid_spacing = 5.0;
    let line_count = (grid_size / grid_spacing) as i32;

    if dotted {
        // Place a small dot at every grid intersection point on the XZ plane
        let dot_mesh = meshes.add(Sphere::new(1.0).mesh().ico(1).unwrap());
        let dot_material = materials.add(StandardMaterial {
            base_color: Color::srgb(0.35, 0.35, 0.35),
            unlit: true,
            ..default()
        });
        for i in -line_count..=line_count {
            for j in -line_count..=line_count {
                let x = i as f32 * grid_spacing;
                let z = j as f32 * grid_spacing;
                commands.spawn((
                    PbrBundle {
                        mesh: dot_mesh.clone(),
                        material: dot_material.clone(),
                        transform: Transform::from_translation(Vec3::new(x, 0.0, z))
                            .with_scale(Vec3::splat(0.08)),
                        ..default()
                    },
                    AxisGrid,
                ));
            }
        }
    } else {
        // Solid grid lines on the XZ plane
        for i in -line_count..=line_count {
            let offset = i as f32 * grid_spacing;
            spawn_axis_line(
                commands, meshes, materials,
                Vec3::new(-grid_size, 0.0, offset),
                Vec3::new(grid_size, 0.0, offset),
                Color::srgb(0.22, 0.22, 0.22),
            );
            spawn_axis_line(
                commands, meshes, materials,
                Vec3::new(offset, 0.0, -grid_size),
                Vec3::new(offset, 0.0, grid_size),
                Color::srgb(0.22, 0.22, 0.22),
            );
        }
    }

    // Main axes — all three share origin (0,0,0) so they intersect correctly
    // X axis - Red
    spawn_axis_line(
        commands, meshes, materials,
        Vec3::new(0.0, 0.0, 0.0),
        Vec3::new(grid_size, 0.0, 0.0),
        Color::srgb(0.9, 0.15, 0.15),
    );
    // Y axis - Green
    spawn_axis_line(
        commands, meshes, materials,
        Vec3::new(0.0, 0.0, 0.0),
        Vec3::new(0.0, grid_size, 0.0),
        Color::srgb(0.15, 0.9, 0.15),
    );
    // Z axis - Blue
    spawn_axis_line(
        commands, meshes, materials,
        Vec3::new(0.0, 0.0, 0.0),
        Vec3::new(0.0, 0.0, grid_size),
        Color::srgb(0.15, 0.15, 0.9),
    );
}

fn spawn_axis_line(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    start: Vec3,
    end: Vec3,
    color: Color,
) {
    let direction = end - start;
    let length = direction.length();
    if length < 1e-6 {
        return;
    }
    let midpoint = start + direction * 0.5;

    // Bevy's Cylinder is aligned along Y by default.
    // Rotate from Y to the line's direction so each axis points correctly.
    let rotation = Quat::from_rotation_arc(Vec3::Y, direction.normalize());

    commands.spawn((
        PbrBundle {
            mesh: meshes.add(Cylinder::new(0.1, length)),
            material: materials.add(StandardMaterial {
                base_color: color,
                unlit: true,
                ..default()
            }),
            transform: Transform::from_translation(midpoint).with_rotation(rotation),
            ..default()
        },
        AxisGrid,
    ));
}

pub fn update_axis_grid(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    settings: Res<RenderSettings>,
    axis_query: Query<Entity, With<AxisGrid>>,
) {
    if settings.is_changed() {
        // Remove old axis grid
        for entity in axis_query.iter() {
            commands.entity(entity).despawn();
        }

        // Recreate if enabled
        if settings.show_axis {
            create_axis_grid(&mut commands, &mut meshes, &mut materials, settings.axis_dotted);
        }
    }
}

pub fn object_interaction(
    mut commands: Commands,
    mouse_button: Res<ButtonInput<MouseButton>>,
    keyboard: Res<ButtonInput<KeyCode>>,
    windows: Query<&Window>,
    camera_query: Query<(&Camera, &GlobalTransform)>,
    mut object_query: Query<(Entity, &mut Transform, &KrystalObject, Option<&Selected>), With<Selectable>>,
) {
    let window = windows.single();
    let (camera, camera_transform) = camera_query.single();

    // Handle selection
    if mouse_button.just_pressed(MouseButton::Left) {
        if let Some(cursor_pos) = window.cursor_position() {
            if let Some(ray) = camera.viewport_to_world(camera_transform, cursor_pos) {
                // Simple raycast - in production would use bevy_mod_picking
                let mut closest_distance = f32::MAX;
                let mut closest_entity = None;

                for (entity, transform, _obj, _selected) in object_query.iter() {
                    let distance = ray.origin.distance(transform.translation);
                    if distance < closest_distance && distance < 50.0 {
                        closest_distance = distance;
                        closest_entity = Some(entity);
                    }
                }

                // Deselect all
                for (entity, _transform, _obj, selected) in object_query.iter() {
                    if selected.is_some() {
                        commands.entity(entity).remove::<Selected>();
                    }
                }

                // Select closest
                if let Some(entity) = closest_entity {
                    commands.entity(entity).insert(Selected);
                }
            }
        }
    }

    // Handle movement of selected objects
    for (_entity, mut transform, obj, selected) in object_query.iter_mut() {
        if selected.is_some() && obj.moveable {
            let move_speed = 0.5;
            
            if keyboard.pressed(KeyCode::KeyI) {
                transform.translation.z -= move_speed;
            }
            if keyboard.pressed(KeyCode::KeyK) {
                transform.translation.z += move_speed;
            }
            if keyboard.pressed(KeyCode::KeyJ) {
                transform.translation.x -= move_speed;
            }
            if keyboard.pressed(KeyCode::KeyL) {
                transform.translation.x += move_speed;
            }
            if keyboard.pressed(KeyCode::KeyU) {
                transform.translation.y += move_speed;
            }
            if keyboard.pressed(KeyCode::KeyO) {
                transform.translation.y -= move_speed;
            }
        }
    }
}
