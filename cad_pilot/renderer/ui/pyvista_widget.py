import customtkinter as ctk
import pyvista as pv
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

class PyVistaWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a PyVista plotter
        self.plotter = pv.Plotter(off_screen=True) # Render off-screen initially

        # Create a VTK Tkinter interactor
        self.interactor = vtkTkRenderWindowInteractor(self, rw=self.plotter.render_window)
        self.interactor.grid(row=0, column=0, sticky="nsew")

        # Set the interactor for the plotter
        self.plotter.interactor = self.interactor

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)

    def clear_actors(self):
        self.plotter.clear_actors()

    def reset_camera(self):
        self.plotter.reset_camera()

    def render(self):
        self.plotter.render()
