use bevy::prelude::*;

#[derive(Resource)]
pub struct RenderSettings {
    pub background: BackgroundTheme,
    pub show_axis: bool,
    pub axis_dotted: bool,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum BackgroundTheme {
    Grey,
    White,
    DarkGrey,
    BlueishGrey,
}

impl Default for RenderSettings {
    fn default() -> Self {
        Self {
            background: BackgroundTheme::Grey,
            show_axis: true,
            axis_dotted: false,
        }
    }
}

impl BackgroundTheme {
    pub fn color(&self) -> Color {
        match self {
            BackgroundTheme::Grey => Color::srgb(0.5, 0.5, 0.5),
            BackgroundTheme::White => Color::srgb(0.95, 0.95, 0.95),
            BackgroundTheme::DarkGrey => Color::srgb(0.2, 0.2, 0.2),
            BackgroundTheme::BlueishGrey => Color::srgb(0.4, 0.45, 0.52),
        }
    }

    pub fn next(&self) -> Self {
        match self {
            BackgroundTheme::Grey => BackgroundTheme::White,
            BackgroundTheme::White => BackgroundTheme::DarkGrey,
            BackgroundTheme::DarkGrey => BackgroundTheme::BlueishGrey,
            BackgroundTheme::BlueishGrey => BackgroundTheme::Grey,
        }
    }
}

pub fn setup_ui(
    mut commands: Commands,
    settings: Res<RenderSettings>,
) {
    // Spawn help text
    commands.spawn(
        TextBundle::from_section(
            get_help_text(),
            TextStyle {
                font_size: 16.0,
                color: Color::WHITE,
                ..default()
            },
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(10.0),
            left: Val::Px(10.0),
            ..default()
        }),
    );

    // Set initial background
    commands.insert_resource(ClearColor(settings.background.color()));
}

fn get_help_text() -> String {
    format!(
        "Krystal 3D Renderer - Controls:\n\
        \n\
        Camera:\n\
        - Right Click + Drag: Orbit\n\
        - Shift + Right Click + Drag: Pan\n\
        - Scroll Wheel: Zoom\n\
        - Arrow Keys: Orbit\n\
        - W/A/S/D: Pan\n\
        - +/-: Zoom\n\
        \n\
        Settings:\n\
        - B: Change Background\n\
        - G: Toggle Axis Grid\n\
        - X: Toggle Axis Style (dotted/solid)\n\
        - ESC: Exit\n\
        \n\
        Interaction:\n\
        - Click: Select Object\n\
        - Drag Selected: Move Object\n"
    )
}

pub fn handle_background_change(
    keyboard: Res<ButtonInput<KeyCode>>,
    mut settings: ResMut<RenderSettings>,
    mut clear_color: ResMut<ClearColor>,
) {
    if keyboard.just_pressed(KeyCode::KeyB) {
        settings.background = settings.background.next();
        clear_color.0 = settings.background.color();
        println!("Background changed to: {:?}", settings.background);
    }
}

pub fn handle_axis_toggle(
    keyboard: Res<ButtonInput<KeyCode>>,
    mut settings: ResMut<RenderSettings>,
) {
    if keyboard.just_pressed(KeyCode::KeyG) {
        settings.show_axis = !settings.show_axis;
        println!("Axis grid: {}", if settings.show_axis { "ON" } else { "OFF" });
    }
    
    if keyboard.just_pressed(KeyCode::KeyX) {
        settings.axis_dotted = !settings.axis_dotted;
        println!("Axis style: {}", if settings.axis_dotted { "DOTTED" } else { "SOLID" });
    }
}
