import customtkinter as ctk
from tkinter import filedialog
import subprocess
import sys

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CAD Pilot")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")

        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(self, text="C A D _ P I L O T", font=("Orbitron", 48, "bold"), text_color="#00ffff")
        title.grid(row=0, column=0, pady=20, sticky="n")

        # Frame for file list and buttons
        main_frame = ctk.CTkFrame(self, fg_color="black", border_color="#00ffff", border_width=2)
        main_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # File list
        self.file_list = ctk.CTkTextbox(main_frame, fg_color="black", text_color="#00ffff", font=("Share Tech Mono", 14), border_color="#00ffff", border_width=1)
        self.file_list.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="black")
        button_frame.grid(row=2, column=0, pady=20, sticky="s")

        add_button = ctk.CTkButton(button_frame, text="Add File", command=self.add_file, font=("Share Tech Mono", 18), fg_color="black", text_color="#00ffff", border_color="#00ffff", border_width=1, hover_color="#004444")
        add_button.grid(row=0, column=0, padx=10)

        render_gui_button = ctk.CTkButton(button_frame, text="Render with GUI", command=self.render_gui, font=("Share Tech Mono", 18), fg_color="black", text_color="#00ffff", border_color="#00ffff", border_width=1, hover_color="#004444")
        render_gui_button.grid(row=0, column=1, padx=10)

        render_terminal_button = ctk.CTkButton(button_frame, text="Render with Terminal", command=self.render_terminal, font=("Share Tech Mono", 18), fg_color="black", text_color="#00ffff", border_color="#00ffff", border_width=1, hover_color="#004444")
        render_terminal_button.grid(row=0, column=2, padx=10)

    def add_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a CAD Pilot File",
            filetypes=(("CAD Pilot Files", "*.cadp"), ("All files", "*.*"))
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