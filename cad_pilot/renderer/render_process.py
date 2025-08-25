import argparse
from cad_pilot.parser import CadParser
from cad_pilot.transformer import CadTransformer
from cad_pilot.renderer.terminal_renderer import render as terminal_render
from cad_pilot.renderer.lightweight_renderer import LightweightRenderer
from cad_pilot.renderer.gui_renderer import GuiRenderer

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--file", type=str, required=True)
    arg_parser.add_argument("--renderer", choices=["gui", "terminal", "lightweight"], required=True)
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
            renderer = GuiRenderer(scene.objects)
            renderer.render()
        elif args.renderer == "lightweight":
            renderer = LightweightRenderer(scene.objects)
            renderer.render()
        elif args.renderer == "terminal":
            if scene.current_object and hasattr(scene.current_object, 'cq_object'):
                terminal_render(scene.current_object, scene.objects)
            else:
                print("No renderable object found for terminal display.")
    else:
        print("No objects to render.")
