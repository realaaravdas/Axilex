import pyvista as pv

def render(objects):
    plotter = pv.Plotter()
    for obj in objects:
        if hasattr(obj, 'to_pyvista_mesh'):
            mesh = obj.to_pyvista_mesh()
            if mesh:
                plotter.add_mesh(mesh)
    plotter.show()