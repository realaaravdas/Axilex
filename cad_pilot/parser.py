from lark import Lark

cad_grammar = r"""
    ?start: statement+

    statement: shape | transform | boolean_op | module | use

    shape: rect | cube | sphere | cylinder
    transform: translate | rotate | scale
    boolean_op: union | subtract

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

    value: NUMBER | CNAME

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
