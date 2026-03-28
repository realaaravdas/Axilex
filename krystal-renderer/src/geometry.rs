use std::collections::HashMap;
use bevy::prelude::*;
use krystal_parser::{
    KrystalParser, Statement, ShapeStatement, Shape, Value, BinaryOperator,
    BooleanOperation, ModuleDefinition, ModuleUse,
};
// Alias to avoid conflict with bevy::prelude::Transform
use krystal_parser::Transform as KTransform;
use crate::constraints::CollisionRadius;

#[derive(Component)]
pub struct KrystalObject {
    pub name: Option<String>,
    pub moveable: bool,
}

#[derive(Component)]
pub struct Selectable;

#[derive(Component)]
pub struct Selected;

// ── Public entry point ────────────────────────────────────────────────────────

pub fn parse_and_create_geometry(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    source: &str,
) {
    let program = match KrystalParser::parse_program(source) {
        Ok(prog) => prog,
        Err(e) => {
            eprintln!("Parse error: {}", e);
            return;
        }
    };

    // First pass: collect all module definitions so `use` statements can look them up.
    let mut modules: HashMap<String, ModuleDefinition> = HashMap::new();
    for stmt in &program.statements {
        if let Statement::ModuleDef(def) = stmt {
            modules.insert(def.name.clone(), def.clone());
        }
    }

    // Second pass: render every non-definition statement.
    for stmt in &program.statements {
        if !matches!(stmt, Statement::ModuleDef(_)) {
            build_geometry(commands, meshes, materials, stmt, Transform::IDENTITY, &modules);
        }
    }
}

// ── Recursive geometry builder ────────────────────────────────────────────────

fn build_geometry(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    stmt: &Statement,
    parent: Transform,
    modules: &HashMap<String, ModuleDefinition>,
) {
    match stmt {
        // ── Direct shape ──────────────────────────────────────────────────────
        Statement::Shape(ss) => {
            spawn_shape(commands, meshes, materials, ss, parent);
        }

        // ── Transformations ───────────────────────────────────────────────────
        // Compute a local Bevy Transform from the Krystal transform, multiply into
        // the parent, then recurse into children.
        Statement::Transform(kt) => {
            let local   = krystal_transform_to_bevy(kt);
            let combined = parent.mul_transform(local);
            for child in transform_children(kt) {
                build_geometry(commands, meshes, materials, child, combined, modules);
            }
        }

        // ── Boolean operations ────────────────────────────────────────────────
        // CSG is not yet implemented; render all children visually so the scene
        // at least makes sense. subtract/intersect will look different from final.
        Statement::BooleanOp(op) => {
            for child in bool_children(op) {
                build_geometry(commands, meshes, materials, child, parent, modules);
            }
        }

        // ── Module instantiation ──────────────────────────────────────────────
        Statement::ModuleUse(mu) => {
            instantiate_module(commands, meshes, materials, mu, parent, modules);
        }

        // Constraints, tolerances, etc. don't produce renderable geometry.
        _ => {}
    }
}

// ── Module instantiation ──────────────────────────────────────────────────────

fn instantiate_module(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    mu: &ModuleUse,
    parent: Transform,
    modules: &HashMap<String, ModuleDefinition>,
) {
    let Some(def) = modules.get(&mu.name) else {
        eprintln!("Warning: module '{}' not defined", mu.name);
        return;
    };

    if mu.arguments.len() != def.parameters.len() {
        eprintln!(
            "Warning: module '{}' expects {} args, got {}",
            mu.name, def.parameters.len(), mu.arguments.len()
        );
    }

    // Substitute parameter identifiers with the provided argument values throughout
    // the module body, then render the resulting statements.
    for body_stmt in &def.statements {
        let resolved = sub_stmt(body_stmt, &def.parameters, &mu.arguments);
        build_geometry(commands, meshes, materials, &resolved, parent, modules);
    }
}

// ── Shape spawning ────────────────────────────────────────────────────────────

fn spawn_shape(
    commands: &mut Commands,
    meshes: &mut ResMut<Assets<Mesh>>,
    materials: &mut ResMut<Assets<StandardMaterial>>,
    ss: &ShapeStatement,
    parent: Transform,
) {
    let Some((mesh_handle, local_t, color, collision_r)) = make_shape(meshes, &ss.shape) else {
        return;
    };

    // Compose: parent transform applied to the shape's own local position.
    let world_t = parent.mul_transform(local_t);

    commands.spawn((
        PbrBundle {
            mesh: mesh_handle,
            material: materials.add(StandardMaterial {
                base_color: color,
                metallic: 0.15,
                perceptual_roughness: 0.65,
                ..default()
            }),
            transform: world_t,
            ..default()
        },
        KrystalObject { name: ss.name.clone(), moveable: true },
        Selectable,
        CollisionRadius(collision_r),
    ));
}

/// Build the mesh + local transform for a single shape.
/// Returns None for unsupported / unimplemented shape kinds.
fn make_shape(
    meshes: &mut ResMut<Assets<Mesh>>,
    shape: &Shape,
) -> Option<(Handle<Mesh>, Transform, Color, f32)> {
    match shape {
        Shape::Cube { x, y, z, size } => {
            let pos  = kpos(x, y, z);
            let s    = ev(size);
            Some((
                meshes.add(Cuboid::new(s, s, s)),
                Transform::from_translation(pos),
                Color::srgb(0.30, 0.52, 0.82),
                s * 0.866,
            ))
        }

        Shape::Sphere { x, y, z, radius } => {
            let pos = kpos(x, y, z);
            let r   = ev(radius);
            Some((
                meshes.add(Sphere::new(r).mesh().ico(16).unwrap()),
                Transform::from_translation(pos),
                Color::srgb(0.82, 0.30, 0.52),
                r,
            ))
        }

        Shape::Cylinder { x, y, z, radius, height } => {
            let pos = kpos(x, y, z);
            let r   = ev(radius);
            let h   = ev(height);
            Some((
                meshes.add(Cylinder::new(r, h)),
                Transform::from_translation(pos),
                Color::srgb(0.35, 0.75, 0.40),
                r.max(h * 0.5),
            ))
        }

        Shape::Cone { x, y, z, bottom_radius, top_radius, height } => {
            let pos = kpos(x, y, z);
            let r1  = ev(bottom_radius);
            let r2  = ev(top_radius);
            let h   = ev(height);
            // Bevy 0.14 doesn't have a built-in cone/truncated-cone primitive.
            // Approximate with a cylinder using the average radius; a true cone
            // mesh is on the roadmap.
            let r_approx = (r1 + r2) * 0.5;
            Some((
                meshes.add(Cylinder::new(r_approx, h)),
                Transform::from_translation(pos),
                Color::srgb(0.82, 0.52, 0.22),
                r1.max(h * 0.5),
            ))
        }

        Shape::Torus { x, y, z, major_radius, minor_radius } => {
            let pos = kpos(x, y, z);
            let r_maj = ev(major_radius);
            let r_min = ev(minor_radius);
            Some((
                meshes.add(Torus::new(r_min, r_maj)),
                Transform::from_translation(pos),
                Color::srgb(0.65, 0.30, 0.82),
                r_maj + r_min,
            ))
        }

        Shape::Prism { x, y, z, radius, height, .. } => {
            // True n-gon prism mesh not yet built; approximate with cylinder.
            let pos = kpos(x, y, z);
            let r   = ev(radius);
            let h   = ev(height);
            Some((
                meshes.add(Cylinder::new(r, h)),
                Transform::from_translation(pos),
                Color::srgb(0.55, 0.55, 0.30),
                r.max(h * 0.5),
            ))
        }

        // 2D shapes are rendered as very flat cylinders (disks) until extrusion
        // is implemented.
        Shape::Rect { x, y, width, height } => {
            let pos = Vec3::new(ev(x), 0.0, ev(y));
            let w   = ev(width);
            let _h  = ev(height);
            Some((
                meshes.add(Cylinder::new(w * 0.5, 0.1)),
                Transform::from_translation(pos),
                Color::srgb(0.70, 0.70, 0.70),
                w * 0.5,
            ))
        }

        Shape::Circle { x, y, radius } => {
            let pos = Vec3::new(ev(x), 0.0, ev(y));
            let r   = ev(radius);
            Some((
                meshes.add(Cylinder::new(r, 0.1)),
                Transform::from_translation(pos),
                Color::srgb(0.70, 0.70, 0.70),
                r,
            ))
        }

        // Not yet rendered (gear, spring, beam, bearing, hole, ellipse, polygon)
        _ => {
            eprintln!("Warning: shape kind not yet rendered, skipping");
            None
        }
    }
}

// ── Transform helpers ─────────────────────────────────────────────────────────

/// Convert a Krystal transform into a Bevy Transform.
/// Coordinate mapping: Krystal Z = world up = Bevy Y; Krystal Y = Bevy Z.
fn krystal_transform_to_bevy(kt: &KTransform) -> Transform {
    match kt {
        KTransform::Translate { x, y, z, .. } => {
            Transform::from_translation(Vec3::new(ev(x), ev(z), ev(y)))
        }
        KTransform::Rotate { angle, ax, ay, az, .. } => {
            let deg = ev(angle);
            // Apply the same Y↔Z swap to the rotation axis.
            let axis = Vec3::new(ev(ax), ev(az), ev(ay)).normalize_or_zero();
            if axis == Vec3::ZERO {
                Transform::IDENTITY
            } else {
                Transform::from_rotation(Quat::from_axis_angle(axis, deg.to_radians()))
            }
        }
        KTransform::Scale { x, y, z, .. } => {
            Transform::from_scale(Vec3::new(ev(x), ev(z), ev(y)))
        }
        KTransform::Mirror { nx, ny, nz, .. } => {
            // Proper mirror requires a non-uniform negative scale along the
            // reflected axis. This is a visual approximation.
            let (kx, ky, kz) = (ev(nx), ev(ny), ev(nz));
            Transform::from_scale(Vec3::new(
                if kx.abs() > 0.5 { -1.0 } else { 1.0 },
                if kz.abs() > 0.5 { -1.0 } else { 1.0 }, // Bevy Y = Krystal Z
                if ky.abs() > 0.5 { -1.0 } else { 1.0 }, // Bevy Z = Krystal Y
            ))
        }
    }
}

fn transform_children(kt: &KTransform) -> &[Statement] {
    match kt {
        KTransform::Translate { statements, .. } => statements,
        KTransform::Rotate    { statements, .. } => statements,
        KTransform::Scale     { statements, .. } => statements,
        KTransform::Mirror    { statements, .. } => statements,
    }
}

fn bool_children(op: &BooleanOperation) -> &[Statement] {
    match op {
        BooleanOperation::Union     { statements } => statements,
        BooleanOperation::Subtract  { statements } => statements,
        BooleanOperation::Intersect { statements } => statements,
    }
}

// ── Parameter substitution ────────────────────────────────────────────────────

fn sub_val(v: &Value, params: &[String], args: &[Value]) -> Value {
    match v {
        Value::Number(n) => Value::Number(*n),
        Value::Identifier(name) => params
            .iter()
            .position(|p| p == name)
            .and_then(|i| args.get(i))
            .cloned()
            .unwrap_or_else(|| Value::Identifier(name.clone())),
        Value::BinaryOp { left, op, right } => Value::BinaryOp {
            left:  Box::new(sub_val(left,  params, args)),
            op:    op.clone(),
            right: Box::new(sub_val(right, params, args)),
        },
    }
}

fn sub_shape(s: &Shape, p: &[String], a: &[Value]) -> Shape {
    match s {
        Shape::Cube     { x, y, z, size }
            => Shape::Cube { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a), size: sv(size,p,a) },
        Shape::Sphere   { x, y, z, radius }
            => Shape::Sphere { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a), radius: sv(radius,p,a) },
        Shape::Cylinder { x, y, z, radius, height }
            => Shape::Cylinder { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a), radius: sv(radius,p,a), height: sv(height,p,a) },
        Shape::Cone     { x, y, z, bottom_radius, top_radius, height }
            => Shape::Cone { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                bottom_radius: sv(bottom_radius,p,a), top_radius: sv(top_radius,p,a), height: sv(height,p,a) },
        Shape::Torus    { x, y, z, major_radius, minor_radius }
            => Shape::Torus { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                major_radius: sv(major_radius,p,a), minor_radius: sv(minor_radius,p,a) },
        Shape::Prism    { x, y, z, radius, sides, height }
            => Shape::Prism { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                radius: sv(radius,p,a), sides: sv(sides,p,a), height: sv(height,p,a) },
        Shape::Hole     { x, y, z, radius, depth }
            => Shape::Hole { x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                radius: sv(radius,p,a), depth: sv(depth,p,a) },
        Shape::Rect     { x, y, width, height }
            => Shape::Rect { x: sv(x,p,a), y: sv(y,p,a), width: sv(width,p,a), height: sv(height,p,a) },
        Shape::Circle   { x, y, radius }
            => Shape::Circle { x: sv(x,p,a), y: sv(y,p,a), radius: sv(radius,p,a) },
        Shape::Ellipse  { x, y, major_radius, minor_radius }
            => Shape::Ellipse { x: sv(x,p,a), y: sv(y,p,a),
                major_radius: sv(major_radius,p,a), minor_radius: sv(minor_radius,p,a) },
        Shape::Polygon  { x, y, radius, sides }
            => Shape::Polygon { x: sv(x,p,a), y: sv(y,p,a),
                radius: sv(radius,p,a), sides: sv(sides,p,a) },
        other => other.clone(),
    }
}

fn sub_stmt(stmt: &Statement, p: &[String], a: &[Value]) -> Statement {
    match stmt {
        Statement::Shape(ss) => Statement::Shape(ShapeStatement {
            shape: sub_shape(&ss.shape, p, a),
            name:  ss.name.clone(),
        }),
        Statement::Transform(kt) => Statement::Transform(match kt {
            KTransform::Translate { x, y, z, statements } => KTransform::Translate {
                x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                statements: statements.iter().map(|s| sub_stmt(s, p, a)).collect(),
            },
            KTransform::Rotate { angle, ax, ay, az, statements } => KTransform::Rotate {
                angle: sv(angle,p,a), ax: sv(ax,p,a), ay: sv(ay,p,a), az: sv(az,p,a),
                statements: statements.iter().map(|s| sub_stmt(s, p, a)).collect(),
            },
            KTransform::Scale { x, y, z, statements } => KTransform::Scale {
                x: sv(x,p,a), y: sv(y,p,a), z: sv(z,p,a),
                statements: statements.iter().map(|s| sub_stmt(s, p, a)).collect(),
            },
            KTransform::Mirror { nx, ny, nz, statements } => KTransform::Mirror {
                nx: sv(nx,p,a), ny: sv(ny,p,a), nz: sv(nz,p,a),
                statements: statements.iter().map(|s| sub_stmt(s, p, a)).collect(),
            },
        }),
        Statement::BooleanOp(op) => Statement::BooleanOp(match op {
            BooleanOperation::Union     { statements } =>
                BooleanOperation::Union     { statements: statements.iter().map(|s| sub_stmt(s,p,a)).collect() },
            BooleanOperation::Subtract  { statements } =>
                BooleanOperation::Subtract  { statements: statements.iter().map(|s| sub_stmt(s,p,a)).collect() },
            BooleanOperation::Intersect { statements } =>
                BooleanOperation::Intersect { statements: statements.iter().map(|s| sub_stmt(s,p,a)).collect() },
        }),
        other => other.clone(),
    }
}

// Short alias used only inside sub_shape for brevity.
#[inline] fn sv(v: &Value, p: &[String], a: &[Value]) -> Value { sub_val(v, p, a) }

// ── Value evaluator ───────────────────────────────────────────────────────────

/// Evaluate a Value expression to a concrete f32.
/// Unresolved identifiers produce 0.0 with a warning (they should be substituted
/// by the module system before reaching this point).
fn ev(value: &Value) -> f32 {
    match value {
        Value::Number(n) => *n as f32,
        Value::Identifier(name) => {
            eprintln!("Warning: unresolved identifier '{}' evaluated to 0.0", name);
            0.0
        }
        Value::BinaryOp { left, op, right } => {
            let l = ev(left);
            let r = ev(right);
            match op {
                BinaryOperator::Add      => l + r,
                BinaryOperator::Subtract => l - r,
                BinaryOperator::Multiply => l * r,
                BinaryOperator::Divide   => if r.abs() > 1e-9 { l / r } else { 0.0 },
            }
        }
    }
}

/// Convert Krystal (x, y, z) — where Z is world-up — to a Bevy Vec3.
/// Bevy uses Y-up, so Krystal Z maps to Bevy Y, and Krystal Y maps to Bevy Z.
#[inline]
fn kpos(x: &Value, y: &Value, z: &Value) -> Vec3 {
    Vec3::new(ev(x), ev(z), ev(y))
}
