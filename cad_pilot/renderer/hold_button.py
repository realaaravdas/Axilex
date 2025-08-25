import customtkinter as ctk

class HoldButton(ctk.CTkFrame):
    def __init__(self, master, text="Quit", command=None, hold_time=1000, **kwargs):
        super().__init__(master, **kwargs)

        self.command = command
        self.hold_time = hold_time
        self._hold_job = None

        self.button = ctk.CTkButton(self, text=text, **kwargs)
        self.button.grid(row=0, column=0, sticky="nsew")

        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress.set(0)
        self.progress.grid(row=1, column=0, sticky="ew")

        self.button.bind("<ButtonPress-1>", self.on_press)
        self.button.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_hold()

    def on_release(self, event):
        self.cancel_hold()

    def start_hold(self):
        self.progress.set(0)
        self.update_progress(0)

    def update_progress(self, elapsed_time):
        if elapsed_time >= self.hold_time:
            self.progress.set(1)
            if self.command:
                self.command()
        else:
            progress_val = elapsed_time / self.hold_time
            self.progress.set(progress_val)
            self._hold_job = self.after(50, self.update_progress, elapsed_time + 50)

    def cancel_hold(self):
        if self._hold_job:
            self.after_cancel(self._hold_job)
            self._hold_job = None
        self.progress.set(0)
