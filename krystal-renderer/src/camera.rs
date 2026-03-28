use bevy::prelude::*;
use bevy::input::mouse::{MouseMotion, MouseWheel};

#[derive(Component)]
pub struct OrbitCamera {
    pub focus: Vec3,
    pub radius: f32,
    pub theta: f32,  // Azimuthal angle
    pub phi: f32,    // Polar angle
}

impl Default for OrbitCamera {
    fn default() -> Self {
        Self {
            focus: Vec3::ZERO,
            radius: 50.0,
            theta: 0.0,
            phi: 0.5,
        }
    }
}

pub fn setup_camera(commands: &mut Commands) {
    commands.spawn((
        Camera3dBundle {
            transform: Transform::from_xyz(30.0, 30.0, 30.0)
                .looking_at(Vec3::ZERO, Vec3::Y),
            ..default()
        },
        OrbitCamera::default(),
    ));
}

pub fn camera_controls(
    mut query: Query<(&mut Transform, &mut OrbitCamera)>,
    mut motion_events: EventReader<MouseMotion>,
    mut scroll_events: EventReader<MouseWheel>,
    mouse_button: Res<ButtonInput<MouseButton>>,
    keyboard: Res<ButtonInput<KeyCode>>,
    time: Res<Time>,
) {
    let (mut transform, mut orbit) = query.single_mut();

    // Mouse orbit (right click or middle click)
    if mouse_button.pressed(MouseButton::Right) || mouse_button.pressed(MouseButton::Middle) {
        for event in motion_events.read() {
            orbit.theta += event.delta.x * 0.005;  // positive = cursor right → rotate right
            orbit.phi = (orbit.phi - event.delta.y * 0.005).clamp(0.01, std::f32::consts::PI - 0.01);
        }
    }

    // Mouse pan (shift + right click or shift + middle click)
    if (mouse_button.pressed(MouseButton::Right) || mouse_button.pressed(MouseButton::Middle))
        && (keyboard.pressed(KeyCode::ShiftLeft) || keyboard.pressed(KeyCode::ShiftRight))
    {
        for event in motion_events.read() {
            let right = transform.right();
            let up = Vec3::Y;
            orbit.focus -= right * event.delta.x * 0.05;
            orbit.focus += up * event.delta.y * 0.05;
        }
    }

    // Keyboard orbit
    let rotate_speed = 2.0 * time.delta_seconds();
    if keyboard.pressed(KeyCode::ArrowLeft) {
        orbit.theta += rotate_speed;
    }
    if keyboard.pressed(KeyCode::ArrowRight) {
        orbit.theta -= rotate_speed;
    }
    if keyboard.pressed(KeyCode::ArrowUp) {
        orbit.phi = (orbit.phi - rotate_speed).clamp(0.01, std::f32::consts::PI - 0.01);
    }
    if keyboard.pressed(KeyCode::ArrowDown) {
        orbit.phi = (orbit.phi + rotate_speed).clamp(0.01, std::f32::consts::PI - 0.01);
    }

    // Keyboard movement - FPS-style, relative to camera's horizontal orientation
    let move_speed = 20.0 * time.delta_seconds();
    let fwd = transform.forward();
    let right = transform.right();
    // Project camera forward/right onto the horizontal plane so W/S don't fly up/down
    let horizontal_forward = Vec3::new(fwd.x, 0.0, fwd.z).normalize_or_zero();
    let horizontal_right = Vec3::new(right.x, 0.0, right.z).normalize_or_zero();

    if keyboard.pressed(KeyCode::KeyW) {
        orbit.focus += horizontal_forward * move_speed;
    }
    if keyboard.pressed(KeyCode::KeyS) {
        orbit.focus -= horizontal_forward * move_speed;
    }
    if keyboard.pressed(KeyCode::KeyA) {
        orbit.focus -= horizontal_right * move_speed;
    }
    if keyboard.pressed(KeyCode::KeyD) {
        orbit.focus += horizontal_right * move_speed;
    }
    if keyboard.pressed(KeyCode::KeyQ) {
        orbit.focus += Vec3::Y * move_speed;
    }
    if keyboard.pressed(KeyCode::KeyE) {
        orbit.focus -= Vec3::Y * move_speed;
    }

    // Mouse zoom
    for event in scroll_events.read() {
        orbit.radius = (orbit.radius - event.y * 2.0).max(5.0);
    }

    // Keyboard zoom
    if keyboard.pressed(KeyCode::Equal) || keyboard.pressed(KeyCode::NumpadAdd) {
        orbit.radius = (orbit.radius - 20.0 * time.delta_seconds()).max(5.0);
    }
    if keyboard.pressed(KeyCode::Minus) || keyboard.pressed(KeyCode::NumpadSubtract) {
        orbit.radius += 20.0 * time.delta_seconds();
    }

    // Clear motion events if not used
    if !mouse_button.pressed(MouseButton::Right) && !mouse_button.pressed(MouseButton::Middle) {
        motion_events.clear();
    }

    // Update camera position
    let x = orbit.radius * orbit.phi.sin() * orbit.theta.cos();
    let y = orbit.radius * orbit.phi.cos();
    let z = orbit.radius * orbit.phi.sin() * orbit.theta.sin();

    transform.translation = orbit.focus + Vec3::new(x, y, z);
    transform.look_at(orbit.focus, Vec3::Y);
}
