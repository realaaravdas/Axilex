from lark import Lark

cad_grammar = r"""
    ?start: statement+

    statement: shape | transform | boolean_op | module | use | constraint | extrude

    shape: (rect | cube | sphere | cylinder) ["as" CNAME]
    transform: translate | rotate | scale
    boolean_op: union | subtract
    constraint: align_x | align_y | align_z | center_on_x | center_on_y | center_on_z | distance_x | distance_y | distance_z | fixed

    module: "module" CNAME "(" [CNAME ("," CNAME)*] ")" "{" statement+ "}"
    use: "use" CNAME "(" [value ("," value)*] ")"

    rect: "rect" "(" value "," value "," value "," value ")"
    cube: "cube" "(" value "," value "," value "," value ")"
    sphere: "sphere" "(" value "," value "," value "," value ")"
    cylinder: "cylinder" "(" value "," value "," value "," value "," value ")"

    translate: "translate" "(" value "," value "," value ")" "{" statement+ "}"
    rotate: "rotate" "(" value "," value "," value "," value ")" "{" statement+ "}"
    scale: "scale" "(" value "," value "," value ")" "{" statement+ "}"

    union: "union" "{" statement+ "}"
    subtract: "subtract" "{" statement+ "}"

    extrude: "extrude" "(" value ")"

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

    value: term (("+" | "-") term)*
    term: factor (("*" | "/") factor)*
    factor: NUMBER | CNAME | "(" value ")"

    COMMENT: /#.*/

    %import common.CNAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""

class CadParser:
    def __init__(self):
        self.parser = Lark(cad_grammar, start='start')

    def parse(self, code):
        return self.parser.parse(code)
