# Krystal CAD Language Specification (Minimal)
**File Extension:** `.krystal`
**Purpose:** CAD modeling DSL for 3D geometry

## Syntax
```
# Comment
```

## Shapes
**2D:** `rect(x,y,w,h)` `circle(x,y,r)` `ellipse(x,y,rmaj,rmin)` `polygon(x,y,r,sides)`
**3D:** `cube(x,y,z,sz)` `sphere(x,y,z,r)` `cylinder(x,y,z,r,h)` `cone(x,y,z,r1,r2,h)` `torus(x,y,z,rmaj,rmin)` `prism(x,y,z,r,sides,h)`
**Components:** `gear(x,y,z,mod,teeth,angle,h)` `spring(x,y,z,r,wd,coils,pitch)` `beam(x,y,z,len,w,type)` `bearing(x,y,z,id,od,w)` `hole(x,y,z,r,d)`

## Transforms
```
translate(x,y,z) { ... }
rotate(angle,ax,ay,az) { ... }
scale(x,y,z) { ... }
mirror(nx,ny,nz) { ... }
```

## Boolean Ops
```
union { ... }
subtract { ... }
intersect { ... }
```

## Extrusion
```
rect(...)
extrude(h) [cone|dome|hemisphere]
```

## Surface Ops
`revolve(ax,ay,az,angle){...}` `sweep(path){...}` `loft{...}` `shell(t)` `offset(d)` `fillet(r,edges)` `chamfer(d,edges)` `bevel(d,angle)` `thread(d,pitch,len,type)`

## Paths
`curve(pts)` `spline(pts,type)` `arc(cx,cy,r,start,end)`

## Planes
```
plane("XY"|"XZ"|"YZ"|custom) { ... }
```

## Hole Patterns
`linear_holes(x,y,z,r,d,cnt,spacing)` `circular_holes(cx,cy,cz,pr,hr,hd,cnt)` `grid_holes(x,y,z,r,d,rows,cols,sp)`

## Modules
```
module name(p1,p2) { ... }
use name(v1,v2)
```

## Constraints
**Align:** `align_x(o1,o2)` `align_y(o1,o2)` `align_z(o1,o2)`
**Center:** `center_on_x(o1,o2)` `center_on_y(o1,o2)` `center_on_z(o1,o2)`
**Distance:** `distance_x(o1,o2,v)` `distance_y(o1,o2,v)` `distance_z(o1,o2,v)`
**Geometric:** `tangent(o1,o2)` `perpendicular(o1,o2)` `parallel(o1,o2)` `angle(o1,o2,v)`
**Validation:** `no_collision(o1,o2)` `contained_in(o1,o2)` `fixed(o)`

## Tolerances
`tolerance(o,plus,minus)` `geometric_tolerance(o,type,v)` `fit(o1,o2,type)`

## Naming
```
shape(...) as name
```

## Values
Numbers, identifiers, expressions: `+` `-` `*` `/` `()`

## Example
```krystal
# Simple box with hole
cube(0,0,0,20) as box1
subtract {
    use box1
    cylinder(10,10,0,5,20)
}

module bracket(w,h,t) {
    cube(0,0,0,w)
    translate(0,0,h) { cube(0,0,0,t) }
}

use bracket(15,10,3)
```

## Simplifier Markers
Protect code from auto-formatting:
```
# @noformat
<code to protect>
# @noformat_end
```
