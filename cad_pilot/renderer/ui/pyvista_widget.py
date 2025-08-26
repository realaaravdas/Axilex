import customtkinter as ctk
import pyvista as pv
from PIL import Image, ImageTk

class PyVistaWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.plotter = pv.Plotter(off_screen=True)
        self.image_label = ctk.CTkLabel(self, text="")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self._last_mouse_x = 0
        self._last_mouse_y = 0
        self._is_dragging = False

        self.image_label.bind("<ButtonPress-1>", self._on_mouse_press)
        self.image_label.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.image_label.bind("<B1-Motion>", self._on_mouse_drag)
        self.image_label.bind("<MouseWheel>", self._on_mouse_scroll)

        # Initial render
        self._update_display()

    def _on_mouse_press(self, event):
        self._last_mouse_x = event.x
        self._last_mouse_y = event.y
        self._is_dragging = True

    def _on_mouse_release(self, event):
        self._is_dragging = False

    def _on_mouse_drag(self, event):
        if self._is_dragging:
            dx = event.x - self._last_mouse_x
            dy = event.y - self._last_mouse_y

            # Simple camera rotation (adjust sensitivity as needed)
            self.plotter.camera.azimuth += dx * 0.5
            self.plotter.camera.elevation -= dy * 0.5
            self.plotter.camera_position = self.plotter.camera.GetPosition()

            self._last_mouse_x = event.x
            self._last_mouse_y = event.y
            self._update_display()

    def _on_mouse_scroll(self, event):
        # Zoom in/out based on scroll direction
        if event.delta > 0:
            self.plotter.camera.zoom(1.1) # Zoom in
        else:
            self.plotter.camera.zoom(0.9) # Zoom out
        self._update_display()

    def _update_display(self):
        # Render the PyVista scene to an image
        img_array = self.plotter.screenshot(return_img=True)
        img = Image.fromarray(img_array)

        # Resize image to fit the label (optional, but good for performance)
        # Get current size of the label to resize the image to
        label_width = self.image_label.winfo_width()
        label_height = self.image_label.winfo_height()

        if label_width > 0 and label_height > 0:
            img = img.resize((label_width, label_height), Image.LANCZOS)

        # Convert to CTkImage and update the label
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
        self.image_label.configure(image=ctk_img)
        self.image_label.image = ctk_img # Keep a reference!

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)
        self._update_display()

    def clear_actors(self):
        self.plotter.clear_actors()
        self._update_display()

    def reset_camera(self):
        self.plotter.reset_camera()
        self._update_display()

    def render(self):
        # In this setup, render is implicitly called by _update_display
        self._update_display()
