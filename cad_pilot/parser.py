from lark import Lark

cad_grammar = r"""
    ?start: statement+

    statement: shape | transform | boolean_op | module | use | constraint | extrude | surface_op | plane_select | hole_pattern | tolerance_spec

    shape: (rect | circle | ellipse | polygon | cube | sphere | cylinder | cone | torus | prism | gear | spring | beam | bearing | hole) ["as" CNAME]

    // Basic 2D Shapes
    rect: "rect" "(" value "," value "," value "," value ")"
    circle: "circle" "(" value "," value "," value ")"
    ellipse: "ellipse" "(" value "," value "," value "," value ")"
    polygon: "polygon" "(" value "," value "," value "," value ")"  // x, y, radius, sides
    
    // Basic 3D Shapes
    cube: "cube" "(" value "," value "," value "," value ")"
    sphere: "sphere" "(" value "," value "," value "," value ")"
    cylinder: "cylinder" "(" value "," value "," value "," value "," value ")"
    cone: "cone" "(" value "," value "," value "," value "," value "," value ")"
    torus: "torus" "(" value "," value "," value "," value "," value ")"  // x, y, z, major_radius, minor_radius
    prism: "prism" "(" value "," value "," value "," value "," value "," value ")"  // x, y, z, radius, sides, height
    
    // Negative Space / Holes
    hole: "hole" "(" value "," value "," value "," value "," value ")"  // x, y, z, radius, depth
    
    // Specialized Components
    gear: "gear" "(" value "," value "," value "," value "," value "," value "," value ")"  // x, y, z, module, teeth, pressure_angle, height
    spring: "spring" "(" value "," value "," value "," value "," value "," value "," value ")"  // x, y, z, radius, wire_diameter, coils, pitch
    beam: "beam" "(" value "," value "," value "," value "," value "," BEAM_TYPE ")"  // x, y, z, length, width, type
    bearing: "bearing" "(" value "," value "," value "," value "," value "," value ")"  // x, y, z, inner_diameter, outer_diameter, width
    
    BEAM_TYPE: "\"i\"" | "\"t\"" | "\"l\"" | "\"c\"" | "\"box\""
    
    // Transformations
    transform: translate | rotate | scale | mirror

    translate: "translate" "(" value "," value "," value ")" "{" statement+ "}"
    rotate: "rotate" "(" value "," value "," value "," value ")" "{" statement+ "}"
    scale: "scale" "(" value "," value "," value ")" "{" statement+ "}"
    mirror: "mirror" "(" value "," value "," value ")" "{" statement+ "}"

    // Boolean Operations
    boolean_op: union | subtract | intersect
    
    union: "union" "{" statement+ "}"
    subtract: "subtract" "{" statement+ "}"
    intersect: "intersect" "{" statement+ "}"

    // Extrusion and Surface Operations
    extrude: "extrude" "(" value ")" [extrude_option]
    extrude_option: "cone" | "dome" | "hemisphere"
    
    surface_op: revolve | sweep | loft | shell | offset | fillet | chamfer | bevel | thread
    
    revolve: "revolve" "(" value "," value "," value "," value ")" "{" statement+ "}"  // axis_x, axis_y, axis_z, angle
    sweep: "sweep" "(" path_spec ")" "{" statement+ "}"
    loft: "loft" "{" statement+ "}"  // Loft between multiple profiles
    shell: "shell" "(" value ")"  // thickness
    offset: "offset" "(" value ")"  // offset distance
    fillet: "fillet" "(" value "," edge_spec ")"  // radius, edge selection
    chamfer: "chamfer" "(" value "," edge_spec ")"  // distance, edge selection
    bevel: "bevel" "(" value "," value ")"  // distance, angle
    thread: "thread" "(" value "," value "," value "," THREAD_TYPE ")"  // diameter, pitch, length, type
    
    THREAD_TYPE: "\"metric\"" | "\"imperial\"" | "\"acme\"" | "\"buttress\""
    
    path_spec: curve | spline | arc
    edge_spec: "edges" "(" STRING ")"  // Edge selection string
    
    // Curves and Paths
    curve: "curve" "(" point_list ")"
    spline: "spline" "(" point_list "," SPLINE_TYPE ")"
    arc: "arc" "(" value "," value "," value "," value "," value ")"  // cx, cy, radius, start_angle, end_angle
    
    SPLINE_TYPE: "\"interpolate\"" | "\"approximate\"" | "\"bezier\""
    
    point_list: point ("," point)*
    point: "(" value "," value "," value ")"

    // Work Planes
    plane_select: "plane" "(" plane_type ")" "{" statement+ "}"
    plane_type: "\"XY\"" | "\"XZ\"" | "\"YZ\"" | custom_plane
    custom_plane: "\"custom\"" "(" value "," value "," value "," value "," value "," value ")"
    
    // Hole Patterns
    hole_pattern: linear_holes | circular_holes | grid_holes
    
    linear_holes: "linear_holes" "(" value "," value "," value "," value "," value "," value "," spacing_spec ")"  // x, y, z, radius, depth, count, spacing
    circular_holes: "circular_holes" "(" value "," value "," value "," value "," value "," value "," value ")"  // cx, cy, cz, pattern_radius, hole_radius, hole_depth, count
    grid_holes: "grid_holes" "(" value "," value "," value "," value "," value "," value "," value "," value ")"  // x, y, z, radius, depth, rows, cols, spacing
    
    spacing_spec: uniform_spacing | non_uniform_spacing
    uniform_spacing: "uniform" "(" value ")"
    non_uniform_spacing: "non_uniform" "(" value_list ")"
    
    value_list: value ("," value)*

    // Module System
    module: "module" CNAME "(" [CNAME ("," CNAME)*] ")" "{" statement+ "}"
    use: "use" CNAME "(" [value ("," value)*] ")"

    // Enhanced Constraints
    constraint: align_x | align_y | align_z | center_on_x | center_on_y | center_on_z 
              | distance_x | distance_y | distance_z | fixed | tangent | perpendicular 
              | parallel | angle_constraint | no_collision | contained_in

    align_x: "align_x" "(" CNAME "," CNAME ")"
    align_y: "align_y" "(" CNAME "," CNAME ")"
    align_z: "align_z" "(" CNAME "," CNAME ")"

    center_on_x: "center_on_x" "(" CNAME "," CNAME ")"
    center_on_y: "center_on_y" "(" CNAME "," CNAME ")"
    center_on_z: "center_on_z" "(" CNAME "," CNAME ")"

    distance_x: "distance_x" "(" CNAME "," CNAME "," value ")"
    distance_y: "distance_y" "(" CNAME "," CNAME "," value ")"
    distance_z: "distance_z" "(" CNAME "," CNAME "," value ")"

    fixed: "fixed" "(" CNAME ")"
    
    tangent: "tangent" "(" CNAME "," CNAME ")"
    perpendicular: "perpendicular" "(" CNAME "," CNAME ")"
    parallel: "parallel" "(" CNAME "," CNAME ")"
    angle_constraint: "angle" "(" CNAME "," CNAME "," value ")"
    no_collision: "no_collision" "(" CNAME "," CNAME ")"
    contained_in: "contained_in" "(" CNAME "," CNAME ")"

    // Tolerances
    tolerance_spec: dimensional_tolerance | geometric_tolerance | fit_tolerance
    
    dimensional_tolerance: "tolerance" "(" CNAME "," value "," value ")"  // object, plus, minus
    geometric_tolerance: "geometric_tolerance" "(" CNAME "," TOLERANCE_TYPE "," value ")"
    fit_tolerance: "fit" "(" CNAME "," CNAME "," FIT_TYPE ")"
    
    TOLERANCE_TYPE: "\"flatness\"" | "\"straightness\"" | "\"circularity\"" | "\"cylindricity\"" 
                  | "\"perpendicularity\"" | "\"parallelism\"" | "\"angularity\"" 
                  | "\"position\"" | "\"concentricity\"" | "\"symmetry\"" | "\"runout\""
    
    FIT_TYPE: "\"clearance\"" | "\"transition\"" | "\"interference\""

    // Value Expressions
    value: term (("+" | "-") term)*
    term: factor (("*" | "/") factor)*
    factor: NUMBER | CNAME | "(" value ")"

    COMMENT: /#.*/

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %import common.ESCAPED_STRING -> STRING
    %ignore WS
    %ignore COMMENT
"""

class CadParser:
    def __init__(self):
        self.parser = Lark(cad_grammar, start='start')

    def parse(self, code):
        return self.parser.parse(code)
