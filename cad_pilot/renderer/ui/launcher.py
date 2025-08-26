import customtkinter as ctk
from tkinter import filedialog
import sys
from .hold_button import HoldButton
from .colors import colors
from cad_pilot.parser import CadParser
from cad_pilot.transformer import CadTransformer
from cad_pilot import exporter
from .pyvista_widget import PyVistaWidget

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KRYSTALcad")
        self.geometry("1200x600")
        self.configure(fg_color=colors["deep_space"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_launcher_frame()
        self.create_render_frame()

        self.show_launcher_frame()

    def create_launcher_frame(self):
        self.launcher_frame = ctk.CTkFrame(self, fg_color=colors["deep_space"])
        self.launcher_frame.grid(row=0, column=0, sticky="nsew")
        self.launcher_frame.grid_columnconfigure(0, weight=1)
        self.launcher_frame.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(self.launcher_frame, text="KRYSTAL CAD", font=("Orbitron", 56, "bold"), text_color=colors["plasma_blue"])
        title.grid(row=0, column=0, pady=20, sticky="n")

        # Frame for file list and buttons
        main_frame = ctk.CTkFrame(self.launcher_frame, fg_color=colors["void_black"], border_color=colors["stellar_edge"], border_width=1)
        main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # File list
        self.file_list = ctk.CTkTextbox(main_frame, fg_color=colors["deep_space"], text_color=colors["ice_white"], font=("JetBrains Mono", 14), border_color=colors["stellar_edge"], border_width=1)
        self.file_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Buttons
        button_frame = ctk.CTkFrame(self.launcher_frame, fg_color=colors["deep_space"])
        button_frame.grid(row=2, column=0, pady=20, sticky="s")

        add_button = ctk.CTkButton(button_frame, text="Add File", command=self.add_file, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        add_button.grid(row=0, column=0, padx=10)

        render_gui_button = ctk.CTkButton(button_frame, text="Render with GUI", command=lambda: self.render_model("gui"), font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        render_gui_button.grid(row=0, column=1, padx=10)

        render_lightweight_button = ctk.CTkButton(button_frame, text="Lightweight Render", command=lambda: self.render_model("lightweight"), font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        render_lightweight_button.grid(row=0, column=2, padx=10)

        export_dxf_button = ctk.CTkButton(button_frame, text="Export to DXF", command=self.export_dxf, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        export_dxf_button.grid(row=0, column=3, padx=10)

        quit_button = HoldButton(button_frame, text="Quit", command=self.quit, hold_time=1000, fg_color="#0f1419", text_color="#ff1744", border_color="#ff1744", border_width=1, hover_color="#141920")
        quit_button.grid(row=0, column=4, padx=10)

    def create_render_frame(self):
        self.render_frame = ctk.CTkFrame(self, fg_color=colors["deep_space"])
        self.render_frame.grid_columnconfigure(0, weight=1)
        self.render_frame.grid_rowconfigure(0, weight=1)

        self.pyvista_widget = PyVistaWidget(self.render_frame, fg_color=colors["deep_space"])
        self.pyvista_widget.grid(row=0, column=0, sticky="nsew")

        back_button = ctk.CTkButton(self.render_frame, text="Back to Launcher", command=self.show_launcher_frame, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        back_button.grid(row=1, column=0, pady=10)

    def show_launcher_frame(self):
        self.render_frame.grid_forget()
        self.launcher_frame.grid(row=0, column=0, sticky="nsew")

    def show_render_frame(self):
        self.launcher_frame.grid_forget()
        self.render_frame.grid(row=0, column=0, sticky="nsew")

    def add_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a KRYSTALcad File",
            filetypes=(("KRYSTALcad Files", "*.cadp"), ("All files", "*.*"))
        )
        if filepath:
            self.file_list.insert("end", filepath + "\n")

    def render_model(self, render_mode):
        selected_file = self.file_list.get("1.0", "end-1c").strip().split("\n")[-1]
        if selected_file:
            parser = CadParser()
            transformer = CadTransformer()
            try:
                with open(selected_file, "r") as f:
                    code = f.read()
            except FileNotFoundError:
                print(f"Error: File not found at {selected_file}")
                return
            
            tree = parser.parse(code)
            scene = transformer.transform(tree)

            if scene and scene.objects:
                self.show_render_frame()
                self.pyvista_widget.clear_actors()
                for obj in scene.objects:
                    if hasattr(obj, 'to_pyvista_mesh'):
                        mesh = obj.to_pyvista_mesh()
                        if mesh:
                            if render_mode == "lightweight":
                                self.pyvista_widget.add_mesh(mesh, style='wireframe', color=colors["plasma_blue"], line_width=2)
                            else:
                                self.pyvista_widget.add_mesh(mesh, style='surface', color=colors["photon_blue"], smooth_shading=True)
                self.pyvista_widget.reset_camera()
                self.pyvista_widget.render()
            else:
                print("No objects to render.")

    def export_dxf(self):
        selected_file = self.file_list.get("1.0", "end-1c").strip().split("\n")[-1]
        if selected_file:
            parser = CadParser()
            transformer = CadTransformer()
            try:
                with open(selected_file, "r") as f:
                    code = f.read()
            except FileNotFoundError:
                print(f"Error: File not found at {selected_file}")
                return
            
            tree = parser.parse(code)
            scene = transformer.transform(tree)

            if scene and scene.objects:
                output_path = filedialog.asksaveasfilename(
                    defaultextension=".dxf",
                    filetypes=(("DXF files", "*.dxf"), ("All files", "*.*"))
                )
                if output_path:
                    exporter.export_to_dxf(scene.objects, output_path)
            else:
                print("No objects to export.")

if __name__ == "__main__":
    app = App()
    app.mainloop()



