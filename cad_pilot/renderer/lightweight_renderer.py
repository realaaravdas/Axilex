import pyvista as pv
from .ui.colors import colors

class LightweightRenderer:
    def __init__(self, objects):
        self.plotter = pv.Plotter(window_size=[1024, 768], title="KRYSTALcad - Lightweight Render")
        self.objects = objects
        self.is_wireframe = True

    def render(self):
        if not self.objects:
            print("No objects to render.")
            return

        self.plotter.add_axes()
        self.plotter.add_checkbox_button_widget(self.toggle_mode, value=self.is_wireframe)

        self.render_objects()
        self.plotter.show()

    def render_objects(self):
        self.plotter.clear_actors()
        for obj in self.objects:
            if hasattr(obj, 'to_pyvista_mesh'):
                mesh = obj.to_pyvista_mesh()
                if mesh:
                    if self.is_wireframe:
                        self.plotter.add_mesh(mesh, style='wireframe', color=colors["plasma_blue"], line_width=2)
                    else:
                        self.plotter.add_mesh(mesh, style='surface', color=colors["photon_blue"], smooth_shading=True)

    def toggle_mode(self, value):
        self.is_wireframe = value
        self.render_objects()
