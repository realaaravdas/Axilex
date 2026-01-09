use bevy::prelude::*;
use crate::geometry::*;

#[derive(Component, Clone)]
pub struct Constraint {
    pub constraint_type: ConstraintType,
}

#[derive(Clone)]
pub enum ConstraintType {
    DistanceX { target: Entity, distance: f32 },
    DistanceY { target: Entity, distance: f32 },
    DistanceZ { target: Entity, distance: f32 },
    AlignX { target: Entity },
    AlignY { target: Entity },
    AlignZ { target: Entity },
    Fixed,
}

#[derive(Component)]
pub struct CollisionRadius(pub f32);

/// Apply constraints to objects
pub fn apply_constraints(
    mut object_query: Query<(Entity, &mut Transform, &Constraint)>,
    transform_query: Query<&Transform, Without<Constraint>>,
) {
    for (_entity, mut transform, constraint) in object_query.iter_mut() {
        match &constraint.constraint_type {
            ConstraintType::Fixed => {
                // Do nothing - object is fixed
            }
            ConstraintType::DistanceX { target, distance } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.x = target_transform.translation.x + distance;
                }
            }
            ConstraintType::DistanceY { target, distance } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.y = target_transform.translation.y + distance;
                }
            }
            ConstraintType::DistanceZ { target, distance } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.z = target_transform.translation.z + distance;
                }
            }
            ConstraintType::AlignX { target } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.x = target_transform.translation.x;
                }
            }
            ConstraintType::AlignY { target } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.y = target_transform.translation.y;
                }
            }
            ConstraintType::AlignZ { target } => {
                if let Ok(target_transform) = transform_query.get(*target) {
                    transform.translation.z = target_transform.translation.z;
                }
            }
        }
    }
}

/// Simple sphere-based collision detection
pub fn check_collisions(
    mut object_query: Query<(Entity, &mut Transform, &CollisionRadius, &KrystalObject)>,
) {
    let objects: Vec<_> = object_query
        .iter()
        .map(|(e, t, r, _)| (e, t.translation, r.0))
        .collect();

    for (entity1, mut transform1, radius1, obj1) in object_query.iter_mut() {
        if !obj1.moveable {
            continue;
        }

        for &(entity2, pos2, radius2) in &objects {
            if entity1 == entity2 {
                continue;
            }

            let distance = transform1.translation.distance(pos2);
            let min_distance = radius1.0 + radius2;

            if distance < min_distance && distance > 0.0 {
                // Push object away from collision
                let direction = (transform1.translation - pos2).normalize_or_zero();
                let push_amount = min_distance - distance;
                transform1.translation += direction * push_amount * 0.5;
            }
        }
    }
}
