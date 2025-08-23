import argparse
import pyvista as pv
from cad_pilot.parser import CadParser
from cad_pilot.transformer import CadTransformer
from cad_pilot.renderer.terminal_renderer import render as terminal_render

def gui_render(objects):
    plotter = pv.Plotter()
    for obj in objects:
        if hasattr(obj, 'to_pyvista_mesh'):
            mesh = obj.to_pyvista_mesh()
            if mesh:
                plotter.add_mesh(mesh)
    plotter.show()

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--file", type=str, required=True)
    arg_parser.add_argument("--renderer", choices=["gui", "terminal"], required=True)
    args = arg_parser.parse_args()

    parser = CadParser()
    transformer = CadTransformer()

    try:
        with open(args.file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        exit(1)
    
    tree = parser.parse(code)
    scene = transformer.transform(tree)

    if scene and scene.objects:
        if args.renderer == "gui":
            gui_render(scene.objects)
        elif args.renderer == "terminal":
            if scene.current_object and hasattr(scene.current_object, 'cq_object'):
                terminal_render(scene.current_object, scene.objects)
            else:
                print("No renderable object found for terminal display.")
    else:
        print("No objects to render.")
