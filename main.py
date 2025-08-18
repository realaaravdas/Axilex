from cad_pilot.parser import CadParser
from cad_pilot.transformer import CadTransformer
from cad_pilot.renderer.terminal_renderer import render as terminal_render
from cad_pilot.renderer.gui_renderer import render as gui_render
from cad_pilot.exporter import export_to_stl, export_to_step
import argparse

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="CadPilot Compiler and Renderer")
    arg_parser.add_argument("--renderer", choices=["gui", "terminal"], default="gui",
                            help="Choose rendering method: 'gui' for interactive 3D view, 'terminal' for ASCII wireframe.")
    arg_parser.add_argument("--file", type=str, default="examples/advanced_example.cadp",
                            help="Path to the .cadp file to compile and render.")
    arg_parser.add_argument("--export-stl", type=str, help="Export the generated model to an STL file at the specified path.")
    arg_parser.add_argument("--export-step", type=str, help="Export the generated model to a STEP file at the specified path.")
    args = arg_parser.parse_args()

    parser = CadParser()
    try:
        with open(args.file, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {args.file}")
        exit(1)
    
    tree = parser.parse(code)
    transformer = CadTransformer()
    scene = transformer.transform(tree)

    if scene and scene.objects:
        if args.export_stl:
            export_to_stl(scene.objects, args.export_stl)
        
        if args.export_step:
            export_to_step(scene.objects, args.export_step)

        if args.renderer == "gui":
            gui_render(scene.objects)
        elif args.renderer == "terminal":
            if scene.current_object and hasattr(scene.current_object, 'cq_object'):
                terminal_render(scene.current_object, scene.objects)
            else:
                print("No renderable object found for terminal display.")
    else:
        print("No objects to render.")