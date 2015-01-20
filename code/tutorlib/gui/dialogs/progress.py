import tkinter as tk
from tkinter import ttk


class ProgressPopup(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)

        ttk.Label(
            self, text='Working...',
        ).pack(side=tk.TOP, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(
            side=tk.TOP, padx=10, pady=(0, 10), expand=tk.TRUE, fill=tk.X,
        )
        self.progress_bar.start()