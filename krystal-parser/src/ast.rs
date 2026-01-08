// Abstract Syntax Tree definitions for Krystal CAD language
// NOTE: This is a partial implementation focused on parsing
// Full geometry evaluation will be implemented in later phases

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Program {
    pub statements: Vec<Statement>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Statement {
    Shape(ShapeStatement),
    Transform(Transform),
    BooleanOp(BooleanOperation),
    ModuleDef(ModuleDefinition),
    ModuleUse(ModuleUse),
    Constraint(Constraint),
    Extrude(Extrude),
    SurfaceOp(SurfaceOperation),
    PlaneSelect(PlaneSelect),
    HolePattern(HolePattern),
    Tolerance(ToleranceSpec),
}

// ============================================================================
// SHAPES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShapeStatement {
    pub shape: Shape,
    pub name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Shape {
    // 2D Shapes
    Rect { x: Value, y: Value, width: Value, height: Value },
    Circle { x: Value, y: Value, radius: Value },
    Ellipse { x: Value, y: Value, major_radius: Value, minor_radius: Value },
    Polygon { x: Value, y: Value, radius: Value, sides: Value },
    
    // 3D Shapes
    Cube { x: Value, y: Value, z: Value, size: Value },
    Sphere { x: Value, y: Value, z: Value, radius: Value },
    Cylinder { x: Value, y: Value, z: Value, radius: Value, height: Value },
    Cone { x: Value, y: Value, z: Value, bottom_radius: Value, top_radius: Value, height: Value },
    Torus { x: Value, y: Value, z: Value, major_radius: Value, minor_radius: Value },
    Prism { x: Value, y: Value, z: Value, radius: Value, sides: Value, height: Value },
    
    // Negative Space
    Hole { x: Value, y: Value, z: Value, radius: Value, depth: Value },
    
    // Specialized Components
    Gear { x: Value, y: Value, z: Value, module: Value, teeth: Value, pressure_angle: Value, height: Value },
    Spring { x: Value, y: Value, z: Value, radius: Value, wire_diameter: Value, coils: Value, pitch: Value },
    Beam { x: Value, y: Value, z: Value, length: Value, width: Value, beam_type: String },
    Bearing { x: Value, y: Value, z: Value, inner_diameter: Value, outer_diameter: Value, width: Value },
}

// ============================================================================
// TRANSFORMATIONS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Transform {
    Translate { x: Value, y: Value, z: Value, statements: Vec<Statement> },
    Rotate { angle: Value, ax: Value, ay: Value, az: Value, statements: Vec<Statement> },
    Scale { x: Value, y: Value, z: Value, statements: Vec<Statement> },
    Mirror { nx: Value, ny: Value, nz: Value, statements: Vec<Statement> },
}

// ============================================================================
// BOOLEAN OPERATIONS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BooleanOperation {
    Union { statements: Vec<Statement> },
    Subtract { statements: Vec<Statement> },
    Intersect { statements: Vec<Statement> },
}

// ============================================================================
// EXTRUSION & SURFACE OPERATIONS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Extrude {
    pub height: Value,
    pub option: Option<ExtrudeOption>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ExtrudeOption {
    Cone,
    Dome,
    Hemisphere,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SurfaceOperation {
    Revolve { axis_x: Value, axis_y: Value, axis_z: Value, angle: Value, statements: Vec<Statement> },
    Sweep { path: PathSpec, statements: Vec<Statement> },
    Loft { statements: Vec<Statement> },
    Shell { thickness: Value },
    Offset { distance: Value },
    Fillet { radius: Value, edge_spec: String },
    Chamfer { distance: Value, edge_spec: String },
    Bevel { distance: Value, angle: Value },
    Thread { diameter: Value, pitch: Value, length: Value, thread_type: String },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum PathSpec {
    Curve { points: Vec<Point> },
    Spline { points: Vec<Point>, spline_type: String },
    Arc { cx: Value, cy: Value, radius: Value, start_angle: Value, end_angle: Value },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Point {
    pub x: Value,
    pub y: Value,
    pub z: Value,
}

// ============================================================================
// WORK PLANES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlaneSelect {
    pub plane_type: String,
    pub statements: Vec<Statement>,
}

// ============================================================================
// HOLE PATTERNS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HolePattern {
    Linear {
        x: Value,
        y: Value,
        z: Value,
        radius: Value,
        depth: Value,
        count: Value,
        spacing: SpacingSpec,
    },
    Circular {
        cx: Value,
        cy: Value,
        cz: Value,
        pattern_radius: Value,
        hole_radius: Value,
        hole_depth: Value,
        count: Value,
    },
    Grid {
        x: Value,
        y: Value,
        z: Value,
        radius: Value,
        depth: Value,
        rows: Value,
        cols: Value,
        spacing: Value,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum SpacingSpec {
    Uniform(Value),
    NonUniform(Vec<Value>),
}

// ============================================================================
// MODULE SYSTEM
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleDefinition {
    pub name: String,
    pub parameters: Vec<String>,
    pub statements: Vec<Statement>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModuleUse {
    pub name: String,
    pub arguments: Vec<Value>,
}

// ============================================================================
// CONSTRAINTS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Constraint {
    AlignX { obj1: String, obj2: String },
    AlignY { obj1: String, obj2: String },
    AlignZ { obj1: String, obj2: String },
    CenterOnX { obj1: String, obj2: String },
    CenterOnY { obj1: String, obj2: String },
    CenterOnZ { obj1: String, obj2: String },
    DistanceX { obj1: String, obj2: String, distance: Value },
    DistanceY { obj1: String, obj2: String, distance: Value },
    DistanceZ { obj1: String, obj2: String, distance: Value },
    Fixed { obj: String },
    Tangent { obj1: String, obj2: String },
    Perpendicular { obj1: String, obj2: String },
    Parallel { obj1: String, obj2: String },
    Angle { obj1: String, obj2: String, angle: Value },
    NoCollision { obj1: String, obj2: String },
    ContainedIn { obj1: String, obj2: String },
}

// ============================================================================
// TOLERANCES
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ToleranceSpec {
    Dimensional { obj: String, plus: Value, minus: Value },
    Geometric { obj: String, tolerance_type: String, value: Value },
    Fit { obj1: String, obj2: String, fit_type: String },
}

// ============================================================================
// VALUE EXPRESSIONS
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Value {
    Number(f64),
    Identifier(String),
    BinaryOp {
        left: Box<Value>,
        op: BinaryOperator,
        right: Box<Value>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BinaryOperator {
    Add,
    Subtract,
    Multiply,
    Divide,
}
