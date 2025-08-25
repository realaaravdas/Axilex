import customtkinter as ctk
from tkinter import filedialog
import subprocess
import sys

# Color Palette
colors = {
    "deep_space": "#000308",
    "void_black": "#050a0f",
    "dark_matter": "#0a1018",
    "shadow_blue": "#0f1419",
    "stellar_edge": "#141920",
    "ice_white": "#f8fafc",
    "frost_blue": "#e2e8f0",
    "nebula_gray": "#cbd5e1",
    "cosmic_dust": "#94a3b8",
    "plasma_blue": "#00e5ff",
    "quantum_cyan": "#64ffda",
    "neural_blue": "#2196f3",
    "photon_blue": "#03dac6",
    "system_green": "#00ff88",
    "alert_amber": "#ffab00",
    "critical_red": "#ff1744",
    "data_blue": "#00b0ff",
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KRYSTALcad")
        self.geometry("800x600")
        self.configure(fg_color=colors["deep_space"])

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(self, text="KRYSTAL CAD", font=("Orbitron", 56, "bold"), text_color=colors["plasma_blue"])
        title.grid(row=0, column=0, pady=20, sticky="n")

        # Frame for file list and buttons
        main_frame = ctk.CTkFrame(self, fg_color=colors["void_black"], border_color=colors["stellar_edge"], border_width=1)
        main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # File list
        self.file_list = ctk.CTkTextbox(main_frame, fg_color=colors["deep_space"], text_color=colors["ice_white"], font=("JetBrains Mono", 14), border_color=colors["stellar_edge"], border_width=1)
        self.file_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color=colors["deep_space"])
        button_frame.grid(row=2, column=0, pady=20, sticky="s")

        add_button = ctk.CTkButton(button_frame, text="Add File", command=self.add_file, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        add_button.grid(row=0, column=0, padx=10)

        render_gui_button = ctk.CTkButton(button_frame, text="Render with GUI", command=self.render_gui, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
        render_gui_button.grid(row=0, column=1, padx=10)

        render_terminal_button = ctk.CTkButton(button_frame, text="Render with Terminal", command=self.render_terminal, font=("Inter", 16, "bold"), fg_color="#0f1419", text_color="#00e5ff", border_color="#00e5ff", border_width=1, hover_color="#141920")
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
        selected_.file = self.file_list.get("1.0", "end-1c").strip().split("\n")[-1]
        if selected_file:
            subprocess.Popen([sys.executable, "-m", "cad_pilot.renderer.render_process", "--file", selected_file, "--renderer", "terminal"])

if __name__ == "__main__":
    app = App()
    app.mainloop()

