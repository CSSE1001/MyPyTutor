import tkinter as tk
from tkinter import ttk


class Dialog(tk.Toplevel):
    def __init__(self, parent, title, allow_cancel=False):
        super().__init__(parent)
        parent = parent if parent is not None else self.master  # default to tk
        self.parent = parent

        self.configure(borderwidth=5)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 30,
                                  parent.winfo_rooty() + 30))
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.title(title)
        self.transient(parent)

        self.create_buttons(allow_cancel=allow_cancel)
        self.create_widgets()

        self.grab_set()
        self.button_ok.focus_set()

        callback = self.cancel if allow_cancel else self.ok
        self.protocol("WM_DELETE_WINDOW", callback)
        self.bind('<Escape>', callback)
        self.bind('<Return>', self.ok)  # Return is always ok

        self.wait_window()

    def create_widgets(self):
        pass  # override in subclasses

    def create_buttons(self, allow_cancel=False):
        # for subclasses to create widgets in
        self.frame_top = ttk.Frame(self)
        self.frame_top.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        # buttons
        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(side=tk.TOP)

        self.button_ok = ttk.Button(
            frame_buttons,
            text='OK',
            command=self.ok,
        )
        self.button_ok.pack(side=tk.LEFT, expand=1)

        if allow_cancel:
            self.button_cancel = ttk.Button(
                frame_buttons,
                text='Cancel',
                command=self.cancel,
            )
            self.button_cancel.pack(side=tk.LEFT, expand=1)

    def ok(self, event=None):
        self.destroy()

    def cancel(self, event=None):
        self.destroy()
