import customtkinter as ctk
from tkinter import filedialog
import subprocess
import sys

# Color Palette
colors = {
    "primary_bg": "#0a0e1a",
    "secondary_bg": "#111827",
    "panel_bg": "#1e293b",
    "accent_bg": "#0f172a",
    "primary_text": "#e2e8f0",
    "secondary_text": "#cbd5e1",
    "accent_text": "#94a3b8",
    "bright_cyan": "#00d9ff",
    "ice_blue": "#7dd3fc",
    "electric_blue": "#3b82f6",
    "neon_blue": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#06b6d4",
    "subtle_border": "#334155",
    "active_border": "#475569",
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KRYSTALcad")
        self.geometry("800x600")
        self.configure(fg_color=colors["primary_bg"])

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(self, text="KRYSTAL CAD", font=("Orbitron", 48, "bold"), text_color=colors["bright_cyan"])
        title.grid(row=0, column=0, pady=20, sticky="n")

        # Frame for file list and buttons
        main_frame = ctk.CTkFrame(self, fg_color=colors["panel_bg"], border_color=colors["active_border"], border_width=2)
        main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # File list
        self.file_list = ctk.CTkTextbox(main_frame, fg_color=colors["secondary_bg"], text_color=colors["primary_text"], font=("JetBrains Mono", 14), border_color=colors["subtle_border"], border_width=1)
        self.file_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color=colors["primary_bg"])
        button_frame.grid(row=2, column=0, pady=20, sticky="s")

        add_button = ctk.CTkButton(button_frame, text="Add File", command=self.add_file, font=("Inter", 18, "bold"), fg_color=colors["electric_blue"], text_color=colors["primary_text"], border_color=colors["active_border"], border_width=1, hover_color=colors["neon_blue"])
        add_button.grid(row=0, column=0, padx=10)

        render_gui_button = ctk.CTkButton(button_frame, text="Render with GUI", command=self.render_gui, font=("Inter", 18, "bold"), fg_color=colors["electric_blue"], text_color=colors["primary_text"], border_color=colors["active_border"], border_width=1, hover_color=colors["neon_blue"])
        render_gui_button.grid(row=0, column=1, padx=10)

        render_terminal_button = ctk.CTkButton(button_frame, text="Render with Terminal", command=self.render_terminal, font=("Inter", 18, "bold"), fg_color=colors["electric_blue"], text_color=colors["primary_text"], border_color=colors["active_border"], border_width=1, hover_color=colors["neon_blue"])
        render_terminal_button.grid(row=0, column=2, padx=10)

    def add_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a KRYSTALcad File",
            filetypes=(("KRYSTALcad Files", "*.cadp"), ("All files", "*.*"))
        )
        if filepath:
            self.file_list.insert("end", filepath + "\n")

    def render_gui(self):
        selected_file = self.file_list.get("1.0", "end-1c").strip().split("\n")[-1]
        if selected_file:
            subprocess.Popen([sys.executable, "-m", "cad_pilot.renderer.render_process", "--file", selected_file, "--renderer", "gui"])

    def render_terminal(self):
        selected_file = self.file_list.get("1.0", "end-1c").strip().split("\n")[-1]
        if selected_file:
            subprocess.Popen([sys.executable, "-m", "cad_pilot.renderer.render_process", "--file", selected_file, "--renderer", "terminal"])

if __name__ == "__main__":
    app = App()
    app.mainloop()

